using System.Collections.Generic;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using UnityEngine.InputSystem;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// Prompt 30 L3 and L5 in a battle: the match end (sheet "Kết trận") and the endless part's choice.
    /// <para>
    /// When the session's outcome comes, the world is resolved (<see cref="SimWorld.IsOver"/>: the Sim's RUNNING -> RESOLVED,
    /// the result, rewards, stars and score fixed) and from then the runner steps nothing of the battle. The presentation
    /// (<see cref="MatchEnd.BeginPresentation"/>) is pictures only: the card tray and command buttons hide (the boss bar and the
    /// notices stay), the camera goes to the last target in the first 1.5 s, a boss's part-by-part death chain plays (0.4 s
    /// apart, then the hull), and for a big or first win the pictures slow to x0.3 from 1.5 s. The slow motion is Unity's
    /// time scale, which with no Sim step left only reaches what is drawn (particles, wrecks burning, aircraft falling): the
    /// view's clock, never the Sim's time. The presentation's own clock is <see cref="MatchEnd.Advance"/> with unscaled seconds,
    /// so slow motion never stretches it. A tap skips it after 0.75 s; a story line it cut (on show or waiting) is shown on
    /// the results panel and goes to the dialogue log. A loss: the camera to our HQ or the last vehicle lost, one blast,
    /// the general's line, no slow motion.
    /// </para>
    /// <para>
    /// L5: a won Defend, Survival or Boss Rush whose session can go on shows "Continue (endless)" and "End". Continue claims the
    /// reward first (the win and its rewards stay recorded whatever happens next), reopens the world and resumes; the endless
    /// part then pays its coins and badges as the waves (bosses) go by.
    /// </para>
    /// Kept apart from MatchRunner.cs so the two change independently.
    /// </summary>
    public sealed partial class MatchRunner
    {
        /// <summary>The camera reaches the last target in this long; slow motion starts then.</summary>
        private const float EndCameraSeconds = 1.5f;

        /// <summary>The pictures' pace in a slow-motion ending (sheet "Kết trận": x0.3).</summary>
        private const float EndSlowScale = 0.3f;

        /// <summary>Seconds between two blasts of a boss's death chain (the sheet's 0.3-0.5 s).</summary>
        private const float ChainGap = 0.4f;

        /// <summary>A target destroyed this long before the resolve still draws the camera.</summary>
        private const double EndTargetWindow = 6.0;

        private MatchOutcome _endOutcome;
        private bool _presenting;
        private Vector3 _endFocus;
        private float _endZoom;
        private readonly List<(Vector3 at, float when, ExplosionTier tier)> _endBlasts = new();
        private int _endBlastNext;
        private readonly List<string> _missedStory = new();

        // The last targets, as the battle went: the enemy's (a boss's parts with it) and ours.
        private Vector2? _lastEnemyDown, _lastOwnDown;
        private double _lastEnemyDownAt = double.NegativeInfinity, _lastOwnDownAt = double.NegativeInfinity;
        private bool _lastEnemyBoss;
        private readonly List<Vector3> _lastBossParts = new();
        private int _endlessSteps;

        /// <summary>While the match end plays (between the resolve and the results panel).</summary>
        internal bool Presenting => _presenting;

        /// <summary>From <see cref="DispatchEvents"/>: a vehicle destroyed, remembered as the camera's last target.</summary>
        private void NoteEndTarget(in SimEvent e)
        {
            if (_menu) return;
            if (e.Team == PlayerTeam)
            {
                _lastOwnDown = new Vector2(e.Position.X, e.Position.Y);
                _lastOwnDownAt = _world.Time;
                return;
            }
            if (e.Team != EnemyTeam || !_world.Catalog.Vehicles.TryGetValue(e.DefId, out var def)) return;
            // A boss stays the target over the escorts that fall after it in the same moment.
            if (_lastEnemyBoss && !def.Boss && _world.Time - _lastEnemyDownAt < 2.0) return;
            _lastEnemyDown = new Vector2(e.Position.X, e.Position.Y);
            _lastEnemyDownAt = _world.Time;
            _lastEnemyBoss = def.Boss;
            _lastBossParts.Clear();
            if (!def.Boss) return;
            // Where its parts were as it died (the view's nodes, else the Sim's places, else round the hull).
            var parts = Mathf.Min(def.Parts.Count, 6);
            for (var i = 0; i < parts; i++)
            {
                if (_views.TryGet(e.Entity, out var view)) _lastBossParts.Add(view.PartWorld(i));
                else if (_world.TryGetVehicle(e.Entity, out var boss)) _lastBossParts.Add(new Vector3(boss.PartPosition(i).X, 1.5f, boss.PartPosition(i).Y));
            }
            if (_lastBossParts.Count == 0)
            {
                var r = Mathf.Max(3f, def.Radius * 0.6f);
                for (var i = 0; i < 4; i++)
                {
                    var a = i * Mathf.PI * 0.5f + 0.4f;
                    _lastBossParts.Add(new Vector3(e.Position.X + Mathf.Cos(a) * r, 1.5f, e.Position.Y + Mathf.Sin(a) * r));
                }
            }
        }

        /// <summary>The outcome came: the world resolves and the presentation starts (the results follow it).</summary>
        private void BeginEnding(MatchOutcome outcome)
        {
            _endOutcome = outcome;
            // A session that decided the result itself: the world resolves now (nothing of the battle moves from here).
            if (_world.Ending.Phase == MatchPhase.Running) _world.IsOver = true;
            var kind = EndKindOf(outcome);
            _world.Ending.BeginPresentation(kind);
            if (_world.Ending.Phase != MatchPhase.Presentation)
            {
                // Nothing to present (the world was not resolved: a session that reopens itself): straight to the results.
                ShowOutcome(outcome);
                return;
            }
            _presenting = true;
            _missedStory.Clear();
            _hud.SetEnding(true);
            _commander?.Disarm();
            _selection.Deselect();
            PlanEndShot(kind);
            Haptics.Pulse(outcome.Result > 0 ? 120 : 90, 200);
        }

        /// <summary>
        /// The presentation's length (sheet "Kết trận"): the first win of a main boss's mission or a big operation 6-8 s, a
        /// first win 4-5 s, a mission played again (and the quick modes) 2.5-4 s, a loss 3-4 s.
        /// </summary>
        private EndKind EndKindOf(MatchOutcome outcome)
        {
            if (outcome.Result < 0) return EndKind.Loss;
            if (outcome.Result == 0) return EndKind.Replay;
            if (_session is MissionSession mission)
            {
                // Before the reward is claimed: the mission is recorded with the claim.
                if (PlayerProfile.Completed(mission.Def.Id)) return EndKind.Replay;
                return mission.Def.Boss != null || mission.Def.Operation || mission.Operation != null ? EndKind.FirstBigWin : EndKind.FirstWin;
            }
            return _session is BossRushSession or SiegeSession or WeeklySession ? EndKind.FirstWin : EndKind.Replay;
        }

        /// <summary>Where the camera goes, and the blasts it sees.</summary>
        private void PlanEndShot(EndKind kind)
        {
            _endBlasts.Clear();
            _endBlastNext = 0;
            _endZoom = _camera.Zoom * 0.9f;
            var resolved = _world.Ending.ResolvedTime;
            _endFocus = _camera.Focus;
            if (kind == EndKind.Loss)
            {
                // Our HQ (standing or not), else the last vehicle we lost; one blast there.
                if (_world.Bases.Of(PlayerTeam) is { } home && _world.TryGetVehicle(home.Hq, out var hq))
                    _endFocus = new Vector3(hq.Position.X, 0f, hq.Position.Y);
                else if (_lastOwnDown is { } own && resolved - _lastOwnDownAt < EndTargetWindow)
                    _endFocus = new Vector3(own.x, 0f, own.y);
                _endBlasts.Add((_endFocus + Vector3.up, 0.6f, ExplosionTier.Large));
                return;
            }
            if (_lastEnemyDown is { } down && resolved - _lastEnemyDownAt < EndTargetWindow)
            {
                _endFocus = new Vector3(down.x, 0f, down.y);
                if (_lastEnemyBoss)
                {
                    // The boss's death chain: part by part, then the hull.
                    var when = 0.3f;
                    foreach (var part in _lastBossParts)
                    {
                        _endBlasts.Add((part, when, ExplosionTier.Large));
                        when += ChainGap;
                    }
                    _endBlasts.Add((_endFocus + Vector3.up * 1.5f, when + 0.1f, ExplosionTier.Huge));
                }
            }
            else if (_world.Bases.Of(EnemyTeam) is { } theirs && _world.TryGetVehicle(theirs.Hq, out var enemyHq))
                _endFocus = new Vector3(enemyHq.Position.X, 0f, enemyHq.Position.Y);
        }

        /// <summary>Every frame (end of Update): the presentation's clock, its blasts, the tap that skips it, the results.</summary>
        private void TickEnding()
        {
            if (!_presenting) return;
            var ending = _world.Ending;
            if (ending.Phase == MatchPhase.Presentation)
            {
                ending.Advance(Time.unscaledDeltaTime);
                var t = (float)ending.Elapsed;
                while (_endBlastNext < _endBlasts.Count && _endBlasts[_endBlastNext].when <= t)
                {
                    var (at, _, tier) = _endBlasts[_endBlastNext++];
                    _effects.Blast(tier, at);
                    Haptics.Pulse(tier >= ExplosionTier.Huge ? 160 : 80, 220);
                }
                if (TappedThisFrame()) ending.Skip();
            }
            // The view's pace: slow motion from 1.5 s for a big or first win, eased in; the Sim is not stepped at all.
            Time.timeScale = ending.Phase == MatchPhase.Presentation && ending.SlowMotion
                ? Mathf.Lerp(1f, EndSlowScale, Mathf.Clamp01(((float)ending.Elapsed - EndCameraSeconds) / 0.3f))
                : 1f;
            if (ending.Phase == MatchPhase.Results) FinishEnding();
        }

        /// <summary>The camera during the presentation: to the last target in the first 1.5 s, then held there.</summary>
        private void EndingCamera() =>
            _camera.Glide(_endFocus, _endZoom, Time.unscaledDeltaTime, (float)_world.Ending.Elapsed < EndCameraSeconds ? 3f : 6f);

        /// <summary>The letterbox while the presentation plays (in over 0.4 s).</summary>
        private float EndingLetterbox => _presenting && _world.Ending.Phase == MatchPhase.Presentation
            ? Mathf.Clamp01((float)_world.Ending.Elapsed / 0.4f)
            : 0f;

        private static bool TappedThisFrame() =>
            (Touchscreen.current?.primaryTouch.press.wasPressedThisFrame ?? false) ||
            (Mouse.current?.leftButton.wasPressedThisFrame ?? false) ||
            (Keyboard.current?.spaceKey.wasPressedThisFrame ?? false);

        /// <summary>RESULTS: the story lines the presentation cut go to the results (and the log), then the panel.</summary>
        private void FinishEnding()
        {
            _presenting = false;
            Time.timeScale = 1f;
            _hud.SetEnding(false);
            _missedStory.Clear();
            if (_dialogue != null)
                foreach (var line in _dialogue.FlushStory(_dialogueClock))
                    _missedStory.Add(DialogueText.Subtitle(line.Name, line.Words, _hud.Dialogue?.ColourFor(line.Enemy)));
            var outcome = _endOutcome;
            if (outcome != null) ShowOutcome(outcome);
        }

        /// <summary>L5: the endless part goes on from the results (the reward claimed first).</summary>
        private void ContinueEndless()
        {
            if (!_resultShown || _session == null || !_session.CanContinue) return;
            ClaimReward();
            if (!_session.ContinueEndless(_world)) return;
            _resultShown = false;
            _endOutcome = null;
            _reward = null;
            _endlessSteps = _session.Mode is IEndlessMode e ? e.EndlessSteps : 0;
            Time.timeScale = 1f;
            _hud.HideResult();
            _music?.Resume();
            _hud.Toast(Strings.Get("result.endlessKept"), seconds: 4f, kind: NoticeKind.Reward);
        }

        /// <summary>The endless parts' mode id (Endless, the menu entry, shares Defend's).</summary>
        private string EndlessId => _session is SurvivalSession ? "survival" : _session is BossRushSession ? "bossrush" : "defend";

        /// <summary>L5, every frame in battle: the endless part's coins (and a badge) as the waves or bosses go by.</summary>
        private void TickEndless()
        {
            if (_menu || _presenting || _resultShown || _session?.Mode is not IEndlessMode { InEndless: true } endless) return;
            var paid = _session.PayEndless(EndlessId);
            if (paid > 0) _hud.Toast(Strings.Format("toast.endlessPaid", ("coins", paid)), seconds: 2.5f, kind: NoticeKind.Reward);
            if (endless.EndlessSteps == _endlessSteps) return;
            _endlessSteps = endless.EndlessSteps;
            var badge = EndlessRules.BadgeAt(_endlessSteps, _session.Mode is BossRushMode);
            if (badge > 0) _hud.Toast(Strings.Format("toast.endlessBadge", ("steps", badge)), seconds: 4f, kind: NoticeKind.Reward);
        }
    }
}
