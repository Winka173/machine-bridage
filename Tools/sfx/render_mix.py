"""Fix pass L7: three offline test mixes of the battle sound, rendered from the library by the game's mixing rules (no Unity).

    python Tools/sfx/render_mix.py            # Docs/audio/samples/{normal,boss,crowded}_battle.ogg + mixes.json
    python Tools/sfx/render_mix.py --wav      # .wav instead

A scripted, seeded battle per mix (events: shots, landings, hits by surface, wrecks, whistles, flares, engines) heard from a
camera over the field's centre. The mixing mirrors AudioDirector (fix pass L7) step by step:
  * the bank rules: variants without repeats, per-bank voice limits and cooldowns, the speed of sound for far blasts;
  * the small-arms cluster rule (play-test 12: 3 machine-gun shooters within 20 m inside 0.5 s -> one cluster sound now
    and then); rapid fire (play-test 12: 8.5 rounds a second and up) as one burst segment a shooter, pitched to the gun's
    rate, never cut mid-burst (a new one takes the quietest only when twice as loud); the Sim's events on its 20 Hz tick;
  * play-test 12: a missile's hiss just before it lands (one in 0.3 s);
  * hits by surface and the match-wide metal cap (MetalCap: 3 at once, 2.5 a second, 0.12 s apart);
  * the camera-distance falloff (SoundLibrary.Falloff), bigger sizes carrying farther, 0.85 off screen, the far low pass;
  * 32 voices, 24 for ordinary effects, cut by priority (warnings > boss / 406 mm > near blasts > near shots > far blasts >
    far shots > small arms > ambience);
  * the Effects compressor (control rate, 50 Hz, from the clips' envelopes; threshold 0.3, ratio 3, 30 / 300 ms) and the
    ducking of light sounds under a near blast; the output limiter (-1 dBFS, 120 ms release).
Not mirrored: Unity's pitch spread (8 %) and its exact pan law (a constant-power pan is used here).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_sfx as az  # noqa: E402

SR = 44100
ROOT = Path(__file__).resolve().parents[2]
AUDIO = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Audio'
OUT = ROOT / 'Docs' / 'audio' / 'samples'

# AudioDirector / SoundLibrary constants (fix pass L7).
VOICES, EFFECT_VOICES = 32, 24
REF_DISTANCE, HEIGHT_SHARE = 25.0, 0.5
OFF_SCREEN = 0.85
NEAR_SHARE = 0.45
THRESHOLD, RATIO, ATTACK, RELEASE = 0.3, 3.0, 0.03, 0.3
CEILING = 0.89
SPEED_OF_SOUND = 343.0
P = {'ambient': 10, 'small': 20, 'far_shot': 25, 'far_blast': 30, 'near_shot': 40, 'near_blast': 50, 'boss': 60, 'warning': 70}
SIZE_INDEX = {'s0': 0, 's1': 1, 's2': 2, 's3': 3, 's4': 4, 'bomb': 5, 's406': 6, 'super': 7}

# bank -> (max voices, cooldown s, light (ducked), delayed (speed of sound)) as AudioDirector.AddTierBanks sets them.
BANKS = {}
for i, b in enumerate(['shot_s0', 'shot_s1', 'shot_s2', 'shot_s3', 'shot_s4', 'shot_s406', 'shot_super']):
    BANKS[b] = ([4, 4, 4, 3, 2, 2, 2][i], 0.06 if i <= 1 else 0.05 + 0.01 * i, i <= 1, False)
for b in ['launch_atgm', 'launch_sam', 'launch_s2', 'launch_s3']:
    BANKS[b] = (3, 0.06, False, False)
for b in ['launch_big', 'launch_cruise']:
    BANKS[b] = (2, 0.06, False, False)
# Play-test 12: the 57 mm, the bursts (SoundLibrary.Bursts: bank -> cyclic rate, rounds a segment), the hiss, the old flak bank.
BANKS['shot_ac57'] = (3, 0.07, True, False)
BURSTS = {'burst_s0_10': (0, 10.0, 3), 'burst_s0_16': (0, 16.0, 5), 'burst_s0_55': (0, 55.0, 18), 'burst_s1_10': (1, 10.0, 3),
          'burst_s1_22': (1, 22.0, 7), 'burst_s1_35': (1, 35.0, 12), 'burst_s1_55': (1, 55.0, 18)}
for b in BURSTS:
    BANKS[b] = (3, 0.0, True, False)
NO_STEAL = set(BURSTS)
BANKS['missile_hiss'] = (2, 0.25, True, False)
BANKS['flak'] = (3, 0.08, True, False)
BURST_FROM, PITCH_MIN, PITCH_MAX, BURST_SLACK, HISS_LEAD, HISS_GAP = 8.5, 0.85, 1.18, 0.02, 0.5, 0.3
TICK = 0.05  # the Sim's step (20 Hz): events land on it
for i, b in enumerate(['blast_he_s1', 'blast_he_s2', 'blast_he_s3', 'blast_he_s4', 'blast_bomb', 'blast_he_s406', 'blast_super']):
    BANKS[b] = (2 if i >= 5 else 3 if i >= 2 else 4, 0.04 + 0.01 * i, False, True)
BANKS.update({'blast_thermo_s3': (2, 0.1, False, True), 'blast_thermo_s4': (2, 0.1, False, True), 'blast_heat_s2': (3, 0.05, False, False),
              'blast_heat_s3': (3, 0.05, False, False), 'blast_air_s1': (3, 0.06, True, False), 'blast_air_s2': (3, 0.06, True, False),
              'blast_air_s3': (3, 0.06, True, False)})
for b in ['hit_ground_light', 'hit_concrete_light', 'hit_pen_light']:
    BANKS[b] = (3, 0.05, True, False)
for b in ['hit_ground_heavy', 'hit_concrete_heavy', 'hit_pen_heavy']:
    BANKS[b] = (3, 0.05, False, False)
BANKS.update({'hit_armour_light': (3, 0.05, True, False), 'hit_armour_heavy': (3, 0.05, False, False), 'hit_armour_glance': (3, 0.05, False, False)})
BANKS.update({'hit_metal_light': (2, 0.12, True, False), 'hit_metal_heavy': (2, 0.12, False, False), 'smallarms_cluster': (2, 0.35, True, False),
              'crash_fall': (2, 0.3, False, False), 'crash_impact': (2, 0.1, False, True), 'flare_pop': (2, 0.15, False, False),
              'warn_whistle_big': (2, 0.3, False, False), 'warn_whistle': (3, 0.22, False, False), 'wreck_ship': (2, 0.2, False, True)})
for k in ['tank', 'wheeled', 'truck', 'artillery', 'aircraft', 'heli', 'drone']:
    BANKS['wreck_' + k] = (3, 0.1, False, True)
BANK_VOLUME = {'warn_whistle': 0.5, 'flak': 0.5}


def burst_of(size: int, rate: float):
    """SoundLibrary.BurstBank: (bank, pitch, segment s) of a gun of this size at this rate, or None."""
    if size > 1 or rate < BURST_FROM:
        return None
    best = min((b for b, (z, _, _) in BURSTS.items() if z == size), key=lambda b: abs(math.log(rate / BURSTS[b][1])))
    _, r, rounds = BURSTS[best]
    pitch = min(PITCH_MAX, max(PITCH_MIN, rate / r))
    return best, pitch, rounds / r / pitch


def size_of(bank: str) -> int:
    for key, idx in (('super', 7), ('s406', 6), ('bomb', 5), ('big', 6), ('_s4', 4), ('_s3', 3), ('_s2', 2), ('_s1', 1), ('_s0', 0)):
        if key in bank:
            return idx
    return 2


def falloff(ground: float, height: float, reach: float) -> float:
    if reach <= 0:
        return 0.0
    d = math.sqrt(ground * ground + (height * HEIGHT_SHARE) ** 2)
    near = (REF_DISTANCE / max(REF_DISTANCE, d)) ** 0.7
    edge = min(1.0, max(0.0, 1 - ground / reach))
    return near * edge * edge * (3 - 2 * edge)


def compressor_gain(level: float) -> float:
    return 1.0 if level <= THRESHOLD else (level / THRESHOLD) ** (1 / RATIO - 1)


class Clips:
    def __init__(self):
        self.cache, self.last = {}, {}
        self.env = {}
        for line in (AUDIO / 'sfx' / 'envelopes.txt').read_text(encoding='utf-8').splitlines():
            if line and not line.startswith('#'):
                k, rest = line.split(' ', 1)
                self.env[k] = np.array([int(v) / 1000 for v in rest.split()])

    def files(self, bank: str):
        folder = AUDIO / 'sfx' / bank
        if not folder.exists():
            folder = AUDIO / bank
        return sorted(folder.glob('*.ogg'))

    def next(self, bank: str, rng):
        files = self.files(bank)
        i = int(rng.integers(len(files) - 1)) if len(files) > 1 else 0
        if len(files) > 1 and self.last.get(bank, -1) >= 0 and i >= self.last[bank]:
            i += 1
        self.last[bank] = i
        path = files[i]
        if path not in self.cache:
            x, sr = sf.read(str(path), dtype='float64', always_2d=True)
            x = x.mean(axis=1)
            self.cache[path] = signal.resample_poly(x, SR, sr) if sr != SR else x
        return path.stem, self.cache[path]


class Mixer:
    """AudioDirector's voice and mix rules over a scripted event list."""

    def __init__(self, seconds: float, reach: float = 160.0, height: float = 60.0, seed: int = 7):
        self.seconds, self.reach, self.height = seconds, reach, height
        self.rng = np.random.default_rng(seed)
        self.clips = Clips()
        self.voices = []  # dicts: start, end, bank, level, priority, clip, name, pan, cutoff, light
        self.last_played = {}
        self.small = {}  # shooter -> (last shot, where)
        self.bursts = {}  # shooter -> its segment's end
        self.next_hiss = -10.0
        self.cluster_until, self.cluster_at = -10.0, (0.0, 0.0)
        self.metal = {'tokens': 3.0, 'at': None, 'last': -100.0}
        self.duck = []  # times a near blast ducked the light sounds
        self.stats = {'events': 0, 'played': 0, 'cooldown': 0, 'out_of_reach': 0, 'cut_for_priority': 0, 'dropped_no_voice': 0,
                      'clustered_shots': 0, 'metal_played': 0, 'metal_capped': 0, 'max_busy': 0, 'bursts': 0, 'burst_events': 0,
                      'burst_dropped_at_cap': 0}

    # --- the rules
    def dist(self, at):
        return math.hypot(at[0], at[1])

    def near(self, at):
        return self.dist(at) < self.reach * NEAR_SHARE

    def priority(self, size: int, boss: bool, blast: bool, at) -> int:
        if boss or size >= 6:
            return P['boss']
        if blast:
            return P['near_blast'] if self.near(at) else P['far_blast']
        if size == 0:
            return P['small']
        return P['near_shot'] if self.near(at) else P['far_shot']

    def metal_take(self, now: float) -> bool:
        m = self.metal
        if m['at'] is not None:
            m['tokens'] = min(3.0, m['tokens'] + (now - m['at']) * 2.5)
        m['at'] = now
        if now - m['last'] < 0.12 or m['tokens'] < 1:
            return False
        m['tokens'] -= 1
        m['last'] = now
        return True

    def play(self, t: float, bank: str, at, priority: int, carry: float = 0.0, volume: float = 1.0, pitch: float = 1.0):
        self.stats['events'] += 1
        maxv, cooldown, light, delayed = BANKS.get(bank, (3, 0.05, False, False))
        if t - self.last_played.get(bank, -10) < cooldown:
            self.stats['cooldown'] += 1
            return
        reach = self.reach + carry
        d = self.dist(at)
        if d >= reach * 0.98:
            self.stats['out_of_reach'] += 1
            return
        self.last_played[bank] = t
        delay = min(0.3, max(0.0, d - 30) / SPEED_OF_SOUND) if delayed else 0.0
        self.start(t + (delay if delay > 0.02 else 0.0), bank, at, priority, reach, volume * BANK_VOLUME.get(bank, 1.0), maxv, light, pitch)

    def start(self, t, bank, at, priority, reach, volume, maxv, light, pitch=1.0):
        d = self.dist(at)
        if 1 - d / reach <= 0.02:
            return
        off = abs(at[0]) > 70 or abs(at[1]) > 40
        level = volume * falloff(d, self.height, reach) * (OFF_SCREEN if off else 1.0)
        if level <= 0.001:
            return
        playing = [v for v in self.voices if v['start'] <= t < v['end']]
        self.stats['max_busy'] = max(self.stats['max_busy'], len(playing))
        same = [v for v in playing if v['bank'] == bank]
        victim = None
        if len(same) >= maxv and bank in NO_STEAL:
            quiet = min(same, key=lambda v: v['level'])
            if quiet['level'] * 2 >= level:
                self.stats['burst_dropped_at_cap'] += 1
                return
            victim = quiet
        elif len(same) >= maxv:
            victim = min(same, key=lambda v: v['start'])
        else:
            weaker = [v for v in playing if v['priority'] < priority or (v['priority'] == priority and v['level'] <= level)]
            weakest = min(weaker, key=lambda v: (v['priority'], v['level'])) if weaker else None
            if len(playing) >= EFFECT_VOICES and priority < P['boss']:
                if weakest is None:
                    self.stats['dropped_no_voice'] += 1
                    return
                victim = weakest
                self.stats['cut_for_priority'] += 1
            elif len(playing) >= VOICES:
                if weakest is None:
                    self.stats['dropped_no_voice'] += 1
                    return
                victim = weakest
                self.stats['cut_for_priority'] += 1
        if victim is not None:
            victim['end'] = t
        if priority >= P['near_blast']:
            self.duck.append(t)
        name, clip = self.clips.next(bank, self.rng)
        if abs(pitch - 1) > 1e-3:  # played faster or slower: shorter or longer, the rhythm with it
            clip = np.interp(np.arange(0, len(clip) - 1, pitch), np.arange(len(clip)), clip)
        far = min(1.0, d / reach) ** 0.8
        self.voices.append({'start': t, 'end': t + len(clip) / SR, 'bank': bank, 'level': level, 'priority': priority, 'clip': clip, 'name': name,
                            'pan': max(-0.9, min(0.9, at[0] / 140.0 * 1.4)), 'cutoff': 22000 + (2200 - 22000) * far, 'light': light})
        self.stats['played'] += 1

    def gun(self, t, who, at, size: int, rate: float, bank: str):
        """A machine gun's or an autocannon's round: the cluster rule (machine guns), else its burst segment, else a clip."""
        if size == 0 and self.clustered(t, who, at):
            return
        b = burst_of(size, rate)
        if b is None:
            self.play(t, bank, at, self.priority(size, False, False, at), 12 * size)
            return
        name, pitch, segment = b
        self.stats['burst_events'] += 1
        if t < self.bursts.get(who, -10.0) - BURST_SLACK:
            return
        self.bursts[who] = t + segment
        self.stats['bursts'] += 1
        self.play(t, name, at, self.priority(size, False, False, at), 12 * size, 1.0, pitch)

    def incoming(self, t, at, travel: float):
        """A missile's hiss just before it lands (one in HISS_GAP s)."""
        if travel < HISS_LEAD + 0.4 or t < self.next_hiss:
            return
        self.next_hiss = t + HISS_GAP
        self.play(t + travel - HISS_LEAD, 'missile_hiss', at, P['far_shot'], 0.0, 0.9)

    def clustered(self, t, who, at) -> bool:
        """Three machine-gun shooters within 20 m inside 0.5 s: one cluster sound now and then (True: taken into it)."""
        self.small = {w: (tt, p) for w, (tt, p) in self.small.items() if t - tt <= 0.5 and w != who}
        near = [p for _, p in self.small.values() if math.hypot(p[0] - at[0], p[1] - at[1]) <= 20]
        if len(self.small) < 64:
            self.small[who] = (t, at)
        if len(near) + 1 < 3:
            return False
        self.stats['clustered_shots'] += 1
        if t >= self.cluster_until or math.hypot(self.cluster_at[0] - at[0], self.cluster_at[1] - at[1]) > 20:
            self.cluster_until = t + 0.9
            cx = (at[0] + sum(p[0] for p in near)) / (len(near) + 1)
            cy = (at[1] + sum(p[1] for p in near)) / (len(near) + 1)
            self.cluster_at = (cx, cy)
            self.play(t, 'smallarms_cluster', self.cluster_at, P['small'])
        return True

    def hit(self, t, at, size: int, surface: str):
        heavy = size >= 2
        # play-test 13: armour not pierced knocks (hit_armour_*); a rare share (8 %) whines off as a ricochet under the cap
        if surface == 'metal' and self.rng.random() < 0.08 and self.metal_take(t):
            self.stats['metal_played'] += 1
            bank = 'hit_metal_' + ('heavy' if heavy else 'light')
        else:
            bank = {'metal': 'hit_armour_', 'pierced': 'hit_pen_', 'concrete': 'hit_concrete_', 'ground': 'hit_ground_'}[surface] + ('heavy' if heavy else 'light')
        self.play(t, bank, at, self.priority(size, False, False, at), 12 * size)

    # --- the render
    def render(self, loops=()):
        n = int(self.seconds * SR) + SR * 12
        out = np.zeros((n, 2))
        rate = 50
        blocks = n // (SR // rate) + 1
        sums = np.zeros(blocks)
        for v in self.voices:
            env = self.clips.env.get(v['name'])
            b0 = int(v['start'] * rate)
            b1 = int(v['end'] * rate)
            for b in range(b0, min(b1, blocks)):
                i = b - b0
                rms = env[i] if env is not None and i < len(env) else (0.2 if env is None else 0.0)
                sums[b] += (v['level'] * rms) ** 2
        target = np.array([compressor_gain(math.sqrt(s)) for s in sums])
        gain = np.ones(blocks)
        g = 1.0
        for b in range(blocks):
            tau = ATTACK if target[b] < g else RELEASE
            g += (target[b] - g) * (1 - math.exp(-(1 / rate) / tau))
            gain[b] = g
        duck = np.ones(blocks)
        for t in self.duck:
            b0 = int(t * rate)
            for b in range(b0, min(blocks, b0 + int(0.35 * rate) + 1)):
                left = 0.35 - (b - b0) / rate
                duck[b] = min(duck[b], 1 + (0.5 - 1) * min(1.0, max(0.0, left / 0.35)))
        per_sample = np.repeat(gain, SR // rate)[:n]
        per_duck = np.repeat(duck, SR // rate)[:n]
        for v in self.voices:
            clip = v['clip']
            if v['cutoff'] < 20000:
                sos = signal.butter(1, v['cutoff'] / (SR / 2), output='sos')
                clip = signal.sosfilt(sos, clip)
            a = int(v['start'] * SR)
            m = min(len(clip), int((v['end'] - v['start']) * SR), n - a)
            if m <= 0:
                continue
            seg = clip[:m] * v['level']
            if m < len(clip):  # cut: a 5 ms fade
                k = min(m, int(0.005 * SR))
                seg[-k:] *= np.linspace(1, 0, k)
            seg = seg * per_sample[a:a + m] * (per_duck[a:a + m] if v['light'] else 1.0)
            ang = (v['pan'] + 1) * math.pi / 4
            out[a:a + m, 0] += seg * math.cos(ang) * math.sqrt(2) * 0.7071
            out[a:a + m, 1] += seg * math.sin(ang) * math.sqrt(2) * 0.7071
        for bank, level, t0, t1 in loops:
            _, clip = self.clips.next(bank, self.rng)
            a, b = int(t0 * SR), min(n, int(t1 * SR))
            reps = np.tile(clip, (b - a) // len(clip) + 2)[:b - a]
            fade = np.clip(np.minimum(np.arange(b - a), (b - a) - np.arange(b - a)) / (1.5 * SR), 0, 1)
            out[a:b, 0] += reps * level * fade
            out[a:b, 1] += reps * level * fade
        # The output limiter: peak follower, instant attack, 120 ms release.
        peak = np.max(np.abs(out), axis=1)
        rel = math.exp(-1 / (0.12 * SR))
        # A running max with release, in 64-sample blocks (exact enough for a test mix).
        e = 0.0
        follow = np.empty_like(peak)
        for i in range(0, len(peak), 64):
            blk = peak[i:i + 64]
            top = float(blk.max()) if len(blk) else 0.0
            e = top if top > e else e * rel ** 64
            follow[i:i + 64] = max(e, top)
        lim = np.minimum(1.0, CEILING / np.maximum(follow, 1e-9))
        self.stats['limiter_min_gain_db'] = round(20 * math.log10(float(lim.min())), 1)
        self.stats['compressor_min_gain_db'] = round(20 * math.log10(float(gain.min())), 1)
        out = out * lim[:, None]
        end = int(self.seconds * SR) + SR * 3
        out = out[:end]
        k = SR // 2
        out[-k:] *= np.linspace(1, 0, k)[:, None]
        return out


# ------------------------------------------------------------------------------------------------------- scenarios


def tick(t: float) -> float:
    """The Sim's events come on its 20 Hz step."""
    return math.ceil(t / TICK) * TICK


def field(rng, spread=110.0, depth=60.0):
    return (float(rng.uniform(-spread, spread)), float(rng.uniform(-depth, depth)))


def normal_battle(seconds=40.0):
    """Ten a side: machine guns and autocannons in streams, tank guns (most pierce, some glance, some miss), 152 mm shells,
    ATGMs, two wrecks, a helicopter's flares; tracked engines and the wind."""
    m = Mixer(seconds, seed=11)
    rng = np.random.default_rng(101)
    events = []
    for g in range(8):  # machine guns (play-test 12: 9-16 rounds a second, as the M2, the coax and the bunker's HMG)
        at = field(rng, 90, 40)
        rate = float(rng.choice([9.0, 12.0, 16.0]))
        t = rng.uniform(0, 5)
        while t < seconds - 2:
            for k in range(int(rng.integers(6, 14))):
                events.append((tick(t + k / rate), 'gun', f'mg{g}', at, 0, rate, 'shot_s0'))
                if rng.random() < 0.5:
                    events.append((t + k / rate + 0.3, 'hit', field(rng, 90, 40), 0, 'ground'))
            t += rng.uniform(1.5, 4)
    zu = (60.0, 25.0)  # a ZU-23 (25 rounds a second, flak) and a Bofors (4 a second, the recorded flak burst) at a helicopter
    for t0 in (12.0, 25.0):
        for k in range(30):
            events.append((tick(t0 + k / 25.0), 'gun', 'zu23', zu, 1, 25.0, 'flak'))
        for k in range(6):
            events.append((tick(t0 + 0.5 + k * 0.25), 'gun', 'bofors', (-70.0, 30.0), 1, 4.0, 'flak'))
            events.append((t0 + 1.4 + k * 0.25, 'blast', 'blast_air_s1', (5.0, 35.0), 1))
    for g in range(3):  # 30 mm autocannons on light armour and the ground
        at = field(rng, 80, 40)
        t = rng.uniform(2, 8)
        while t < seconds - 3:
            for k in range(int(rng.integers(3, 6))):
                events.append((tick(t + k * 0.18), 'gun', f'ac{g}', at, 1, 5.5, 'shot_s1'))
                tgt = field(rng, 80, 40)
                events.append((t + k * 0.18 + 0.4, 'hit', tgt, 1, rng.choice(['metal', 'pierced', 'ground', 'ground'])))
            t += rng.uniform(3, 6)
    for _ in range(4):  # tank guns
        at = field(rng, 100, 50)
        t = rng.uniform(1, 6)
        while t < seconds - 2:
            events.append((t, 'shot', 'shot_s3', at, 3))
            events.append((t + 0.3, 'hit', field(rng, 100, 50), 3, rng.choice(['pierced', 'pierced', 'pierced', 'metal', 'ground'])))
            t += rng.uniform(5, 9)
    t = 6.0
    while t < seconds - 4:  # a 152 mm battery
        events.append((t, 'shot', 'shot_s3', (-150.0, 30.0), 3))
        events.append((t + 6, 'whistle', field(rng, 60, 30)))
        events.append((t + 7.2, 'blast', 'blast_he_s3', events[-1][2], 3))
        t += rng.uniform(4, 7)
    for t in (9.0, 21.0, 30.0):  # ATGMs (play-test 12: a launch, the hiss in, the HEAT blast)
        at, tgt = field(rng, 80, 40), field(rng, 80, 40)
        events.append((t, 'shot', 'launch_atgm', at, 2))
        events.append((t, 'incoming', tgt, 1.8))
        events.append((t + 1.8, 'blast', 'blast_heat_s2', tgt, 2))
    for t in (16.0, 33.0):  # a SAM at an aircraft
        events.append((t, 'shot', 'launch_sam', (-60.0, -20.0), 2))
        events.append((t, 'incoming', (-20.0, 30.0), 1.4))
        events.append((t + 1.4, 'blast', 'blast_air_s2', (-20.0, 30.0), 2))
    events.append((15.5, 'wreck', 'wreck_tank', (20.0, -10.0)))
    events.append((27.0, 'wreck', 'wreck_wheeled', (-45.0, 15.0)))
    events.append((18.0, 'flare', (35.0, 20.0)))
    return m, events, [('engine_tracked', 0.3, 0.0, seconds), ('wind_loop', 0.1, 0.0, seconds)]


def boss_battle(seconds=45.0):
    """A big-gun boss: the 406 mm salvo with its warning whistles, the super weapon with its own, 500 kg bombs, a Smerch
    salvo, over a normal fight's small arms and tank guns."""
    m, events, loops = normal_battle(seconds)
    m.rng = np.random.default_rng(12)
    rng = np.random.default_rng(202)
    boss = (0.0, -150.0)
    for t in (5.0, 17.0, 29.0, 38.0):
        for k in range(3):
            events.append((t + k * 0.35, 'shot', 'shot_s406', boss, 6, True))
            tgt = field(rng, 70, 35)
            events.append((t + 3.0 + k * 0.35, 'whistle_big', tgt))
            events.append((t + 4.5 + k * 0.35, 'blast', 'blast_he_s406', tgt, 6, True))
    events.append((24.0, 'shot', 'shot_super', boss, 7, True))
    events.append((26.5, 'whistle_big', (10.0, 5.0)))
    events.append((28.0, 'blast', 'blast_super', (10.0, 5.0), 7, True))
    for t in (11.0, 12.0, 33.0):
        events.append((t, 'blast', 'blast_bomb', field(rng, 80, 40), 5))
    for k in range(6):
        events.append((14.0 + k * 0.4, 'shot', 'launch_big', (-130.0, 60.0), 6))
        events.append((14.0 + k * 0.4, 'incoming', (0.0, 0.0), 6.0))
        events.append((20.0 + k * 0.4, 'blast', 'blast_he_s406', field(rng, 90, 45), 6))
    events.append((36.0, 'wreck', 'wreck_aircraft', (-30.0, 25.0)))
    return m, events, loops + [('rotor_loop', 0.15, 8.0, 30.0)]


def crowded_battle(seconds=40.0):
    """Forty a side: dense small arms (clusters), a dozen autocannons hammering armour (the metal cap), tank guns, mortars
    and howitzers landing all round, wrecks: the voice limit and the priorities at work."""
    m = Mixer(seconds, seed=13)
    rng = np.random.default_rng(303)
    events = []
    for g in range(30):
        at = field(rng, 100, 50)
        rate = float(rng.choice([9.0, 12.0, 16.0]))
        t = rng.uniform(0, 3)
        while t < seconds - 1:
            for k in range(int(rng.integers(5, 14))):
                events.append((tick(t + k / rate), 'gun', f'mg{g}', at, 0, rate, 'shot_s0'))
                if rng.random() < 0.4:
                    events.append((t + k * 0.08 + 0.25, 'hit', field(rng, 100, 50), 0, 'ground'))
            t += rng.uniform(0.8, 2.5)
    for g in range(3):  # gatlings (the GAU-8, the GSh-6-23: 55-60 rounds a second) in bursts
        at = field(rng, 100, 50)
        t = rng.uniform(1, 6)
        while t < seconds - 2:
            for k in range(int(rng.integers(20, 45))):
                events.append((tick(t + k / 60.0), 'gun', f'gau{g}', at, 1, 60.0, 'shot_s1'))
            t += rng.uniform(3, 6)
    for g in range(12):
        at = field(rng, 100, 50)
        t = rng.uniform(0, 4)
        while t < seconds - 2:
            for k in range(int(rng.integers(4, 8))):
                events.append((tick(t + k * 0.15), 'gun', f'ac{g}', at, 1, 6.7, 'shot_s1'))
                events.append((t + k * 0.15 + 0.35, 'hit', field(rng, 100, 50), 1, rng.choice(['metal', 'metal', 'pierced', 'ground'])))
            t += rng.uniform(2, 4)
    for _ in range(10):
        at = field(rng, 110, 55)
        t = rng.uniform(0, 5)
        while t < seconds - 2:
            events.append((t, 'shot', 'shot_s3', at, 3))
            events.append((t + 0.3, 'hit', field(rng, 110, 55), 3, rng.choice(['pierced', 'pierced', 'metal', 'ground', 'concrete'])))
            t += rng.uniform(4, 8)
    t = 2.0
    while t < seconds - 2:
        size = int(rng.choice([2, 2, 3, 3, 4]))
        bank = {2: 'blast_he_s2', 3: 'blast_he_s3', 4: 'blast_he_s4'}[size]
        events.append((t, 'blast', bank, field(rng, 110, 55), size))
        t += rng.uniform(0.4, 1.4)
    for t in np.arange(6.0, seconds - 3, 4.5):
        events.append((float(t), 'wreck', str(rng.choice(['wreck_tank', 'wreck_wheeled', 'wreck_truck'])), field(rng, 90, 45)))
    return m, events, [('engine_tracked', 0.3, 0.0, seconds), ('engine_heavy', 0.2, 0.0, seconds), ('wind_loop', 0.08, 0.0, seconds)]


def run(mixer: Mixer, events, loops):
    events = sorted(events, key=lambda e: e[0])
    for e in events:
        t, kind = e[0], e[1]
        if kind == 'gun':
            mixer.gun(t, e[2], e[3], e[4], e[5], e[6])
        elif kind == 'incoming':
            mixer.incoming(t, e[2], e[3])
        elif kind == 'shot':
            bank, at, size = e[2], e[3], e[4]
            boss = len(e) > 5 and e[5]
            mixer.play(t, bank, at, mixer.priority(size, boss, False, at), 12 * size)
        elif kind == 'hit':
            mixer.hit(t, e[2], e[3], e[4])
        elif kind == 'blast':
            bank, at, size = e[2], e[3], e[4]
            boss = len(e) > 5 and e[5]
            mixer.play(t, bank, at, mixer.priority(size, boss, True, at), 12 * size)
        elif kind == 'wreck':
            mixer.play(t, e[2], e[3], P['near_blast'] if mixer.near(e[3]) else P['far_blast'], 30)
        elif kind == 'whistle':
            mixer.play(t, 'warn_whistle', e[2], P['warning'])
        elif kind == 'whistle_big':
            mixer.play(t, 'warn_whistle_big', e[2], P['warning'])
        elif kind == 'flare':
            mixer.play(t, 'flare_pop', e[2], P['near_shot'], 10)
    return mixer.render(loops)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--wav', action='store_true', help='write .wav (16-bit) instead of .ogg')
    args = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    report = {}
    for name, build in (('normal_battle', normal_battle), ('boss_battle', boss_battle), ('crowded_battle', crowded_battle)):
        mixer, events, loops = build()
        out = run(mixer, events, loops)
        path = OUT / f'{name}.{"wav" if args.wav else "ogg"}'
        if args.wav:
            sf.write(str(path), out.astype(np.float32), SR, subtype='PCM_16')
        else:
            with sf.SoundFile(str(path), 'w', SR, 2, format='OGG', subtype='VORBIS') as f:
                for i in range(0, len(out), 8192):
                    f.write(out[i:i + 8192].astype(np.float32))
        lufs, mmax = az.loudness(out.mean(axis=1), SR)
        mixer.stats.update({'seconds': round(len(out) / SR, 1), 'lufs': round(lufs, 1), 'lufs_mmax': round(mmax, 1),
                            'peak_db': round(20 * math.log10(float(np.max(np.abs(out))) or 1e-9), 1),
                            'sub150': round(az.sub_share(out.mean(axis=1), SR), 1)})
        report[name] = mixer.stats
        print(f'WROTE {path.relative_to(ROOT).as_posix()}: {mixer.stats}')
    (OUT / 'mixes.json').write_text(json.dumps(report, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
