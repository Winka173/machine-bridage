namespace MbConst;

internal static class Program
{
    /// <summary>Writes the empty generated domain files the registry (SimTunables.Pack2.cs) lists, if missing.</summary>
    private static int Init()
    {
        foreach (var d in Pack2Files.Domains)
            if (!File.Exists(Repo.Abs(Pack2Files.FileOf(d)))) { Pack2Files.Write(d, new List<Pack2Files.Field>()); Console.WriteLine(Pack2Files.FileOf(d)); }
        return 0;
    }

    private static int Main(string[] args)
    {
        if (args.Length == 0)
        {
            Console.Error.WriteLine("mbconst move  --csv <moves.csv> [--dry-run]      literal -> SimTunables.<Key> (+ tunables.json)");
            Console.Error.WriteLine("mbconst check --base <rev> [--head <rev>] | --pair <b>:<h>[=label] ... [--out f] [--dotnet]");
            Console.Error.WriteLine("mbconst scan  [--out <dir>] [--lists <dir>]       pass 1: reachability, six scans, candidates");
            return 2;
        }
        var rest = args.Skip(1).ToArray();
        return args[0] switch
        {
            "move" => Move.Run(rest),
            "check" => Check.Run(rest),
            "scan" => Scan.Run(rest),
            "init" => Init(),
            _ => 2,
        };
    }
}

internal static partial class Scan
{
    public static int Run(string[] args) => 0;
}
