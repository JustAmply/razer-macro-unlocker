namespace RazerMacroUnlocker.Core;

public static class SettingsValidator
{
    public static void Validate(AppSettings settings)
    {
        if (settings.Version != 1)
            throw new InvalidOperationException("This configuration version is not supported.");
        if (settings.Bindings is null || settings.Bindings.Count > 24)
            throw new InvalidOperationException("Up to 24 key assignments are supported.");
        var ids = new HashSet<Guid>();
        var keys = new HashSet<(int, int)>();
        foreach (var binding in settings.Bindings)
        {
            if (binding is null || !ids.Add(binding.Id))
                throw new InvalidOperationException("Each assignment requires a unique ID.");
            ValidateBinding(binding);
            if (binding.Enabled && !keys.Add((binding.KeyCode, binding.Modifiers)))
                throw new InvalidOperationException($"{binding.Label}: This key combination is assigned more than once.");
            if (binding.Enabled && binding.Action == ActionKind.Shortcut
                && settings.Bindings.Any(input => input is { Enabled: true } && input.KeyCode == binding.OutputKeyCode
                    && input.Modifiers == binding.OutputModifiers))
                throw new InvalidOperationException($"{binding.Label}: A shortcut cannot trigger another configured input key.");
        }
    }

    public static void ValidateBinding(HotkeyBinding binding)
    {
        if (string.IsNullOrWhiteSpace(binding.Label))
            throw new InvalidOperationException("Give each key a name.");
        if (binding.KeyCode is < 0x70 or > 0x87 || binding.KeyCode == 0x7B)
            throw new InvalidOperationException("Choose F1–F24. Windows reserves F12 for debuggers.");
        if ((binding.Modifiers & ~15) != 0)
            throw new InvalidOperationException("Invalid modifier key.");
        if (!Enum.IsDefined(binding.Action))
            throw new InvalidOperationException("Unknown action type.");
        if (!binding.Enabled) return;
        switch (binding.Action)
        {
            case ActionKind.Desktop when binding.Desktop is < 1 or > 99:
                throw new InvalidOperationException("The desktop number must be between 1 and 99.");
            case ActionKind.OpenPath when string.IsNullOrWhiteSpace(binding.Target)
                                          || !Path.IsPathFullyQualified(binding.Target):
                throw new InvalidOperationException("Choose a program, file, or folder using its full path.");
            case ActionKind.OpenUrl when !Uri.TryCreate(binding.Target, UriKind.Absolute, out var uri)
                                         || (uri.Scheme != Uri.UriSchemeHttps && uri.Scheme != Uri.UriSchemeHttp):
                throw new InvalidOperationException("Enter a complete https:// or http:// address.");
            case ActionKind.Shortcut:
                ValidateShortcut(binding.OutputKeyCode, binding.OutputModifiers);
                if (binding.KeyCode == binding.OutputKeyCode && binding.Modifiers == binding.OutputModifiers)
                    throw new InvalidOperationException("A shortcut cannot trigger its own input key.");
                break;
        }
    }

    public static void ValidateShortcut(int keyCode, int modifiers)
    {
        if ((modifiers & ~15) != 0)
            throw new InvalidOperationException("Invalid shortcut modifier.");
        if (keyCode is not (>= 0x30 and <= 0x39) and not (>= 0x41 and <= 0x5A)
            and not (>= 0x70 and <= 0x7B) and not (>= 0x21 and <= 0x28)
            and not (0x08 or 0x09 or 0x0D or 0x1B or 0x20 or 0x2D or 0x2E))
            throw new InvalidOperationException("Choose a letter, digit, F1–F12, or navigation key. Macro keys cannot be shortcut outputs.");
    }
}
