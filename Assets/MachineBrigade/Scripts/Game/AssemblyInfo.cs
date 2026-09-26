using System.Runtime.CompilerServices;

// Tests drive effects and views directly (for example a blast played into a scene), and editor
// tools render them (EffectShots).
[assembly: InternalsVisibleTo("MachineBrigade.Tests.EditMode")]
[assembly: InternalsVisibleTo("MachineBrigade.Editor")]
