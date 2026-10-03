"""Units of the numeric columns units.py could not name (the old Don_vi_chua_ro sheet), for Schema.don_vi.

Read from the C# docs where they say it (TierFx.Muzzle, EffectLife.Band) and from the column's own name and neighbours
elsewhere; a column whose meaning the name and the code comments do not settle says khong_ro. Labels: s, m, m/s, deg,
hp, hp/s, CP, CP/s, kg, mm, byte, xu (coins), diem (points), so_luong (a count), he_so (a multiplier or weight), ty_le (a
share 0-1), khong_don_vi (an index, a flag, a vector component), khong_ro.
"""
from __future__ import annotations

NO_UNIT = "khong_don_vi"
UNKNOWN = "khong_ro"


def _group(unit: str, names: str) -> dict:
    return {n: unit for n in names.split()}


FILL: dict[str, str] = {}
for _u, _n in (
    ("s", "ban_flash_life ban_puff_life_arg0 ban_puff_life_arg1 doi_fireball doi_smoke_max doi_smoke_min burrow_surface "
          "burrow_under factory_grow landing_stop pods_fall tiers_crash_fall bien_co_warning params_burn params_fall "
          "params_hold params_outage params_slow_for params_still prep_seconds waves_first transform flight "
          "numbers_escalation_at numbers_final_phase numbers_overtime numbers_rebuild_cutoff numbers_sudden_death "
          "paradrop_fall relay_quiet"),
    ("m", "ban_dust_ring ban_pressure ban_puff_size bombard_blind_scatter bombard_scatter pods_spread salvo_blind_scatter "
          "salvo_spread salvo_sweep scoot_min scoot_max defaults_tiers_heights_high defaults_tiers_heights_low "
          "defaults_tiers_heights_orbit tiers_heights_high tiers_heights_low tiers_heights_orbit band d edge_band "
          "edges_band edges_outer end far fortress_inner_wall fortress_outer_line fortress_outer_wall gate_w patrol play "
          "play_area_max_x play_area_max_z play_area_min_x play_area_min_z play_from play_to ring s "
          "sea_routes_corridor sight_jammer_close target_radius target_x target_z terrain_cell visual_ingress_length w "
          "wingman_decoy wingman_follow numbers_anti_snipe_range numbers_base_radius escort_max_advance_distance "
          "escort_safe_zone_radius leash_distance deploy_front naval_dash_w naval_station"),
    ("m/s", "crush_min_speed"),
    ("deg", "facing rot blast_wall_cone ban_squat"),
    ("hp", "bombard_pierce_damage"),
    ("hp/s", "crush_dps fire_trail_dps params_dps"),
    ("CP", "numbers_max_bank player_max_cp"),
    ("CP/s", "relay_second"),
    ("byte", "file_bytes"),
    ("xu", "price"),
    ("diem", "numbers_losses numbers_losses_at_zero_cp numbers_per_second numbers_sector_bonus numbers_start "
             "numbers_target"),
    ("so_luong", "air_cap animations berms bodies bombard_pierce_max bien_co_ally_waves bien_co_escorts bien_co_step "
                 "craft_max craft_per ditches dry_beds embers enemy_hq extra_escorts extra_raiders factory_max factory_min "
                 "hills landing_landings landing_max landing_min loads_air_to_air loads_jassm loads_jet_bombs "
                 "loose_pieces low_tongues material_slots materials materials_used meshes mines_turn_strip min_rarity "
                 "moving_parts moving_parts_muc moving_parts_tran nodes numbers_boss_wave numbers_bosses "
                 "numbers_kill_cap numbers_mini_boss_wave numbers_neutrals_max params_directions params_max params_need "
                 "params_salvos params_size pods_max pods_min pods_per_pod rank_bonus rare_prints renderers "
                 "renderers_muc renderers_tran routes scoot_shots skins submeshes targets textures tongues triangles "
                 "triangles_muc triangles_tran trigger_times variants vertices vertices_muc vertices_tran "
                 "waves_max_alive waves_max_size waves_size degenerate_triangles non_finite_values non_manifold_edges "
                 "open_edges color0_out_of_range primitives_missing_color_0 primitives_missing_normal "
                 "primitives_missing_texcoord_0 ban_puffs fire_control_focus"),
    ("ty_le", "blast_wall_cut color0_max color0_mean color0_min color0_p05 color0_p95 crush_armour_cut heal lod1_share "
              "metallic roughness numbers_anti_snipe_share numbers_catch_up_max numbers_overtime_lead repair_rate "
              "searchlight_dazzle shelter_cut trigger_progress"),
    ("he_so", "air_rearm_rate balloon_scatter ban_flash ban_light ban_water both_damage both_hp brightness collapse "
              "density doi_crater enemy enemy_hp escort_rear_guard_weight escort_threat_to_convoy_weight "
              "bien_co_ally bien_co_wave_scale main_scale numbers_bleed numbers_escalation_income numbers_final_scale "
              "numbers_kill_ticket_factor numbers_sudden_death_income params_clear params_sight rearm_rate score "
              "sea_sight time_scale tower_damage tower_hp trigger_outnumbered waves_grow wingman_pull "
              "wall_route_breach wall_route_route wall_route_threat"),
    ("khong_don_vi", "cruise_final dir_x dir_z in_x in_z interlude neutral params_wind_x params_wind_z seed team"),
):
    FILL.update(_group(_u, _n))

