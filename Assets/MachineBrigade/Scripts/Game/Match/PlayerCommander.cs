using System;
using System.Collections.Generic;
using MachineBrigade.Game.CameraControl;
using MachineBrigade.Game.Hud;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using UnityEngine;
using SimVector2 = System.Numerics.Vector2;

namespace MachineBrigade.Game.Match
{
    /// <summary>
    /// The player's deck: vehicle cards buy a vehicle straight away; support cards arm a strike
    /// that the next tap on the battlefield calls in. Everything goes through
    /// <see cref="SimWorld.Submit"/>, so the same rules apply as for the AI (architecture rule 8).
    /// </summary>
    internal sealed class PlayerCommander
    {
        private readonly SimWorld _world;
        private readonly BattleHud _hud;
        private readonly RtsCamera _camera;
        private readonly int _team;
        private readonly List<CardInfo> _cards;
        private readonly CardState[] _states;
        private int _armed = -1;
        private int _armedItem = -1;
        private readonly List<string> _items = new();
        private ItemState[] _itemStates = Array.Empty<ItemState>();

        public PlayerCommander(SimWorld world, BattleHud hud, RtsCamera camera, int team, List<CardInfo> cards)
        {
            _world = world;
            _hud = hud;
            _camera = camera;
            _team = team;
            _cards = cards;
            _states = new CardState[cards.Count];
            hud.CardPressed += OnCard;
            hud.TargetCancelled += Disarm;
            hud.HqSkillPressed += OnSkill;
            // Items the player brought (bought with coins): a strip of their own under the minimap.
            if (world.TryGetEconomy(team, out var economy))
                foreach (var id in Progression.Items)
                    if (economy.ItemCount(id) > 0) _items.Add(id);
            if (_items.Count > 0)
            {
                _itemStates = new ItemState[_items.Count];
                hud.SetupItems(_items);
                hud.ItemPressed += OnItem;
            }
        }

        /// <summary>Id of the support (or item) waiting for a target, or null.</summary>
        public string ArmedSupport => _armed >= 0 ? _cards[_armed].Id : _armedItem >= 0 ? _items[_armedItem] : _armedSkill ? ArmedSkillId : null;

        /// <summary>Prompt 32 L4: what <see cref="ArmedSupport"/> reads while the HQ's barrage waits for its point (Back disarms it).</summary>
        public const string ArmedSkillId = "hq.skill";

        /// <summary>
        /// What calling a card costs now, to the fraction of a CP (prompt 22 F: a commander's price change; the card shows it
        /// to the whole CP), so a card lights up exactly when the economy would take it.
        /// </summary>
        private float Price(MachineBrigade.Sim.Economy.TeamEconomy economy, CardInfo card)
        {
            if (economy.Commander == null) return card.Cost;
            if (card.Support) return _world.Catalog.TryGetSupport(card.Id, out var s) ? economy.PriceOf(card.Id, s.CpCost) : card.Cost;
            return _world.Catalog.Vehicles.TryGetValue(card.Id, out var v) ? economy.PriceOf(card.Id, v.CpCost) : card.Cost;
        }

        /// <summary>Builds the card list for a deck, reading costs from the catalog.</summary>
        public static List<CardInfo> Cards(SimWorld world, IEnumerable<string> vehicles, IEnumerable<string> supports)
        {
            var cards = new List<CardInfo>();
            // The price the player pays: a ranked card's is cut (see CardRanks.CallCost).
            var economy = world.TryGetEconomy(0, out var e) ? e : null; // the player is team 0
            foreach (var id in vehicles)
                if (world.Catalog.Vehicles.TryGetValue(id, out var v))
                    cards.Add(new CardInfo(id, false, economy?.CostOf(id, v.CpCost) ?? v.CpCost, CardIcons.For(id), StoresStrip.MissileLoad(v), v.FlareCharges));
            foreach (var id in supports)
                if (world.Catalog.TryGetSupport(id, out var s))
                    cards.Add(new CardInfo(id, true, economy?.CostOf(id, s.CpCost) ?? s.CpCost, CardIcons.For(id)));
            return cards;
        }

