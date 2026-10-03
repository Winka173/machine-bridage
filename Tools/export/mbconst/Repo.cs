using System.Diagnostics;
using System.Formats.Tar;
using System.Text;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;

namespace MbConst;

/// <summary>The repository: its root, git, and the C# sources of a revision or of the working tree.</summary>
internal static class Repo
{
    public const string Scripts = "Assets/MachineBrigade/Scripts";
    public const string TunablesJson = "Assets/MachineBrigade/Resources/Data/tunables.json";
    public const string ContentDir = Scripts + "/Sim/Content";

    private static string? _root;

    public static string Root
    {
        get
        {
            if (_root != null) return _root;
            var dir = new DirectoryInfo(Directory.GetCurrentDirectory());
            while (dir != null && !Directory.Exists(Path.Combine(dir.FullName, ".git")) && !File.Exists(Path.Combine(dir.FullName, ".git")))
                dir = dir.Parent;
            _root = (dir ?? throw new InvalidOperationException("not inside a git repository")).FullName.Replace('\\', '/');
            return _root;
        }
        set => _root = value.Replace('\\', '/');
    }

    public static string Abs(string rel) => Path.Combine(Root, rel).Replace('\\', '/');

    /// <summary>Repo-relative path with forward slashes; accepts a path relative to Scripts/ too.</summary>
    public static string Rel(string path)
    {
        var p = path.Replace('\\', '/');
        if (Path.IsPathRooted(p))
        {
            var full = Path.GetFullPath(p).Replace('\\', '/');
            if (full.StartsWith(Root + "/", StringComparison.OrdinalIgnoreCase)) return full[(Root.Length + 1)..];
            return full;
        }
        if (p.StartsWith("Sim/") || p.StartsWith("Game/") || p.StartsWith("Editor/")) return Scripts + "/" + p;
        return p;
    }

    /// <summary>Path under Scripts/ (Sim/..., Game/...), the form the reports use.</summary>
    public static string Short(string rel) => rel.StartsWith(Scripts + "/") ? rel[(Scripts.Length + 1)..] : rel;

    public static string Git(params string[] args) => Encoding.UTF8.GetString(GitBytes(args));

    public static byte[] GitBytes(params string[] args)
    {
        var psi = new ProcessStartInfo("git") { RedirectStandardOutput = true, RedirectStandardError = true, WorkingDirectory = Root };
        foreach (var a in args) psi.ArgumentList.Add(a);
        using var p = Process.Start(psi)!;
        using var ms = new MemoryStream();
        var errTask = p.StandardError.ReadToEndAsync();
        p.StandardOutput.BaseStream.CopyTo(ms);
        p.WaitForExit();
        if (p.ExitCode != 0) throw new InvalidOperationException("git " + string.Join(' ', args) + ": " + errTask.Result.Trim());
        return ms.ToArray();
    }

    public static string? GitOrNull(params string[] args)
    {
        try { return Git(args); } catch { return null; }
    }

    public static string ReadText(string rel) => DecodeText(File.ReadAllBytes(Abs(rel)), out _);

    public static string DecodeText(byte[] bytes, out bool bom)
    {
        bom = bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF;
        return bom ? Encoding.UTF8.GetString(bytes, 3, bytes.Length - 3) : Encoding.UTF8.GetString(bytes);
    }

    /// <summary>Writes text keeping the file's byte-order mark (UTF-8, no BOM for a new file).</summary>
    public static void WriteText(string rel, string text)
    {
        var abs = Abs(rel);
        var bom = false;
        if (File.Exists(abs)) DecodeText(File.ReadAllBytes(abs), out bom);
        Directory.CreateDirectory(Path.GetDirectoryName(abs)!);
        File.WriteAllBytes(abs, (bom ? new byte[] { 0xEF, 0xBB, 0xBF } : Array.Empty<byte>()).Concat(Encoding.UTF8.GetBytes(text)).ToArray());
    }
}

/// <summary>The C# files (and tunables.json) of one tree: the working tree or a git revision.</summary>
internal sealed class SourceSet
{
    public readonly string Name;
    public readonly Dictionary<string, string> Files = new(StringComparer.Ordinal); // repo-relative path -> text
    public string? TunablesJson;

    private SourceSet(string name) => Name = name;

    public static SourceSet Load(string rev) => rev is "" or "WORKTREE" or "worktree" ? FromWorktree() : FromRevision(rev);

    public static SourceSet FromWorktree()
    {
        var s = new SourceSet("WORKTREE");
        foreach (var f in Directory.EnumerateFiles(Repo.Abs(Repo.Scripts), "*.cs", SearchOption.AllDirectories))
        {
            var rel = Repo.Rel(f);
            s.Files[rel] = Repo.ReadText(rel);
        }
        if (File.Exists(Repo.Abs(Repo.TunablesJson))) s.TunablesJson = Repo.ReadText(Repo.TunablesJson);
        return s;
    }

    public static SourceSet FromRevision(string rev)
    {
        var s = new SourceSet(rev);
        var tar = Repo.GitBytes("archive", "--format=tar", rev, Repo.Scripts);
        using (var reader = new TarReader(new MemoryStream(tar)))
        {
            TarEntry? e;
            while ((e = reader.GetNextEntry()) != null)
            {
                if (e.EntryType is not (TarEntryType.RegularFile or TarEntryType.V7RegularFile) || !e.Name.EndsWith(".cs") || e.DataStream == null) continue;
                using var ms = new MemoryStream();
                e.DataStream.CopyTo(ms);
                s.Files[e.Name] = Repo.DecodeText(ms.ToArray(), out _);
            }
        }
        s.TunablesJson = Repo.GitOrNull("show", rev + ":" + Repo.TunablesJson);
        return s;
    }
}

