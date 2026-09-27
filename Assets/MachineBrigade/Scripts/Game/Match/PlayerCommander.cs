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
        public string ArmedSupport => _armed >= 0 ? _cards[_armed].Id : _armedItem >= 0 ? _items[_armedItem] : null;

        /// <summary>Builds the card list for a deck, reading costs from the catalog.</summary>
        public static List<CardInfo> Cards(SimWorld world, IEnumerable<string> vehicles, IEnumerable<string> supports)
        {
            var cards = new List<CardInfo>();
            foreach (var id in vehicles)
                if (world.Catalog.Vehicles.TryGetValue(id, out var v)) cards.Add(new CardInfo(id, false, v.CpCost, CardIcons.For(id)));
            foreach (var id in supports)
                if (world.Catalog.TryGetSupport(id, out var s)) cards.Add(new CardInfo(id, true, s.CpCost, CardIcons.For(id)));
            return cards;
        }

        /// <summary>Tap interceptor: while a strike is armed, the tap chooses its target.</summary>
        public bool TryTap(Vector2 screen)
        {
            if (_armed < 0 && _armedItem < 0) return false;
            if (!_camera.TryGroundPoint(screen, out var ground)) return true;
            var id = ArmedSupport;
            var point = new SimVector2(ground.x, ground.z);
            var towards = point;
            if (_world.Catalog.TryGetSupport(id, out var support) && support.IsLine && _world.TryGetRally(_team, out var home))
            {
                // Bombers run in from our side of the map, centred on the tap.
                var along = point - home;
                along = along.LengthSquared() > 1f ? SimVector2.Normalize(along) : SimVector2.UnitX;
                point -= along * (support.Length * 0.5f);
                towards = point + along;
            }
            var result = _world.Submit(Command.Strike(_team, id, point, towards));
            if (!result.Accepted) _hud.ShowError(result.Error);
            else Disarm();
            return true;
        }

        public void Update()
        {
            if (!_world.TryGetEconomy(_team, out var economy)) return;
            // Auto support can spend the CP or start the cooldown of the card being aimed.
            if (_armed >= 0 && (economy.CooldownLeft(_cards[_armed].Id, _world.Time) > 0f || economy.Cp < _cards[_armed].Cost)) Disarm();
            for (var i = 0; i < _cards.Count; i++)
            {
                var card = _cards[i];
                if (card.Support)
                {
                    var cooldown = 0f;
                    if (_world.Catalog.TryGetSupport(card.Id, out var s) && s.Cooldown > 0f)
                        cooldown = economy.CooldownLeft(card.Id, _world.Time) / s.Cooldown;
                    _states[i] = new CardState(economy.Cp >= card.Cost, false, cooldown, i == _armed);
                }
                else
                {
                    _states[i] = new CardState(economy.Cp >= card.Cost, economy.VehicleCount >= MachineBrigade.Sim.Economy.TeamEconomy.MaxVehicles, 0f, false);
                }
            }
            _hud.SetDeck(economy.Cp, economy.Bank, economy.Earning, economy.Upkeep, _states);
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
            _hud.SetTargeting(Strings.Format("target.hint", Strings.Support(id)));
        }

        private void OnCard(int index)
        {
            var card = _cards[index];
            if (!card.Support)
            {
                var result = _world.Submit(Command.Deploy(_team, card.Id));
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
            if (economy.Cp < card.Cost)
            {
                _hud.ShowError(CommandError.NotEnoughCp);
                return;
            }
            _armed = index;
            _armedItem = -1;
            _hud.SetTargeting(Strings.Format("target.hint", Strings.Support(card.Id)));
        }

        public void Disarm()
        {
            _armed = -1;
            _armedItem = -1;
            _hud.SetTargeting(null);
        }
    }
}