        /// <summary>Tap interceptor: while a strike is armed, the tap chooses its target.</summary>
        public bool TryTap(Vector2 screen)
        {
            if (_armed < 0 && _armedItem < 0 && !_armedSkill) return false;
            if (!_camera.TryGroundPoint(screen, out var ground)) return true;
            // Prompt 32 L4: a Fortress HQ's barrage lands where the map is tapped.
            if (_armedSkill)
            {
                var skill = _world.SubmitPlayer(Command.HqSkill(_team, new SimVector2(ground.x, ground.z)));
                if (!skill.Accepted) _hud.ShowError(skill.Error);
                else Disarm();
                return true;
            }
            var id = ArmedSupport;
            var point = new SimVector2(ground.x, ground.z);
            // Prompt 25 F2 batch A: an armed airborne vehicle card drops it on the tapped ground.
            if (_armed >= 0 && !_cards[_armed].Support)
            {
                var drop = _world.SubmitPlayer(Command.Paradrop(_team, id, point));
                if (!drop.Accepted) _hud.ShowError(drop.Error);
                else
                {
                    _hud.Toast(Strings.Format("toast.deployed", Strings.Unit(id)));
                    Disarm();
                }
                return true;
            }
            var towards = point;
            if (_world.Catalog.TryGetSupport(id, out var support) && support.IsLine && _world.TryGetRally(_team, out var home))
            {
                // Bombers run in from our side of the map, centred on the tap.
                var along = point - home;
                along = along.LengthSquared() > 1f ? SimVector2.Normalize(along) : SimVector2.UnitX;
                point -= along * (support.Length * 0.5f);
                towards = point + along;
            }
            var result = _world.SubmitPlayer(Command.Strike(_team, id, point, towards));
            if (!result.Accepted) _hud.ShowError(result.Error);
            else Disarm();
            return true;
        }

        public void Update()
        {
            if (!_world.TryGetEconomy(_team, out var economy)) return;
            // Auto support can spend the CP or start the cooldown of the card being aimed.
            if (_armed >= 0 && (economy.CooldownLeft(_cards[_armed].Id, _world.Time) > 0f || economy.Cp < Price(economy, _cards[_armed]))) Disarm();
            for (var i = 0; i < _cards.Count; i++)
            {
                var card = _cards[i];
                if (card.Support)
                {
                    var cooldown = 0f;
                    if (_world.Catalog.TryGetSupport(card.Id, out var s) && s.Cooldown > 0f)
                        cooldown = economy.CooldownLeft(card.Id, _world.Time) / s.Cooldown;
                    _states[i] = new CardState(economy.Cp >= Price(economy, card), false, cooldown, i == _armed, economy.CooldownLeft(card.Id, _world.Time));
                }
                else
                {
                    _states[i] = new CardState(economy.Cp >= Price(economy, card), economy.VehicleCount >= MachineBrigade.Sim.Economy.TeamEconomy.MaxVehicles, 0f, i == _armed);
                }
            }
            UpdateSkill();
            // The supply upkeep (prompt 29 pass 0 removed prompt 28's second, army-size factor; the owner: "use supply").
            _hud.SetDeck(economy.Cp, economy.Bank, economy.Earning, economy.Upkeep * economy.CatchUp, _states);
            if (_items.Count == 0) return;
            if (_armedItem >= 0 && (economy.ItemCount(_items[_armedItem]) <= 0 || economy.CooldownLeft(_items[_armedItem], _world.Time) > 0f)) Disarm();
            for (var i = 0; i < _items.Count; i++)
            {
                var cooldown = 0f;
                if (_world.Catalog.TryGetSupport(_items[i], out var s) && s.Cooldown > 0f)
                    cooldown = economy.CooldownLeft(_items[i], _world.Time) / s.Cooldown;
                _itemStates[i] = new ItemState(economy.ItemCount(_items[i]), cooldown, i == _armedItem);
            }
            _hud.SetItems(_itemStates);
        }

        private void OnItem(int index)
        {
            if (_armedItem == index)
            {
                Disarm();
                return;
            }
            if (!_world.TryGetEconomy(_team, out var economy)) return;
            var id = _items[index];
            if (economy.ItemCount(id) <= 0) return;
            if (economy.CooldownLeft(id, _world.Time) > 0f)
            {
                _hud.ShowError(CommandError.OnCooldown);
                return;
            }
            _armed = -1;
            _armedItem = index;
            _armedSkill = false;
            _hud.SetTargeting(Strings.Format("target.hint", Strings.Support(id)));
        }

