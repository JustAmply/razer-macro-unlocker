namespace RazerMacroUnlocker.Core;

public enum ActionKind { Desktop, OpenPath, OpenUrl, Shortcut }

public sealed record HotkeyBinding
{
    public Guid Id { get; init; } = Guid.NewGuid();
    public string Label { get; init; } = "New key";
    public bool Enabled { get; init; } = true;
    public int KeyCode { get; init; } = 0x7C;
    public int Modifiers { get; init; }
    public ActionKind Action { get; init; } = ActionKind.Desktop;
    public int Desktop { get; init; } = 1;
    public string Target { get; init; } = "";
    public string Arguments { get; init; } = "";
    public int OutputKeyCode { get; init; } = 0x41;
    public int OutputModifiers { get; init; } = 2;
}

public sealed record AppSettings
{
    public int Version { get; init; } = 1;
    public bool StartWithWindows { get; init; }
    public bool ShowTrayIcon { get; init; }
    public List<HotkeyBinding> Bindings { get; init; } = Enumerable.Range(1, 5)
        .Select(i => new HotkeyBinding { Label = $"M{i}", KeyCode = 0x7B + i, Desktop = i }).ToList();

    public AppSettings Copy() => this with { Bindings = Bindings.Select(b => b with { }).ToList() };
}

