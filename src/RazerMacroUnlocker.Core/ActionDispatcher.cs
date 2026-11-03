using System.Diagnostics;

namespace RazerMacroUnlocker.Core;

public interface IDesktopService
{
    int Count { get; }
    int Current { get; }
    void Switch(int number);
}

public interface IShortcutService
{
    void Send(int keyCode, int modifiers);
}

public sealed class ActionDispatcher(IDesktopService desktops, IShortcutService shortcuts)
{
    // Each action has one responsibility; new actions do not alter hotkey capture.
    public string Execute(HotkeyBinding binding)
    {
        SettingsValidator.ValidateBinding(binding);
        if (!binding.Enabled) return $"{binding.Label} is disabled.";
        switch (binding.Action)
        {
            case ActionKind.Desktop:
                desktops.Switch(binding.Desktop);
                return $"{binding.Label} → Desktop {binding.Desktop}";
            case ActionKind.OpenPath:
                if (!File.Exists(binding.Target) && !Directory.Exists(binding.Target))
                    throw new InvalidOperationException($"The target no longer exists: {binding.Target}");
                Process.Start(new ProcessStartInfo(binding.Target)
                {
                    UseShellExecute = true,
                    Arguments = binding.Arguments
                });
                return $"{binding.Label} → Opened {Path.GetFileName(binding.Target)}";
            case ActionKind.OpenUrl:
                Process.Start(new ProcessStartInfo(binding.Target) { UseShellExecute = true });
                return $"{binding.Label} → Website opened";
            case ActionKind.Shortcut:
                if (binding.IsPassthrough) return $"Native F{binding.KeyCode - 0x6F}";
                shortcuts.Send(binding.OutputKeyCode, binding.OutputModifiers);
                return $"{binding.Label} → Shortcut sent";
            default:
                throw new InvalidOperationException("Unknown action type.");
        }
    }
}
