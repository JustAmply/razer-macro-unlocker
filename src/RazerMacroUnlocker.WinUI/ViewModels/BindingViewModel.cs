using System.ComponentModel;
using System.Runtime.CompilerServices;
using RazerMacroUnlocker.Core;
using Microsoft.UI.Xaml;

namespace RazerMacroUnlocker.WinUI.ViewModels;

public sealed record OutputKeyOption(int Code, string Name);

public sealed class BindingViewModel : INotifyPropertyChanged
{
    private static readonly ActionKind[] ActionOrder = [ActionKind.Shortcut, ActionKind.Desktop, ActionKind.OpenPath, ActionKind.OpenUrl];
    private readonly HotkeyBinding original;
    private bool enabled;
    private ActionKind action;
    private double desktop;
    private string target;
    private string arguments;
    private OutputKeyOption outputKey;
    private bool outputCtrl;
    private bool outputAlt;
    private bool outputShift;
    private bool outputWin;

    public BindingViewModel(HotkeyBinding binding)
    {
        if (binding.Action != ActionKind.Shortcut)
            binding = binding with { OutputKeyCode = binding.KeyCode, OutputModifiers = binding.Modifiers };
        original = binding;
        enabled = binding.Enabled;
        action = binding.Action;
        desktop = binding.Desktop;
        target = binding.Target;
        arguments = binding.Arguments;
        outputKey = OutputKeys.FirstOrDefault(k => k.Code == binding.OutputKeyCode)
            ?? new OutputKeyOption(binding.OutputKeyCode, $"Key {binding.OutputKeyCode}");
        outputCtrl = (binding.OutputModifiers & 2) != 0;
        outputAlt = (binding.OutputModifiers & 1) != 0;
        outputShift = (binding.OutputModifiers & 4) != 0;
        outputWin = (binding.OutputModifiers & 8) != 0;
    }

    public static IReadOnlyList<string> Actions { get; } = ["Keyboard shortcut", "Desktop", "App or folder", "Website"];
    public static IReadOnlyList<OutputKeyOption> OutputKeys { get; } =
        Enumerable.Range(13, 12).Select(number => new OutputKeyOption(0x6F + number, $"F{number}"))
            .Concat(Enumerable.Range('A', 26).Select(code => new OutputKeyOption(code, ((char)code).ToString())))
            .Concat(Enumerable.Range('0', 10).Select(code => new OutputKeyOption(code, ((char)code).ToString())))
            .Concat(Enumerable.Range(1, 12).Select(number => new OutputKeyOption(0x6F + number, $"F{number}")))
            .Concat(new[]
            {
                new OutputKeyOption(0x0D, "Enter"), new OutputKeyOption(0x20, "Space"),
                new OutputKeyOption(0x09, "Tab"), new OutputKeyOption(0x1B, "Esc"),
                new OutputKeyOption(0x08, "Backspace"), new OutputKeyOption(0x2E, "Delete"),
                new OutputKeyOption(0x25, "Left"), new OutputKeyOption(0x26, "Up"),
                new OutputKeyOption(0x27, "Right"), new OutputKeyOption(0x28, "Down"),
                new OutputKeyOption(0x24, "Home"), new OutputKeyOption(0x23, "End"),
                new OutputKeyOption(0x21, "Page Up"), new OutputKeyOption(0x22, "Page Down")
            }).ToArray();

    public int InputKeyCode => original.KeyCode;
    public string InputName => original.KeyCode is >= 0x7C and <= 0x87 ? $"M{original.KeyCode - 0x7B}" : original.Label;
    public bool Enabled { get => enabled; set => Set(ref enabled, value); }
    public int ActionIndex
    {
        get => Array.IndexOf(ActionOrder, action);
        set { if (value >= 0 && value < ActionOrder.Length) Set(ref action, ActionOrder[value]); }
    }
    public double Desktop { get => desktop; set => Set(ref desktop, value); }
    public string Target { get => target; set => Set(ref target, value); }
    public string Arguments { get => arguments; set => Set(ref arguments, value); }
    public OutputKeyOption OutputKey { get => outputKey; set { if (value is not null) Set(ref outputKey, value); } }
    public bool OutputCtrl { get => outputCtrl; set => Set(ref outputCtrl, value); }
    public bool OutputAlt { get => outputAlt; set => Set(ref outputAlt, value); }
    public bool OutputShift { get => outputShift; set => Set(ref outputShift, value); }
    public bool OutputWin { get => outputWin; set => Set(ref outputWin, value); }
    public Visibility ShortcutVisibility => action == ActionKind.Shortcut ? Visibility.Visible : Visibility.Collapsed;
    public Visibility DesktopVisibility => action == ActionKind.Desktop ? Visibility.Visible : Visibility.Collapsed;
    public Visibility TargetVisibility => action is ActionKind.OpenPath or ActionKind.OpenUrl ? Visibility.Visible : Visibility.Collapsed;
    public Visibility PathVisibility => action == ActionKind.OpenPath ? Visibility.Visible : Visibility.Collapsed;
    public string TargetLabel => action == ActionKind.OpenUrl ? "URL" : "Path";
    public string TargetPlaceholder => action == ActionKind.OpenUrl ? "https://example.com" : "Choose an app, file or folder";
    public string Summary => !Enabled ? "Disabled" : action switch
    {
        ActionKind.Desktop => $"Desktop {Desktop:0}",
        ActionKind.OpenPath => string.IsNullOrWhiteSpace(Target) ? "App or folder" : Path.GetFileName(Target.TrimEnd('\\', '/')),
        ActionKind.OpenUrl => string.IsNullOrWhiteSpace(Target) ? "Website" : Target,
        _ => string.Join(" + ", new[] { OutputCtrl ? "Ctrl" : null, OutputAlt ? "Alt" : null, OutputShift ? "Shift" : null, OutputWin ? "Win" : null, OutputKey.Name }.Where(s => s is not null))
    };

    public HotkeyBinding ToBinding() => original with
    {
        Enabled = Enabled, Action = action,
        Desktop = double.IsFinite(Desktop) ? (int)Desktop : 0,
        Target = Target.Trim(), Arguments = Arguments,
        OutputKeyCode = OutputKey.Code,
        OutputModifiers = (OutputAlt ? 1 : 0) | (OutputCtrl ? 2 : 0) | (OutputShift ? 4 : 0) | (OutputWin ? 8 : 0)
    };

    public event PropertyChangedEventHandler? PropertyChanged;
    public event Action? Edited;

    private void Set<T>(ref T field, T value, [CallerMemberName] string? name = null)
    {
        if (EqualityComparer<T>.Default.Equals(field, value)) return;
        field = value;
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
        foreach (var dependent in new[] { nameof(Summary), nameof(ShortcutVisibility), nameof(DesktopVisibility), nameof(TargetVisibility), nameof(PathVisibility), nameof(TargetLabel), nameof(TargetPlaceholder) })
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(dependent));
        Edited?.Invoke();
    }
}