/// <summary>Builds the Sim and Game compilations the way lane B's .NET SDK compile checks did (C# 9, Unity 6 DLLs).</summary>
internal static class Compiler
{
    public static string UnityEditor = "C:/Program Files/Unity/Hub/Editor/6000.6.3f1/Editor/Data/Managed/UnityEngine";
    public static string ScriptAssemblies = "C:/Users/Winka/Projects/MachineBrigade/Library/ScriptAssemblies";

    public static readonly string[] GameDefines =
        { "UNITY_EDITOR", "UNITY_6000_0_OR_NEWER", "UNITY_2021_3_OR_NEWER", "UNITY_2022_3_OR_NEWER", "UNITY_2023_1_OR_NEWER", "UNITY_STANDALONE_WIN", "UNITY_STANDALONE", "ENABLE_INPUT_SYSTEM" };

    // lane B's NoWarn lists (documentation and Unity-serialisation noise)
    private static readonly string[] SimNoWarn = { "CS8632", "CS1591", "CS0067", "CS1574", "CS1584", "CS1580", "CS1572", "CS1573", "CS1587" };
    private static readonly string[] GameNoWarn = SimNoWarn.Concat(new[] { "CS0618", "CS0649", "CS0414", "CS0169", "CS1701", "CS1702" }).ToArray();

    public static CSharpParseOptions SimParse => new(LanguageVersion.CSharp9, DocumentationMode.Parse);
    public static CSharpParseOptions GameParse => new(LanguageVersion.CSharp9, DocumentationMode.Parse, preprocessorSymbols: GameDefines);

    private static List<MetadataReference>? _netstandard, _unity;

    private static List<MetadataReference> NetStandard()
    {
        if (_netstandard != null) return _netstandard;
        var packs = Path.Combine(Path.GetDirectoryName(typeof(object).Assembly.Location)!, "..", "..", "..", "packs", "NETStandard.Library.Ref", "2.1.0", "ref", "netstandard2.1");
        packs = Path.GetFullPath(packs);
        if (!Directory.Exists(packs)) packs = "C:/Program Files/dotnet/packs/NETStandard.Library.Ref/2.1.0/ref/netstandard2.1";
        _netstandard = Directory.EnumerateFiles(packs, "*.dll").Select(f => (MetadataReference)MetadataReference.CreateFromFile(f)).ToList();
        return _netstandard;
    }

    private static List<MetadataReference> Unity()
    {
        if (_unity != null) return _unity;
        var list = new List<MetadataReference>();
        if (Directory.Exists(UnityEditor))
            list.AddRange(Directory.EnumerateFiles(UnityEditor, "*.dll").Select(f => MetadataReference.CreateFromFile(f)));
        if (Directory.Exists(ScriptAssemblies))
            foreach (var f in Directory.EnumerateFiles(ScriptAssemblies, "*.dll"))
            {
                var n = Path.GetFileName(f);
                var unityPkg = n.StartsWith("Unity.") && !n.Contains("Tests") && !n.Contains("Editor") && !n.Contains("CodeGen");
                if (unityPkg || n.StartsWith("UnityEngine.")) list.Add(MetadataReference.CreateFromFile(f));
            }
        _unity = list;
        return list;
    }

    public sealed class Pair
    {
        public CSharpCompilation Sim = null!;
        public CSharpCompilation Game = null!;
        public readonly Dictionary<string, SyntaxTree> Trees = new(StringComparer.Ordinal);

        public SemanticModel? Model(string rel)
        {
            if (!Trees.TryGetValue(rel, out var t)) return null;
            var c = rel.StartsWith(Repo.Scripts + "/Sim/") ? Sim : Game;
            return c.GetSemanticModel(t, ignoreAccessibility: true);
        }

        public IEnumerable<CSharpCompilation> Both() { yield return Sim; yield return Game; }
    }

    public static Pair Build(SourceSet s)
    {
        var p = new Pair();
        var simTrees = new List<SyntaxTree>();
        var gameTrees = new List<SyntaxTree>();
        foreach (var (rel, text) in s.Files.OrderBy(k => k.Key, StringComparer.Ordinal))
        {
            if (rel.StartsWith(Repo.Scripts + "/Sim/"))
            {
                var t = CSharpSyntaxTree.ParseText(text, SimParse, rel, Encoding.UTF8);
                simTrees.Add(t);
                p.Trees[rel] = t;
            }
            else if (rel.StartsWith(Repo.Scripts + "/Game/"))
            {
                var t = CSharpSyntaxTree.ParseText(text, GameParse, rel, Encoding.UTF8);
                gameTrees.Add(t);
                p.Trees[rel] = t;
            }
        }
        p.Sim = CSharpCompilation.Create("MachineBrigade.Sim", simTrees, NetStandard(),
            Options(SimNoWarn));
        p.Game = CSharpCompilation.Create("MachineBrigade.Game", gameTrees,
            NetStandard().Concat(Unity()).Append(p.Sim.ToMetadataReference()), Options(GameNoWarn));
        return p;
    }

    private static CSharpCompilationOptions Options(string[] noWarn) =>
        new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary, nullableContextOptions: NullableContextOptions.Disable,
                warningLevel: 4, concurrentBuild: true)
            .WithSpecificDiagnosticOptions(noWarn.Select(id => new KeyValuePair<string, ReportDiagnostic>(id, ReportDiagnostic.Suppress)));

    /// <summary>Errors and warnings of both assemblies (generated SimTunables files included).</summary>
    public static List<Diagnostic> Diagnostics(Pair p) =>
        p.Both().SelectMany(c => c.GetDiagnostics()).Where(d => d.Severity >= DiagnosticSeverity.Warning).ToList();
}