# the weights of a tactic module (06/Chien_thuat modules_*) are multipliers
for _n in ("artillery_prep attack_threshold bounding cohesion counterattack cp_saving drop_secondary fallback flank focus "
           "heavy_lead hold hold_base hold_fire kite main_effort mass_support pace pincer sead_cards spread together "
           "wait_air").split():
    FILL["modules_" + _n] = "he_so"
for _n in ("one_piece two_piece_arg1 two_piece_arg2 two_piece_arg3 four_piece_arg1 four_piece_arg2 four_piece_arg3 "
           "hq_skill_threat tiers_shift tiers_opening defaults_tiers_shift").split():
    FILL[_n] = UNKNOWN

# per (sheet, column) where the same name means different things
FILL_SHEET: dict[tuple, str] = {
    ("Vu_khi", "size"): "mm", ("Ban_do", "size"): "m", ("VFX_chay_than_xe", "size"): "m",
    ("Vu_khi", "spread"): "deg", ("Boss_bo_phan", "spread"): "deg",
    ("AI_tham_so", "min"): UNKNOWN, ("AI_tham_so", "max"): UNKNOWN, ("Boss_sieu_vu_khi_don", "max"): "so_luong",
    ("VFX_chay_than_xe", "power"): UNKNOWN, ("VFX_chay_than_xe", "smoke_alpha"): "ty_le",
    ("VFX_chay_than_xe", "smoke_shade"): "ty_le", ("VFX_chay_than_xe", "smoke_size"): "m",
    ("VFX_chay_than_xe", "sparks"): "he_so",
    ("Chuong", "interlude"): NO_UNIT, ("Chien_thuat", "interlude"): NO_UNIT,
    ("Ban_do_goc", "seed"): NO_UNIT, ("Ban_do_goc", "density"): "he_so",
    ("Ban_do_biome", "band"): "m", ("Ban_do_biome", "play"): "m",
    ("Ban_do_vat_the", "neutral"): NO_UNIT,
    ("Vat_the_loai", "collapse"): UNKNOWN,
    ("Boss", "flight"): "s", ("Boss", "cruise_final"): NO_UNIT,
    ("Model_kiem_chuan", "triangles"): "so_luong",
}


def unit_for(sheet: str, col: str) -> str:
    return FILL_SHEET.get((sheet, col)) or FILL.get(col) or UNKNOWN
