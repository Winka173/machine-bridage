"""Machine Brigade procedural music toolkit.

Everything in this package is original code written for the game. The pieces
are composed in Python (see ``mbmusic/tracks``), rendered offline through
FluidSynth with the MIT-licensed FluidR3_GM SoundFont plus numpy synth layers,
then mixed, looped and mastered with numpy/scipy. Nothing here ships with the
game except the rendered .ogg files.
"""

SR = 44100