        private void OnCard(int index)
        {
            var card = _cards[index];
            // Prompt 25 F2 batch A: an airborne vehicle's card arms a drop (tap the map where the side sees); tapped again it
            // comes to the drop zone as any vehicle does.
            if (!card.Support && _armed != index && _world.Catalog.Vehicles.TryGetValue(card.Id, out var airborne) && airborne.Paradrop != null)
            {
                if (_world.TryGetEconomy(_team, out var cash) && cash.Cp < Price(cash, card))
                {
                    _hud.ShowError(CommandError.NotEnoughCp);
                    return;
                }
                _armed = index;
                _armedItem = -1;
                _hud.SetTargeting(Strings.Format("target.paradrop", Strings.Unit(card.Id)));
                return;
            }
            if (!card.Support)
            {
                if (_armed == index) Disarm();
                var result = _world.SubmitPlayer(Command.Deploy(_team, card.Id));
                if (result.Accepted) _hud.Toast(Strings.Format("toast.deployed", Strings.Unit(card.Id)));
                else _hud.ShowError(result.Error);
                return;
            }

            if (_armed == index)
            {
                Disarm();
                return;
            }
            if (!_world.TryGetEconomy(_team, out var economy)) return;
            if (economy.CooldownLeft(card.Id, _world.Time) > 0f)
            {
                _hud.ShowError(CommandError.OnCooldown);
                return;
            }
            if (economy.Cp < Price(economy, card))
            {
                _hud.ShowError(CommandError.NotEnoughCp);
                return;
            }
            _armed = index;
            _armedItem = -1;
            _armedSkill = false;
            _hud.SetTargeting(Strings.Format("target.hint", Strings.Support(card.Id)));
        }

        // ------------------------------------------------------------------ prompt 32 L4: the HQ skill

        private bool _armedSkill;

        /// <summary>The HQ skill button: its type's icon and name, its cooldown, armed while a barrage waits for its point.</summary>
        private void UpdateSkill()
        {
            var state = _world.Bases.Of(_team)?.Hq32;
            if (state == null || !state.Ready || state.Type == MachineBrigade.Sim.Content.HqType.None || (_world.Bases.Of(_team)?.HqFallen ?? true))
            {
                if (_armedSkill) Disarm();
                _hud.SetHqSkill(null, null, null, 0f, 0f, false);
                return;
            }
            var rules = _world.Catalog.Base.HqTypes;
            var left = state.SkillLeft(_world.Time);
            if (_armedSkill && left > 0f) Disarm();
            var key = MachineBrigade.Sim.Content.HqTypeRules.Key(state.Type);
            var icon = state.Type switch
            {
                MachineBrigade.Sim.Content.HqType.Fortress => "barrage",
                MachineBrigade.Sim.Content.HqType.Garrison => "reinforce",
                _ => "shield",
            };
            var tip = Strings.Format("hq.skill." + key + ".tip", ("cooldown", Mathf.RoundToInt(rules.SkillCooldown)), ("stock", state.Stock),
                ("seconds", Mathf.RoundToInt(rules.DomeSeconds)), ("share", Mathf.RoundToInt(rules.Dome(state.Level) * 100f)));
            _hud.SetHqSkill(icon, Strings.Get("hq.skill." + key), tip, left / Mathf.Max(1f, rules.SkillCooldown), left, _armedSkill);
        }

        private void OnSkill()
        {
            var state = _world.Bases.Of(_team)?.Hq32;
            if (state == null || !state.Ready || state.Type == MachineBrigade.Sim.Content.HqType.None) return;
            if (_armedSkill)
            {
                Disarm();
                return;
            }
            if (state.SkillLeft(_world.Time) > 0f)
            {
                _hud.ShowError(CommandError.OnCooldown);
                return;
            }
            if (state.Type == MachineBrigade.Sim.Content.HqType.Fortress)
            {
                _armed = -1;
                _armedItem = -1;
                _armedSkill = true;
                _hud.SetTargeting(Strings.Get("target.hqSkill"));
                return;
            }
            var result = _world.SubmitPlayer(Command.HqSkill(_team));
            if (!result.Accepted) _hud.ShowError(result.Error);
        }

        public void Disarm()
        {
            _armedSkill = false;
            _armed = -1;
            _armedItem = -1;
            _hud.SetTargeting(null);
        }
    }
}
