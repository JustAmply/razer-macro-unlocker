using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Text.Json;
using RazerMacroUnlocker.Core;
using RazerMacroUnlocker.Windows;

namespace RazerMacroUnlocker.Tests;

internal static class Program
{
    [STAThread]
    private static int Main(string[] args)
    {
        var tests = new (string Name, Action Run)[]
        {
            ("Settings round-trip preserves actions and preferences", SettingsRoundTrip),
            ("Invalid save preserves the previous configuration", InvalidSavePreservesConfiguration),
            ("Unsupported configuration does not overwrite the source", UnsupportedConfiguration),
            ("Malformed configuration is reported without data loss", MalformedConfiguration),
            ("Missing launch target does not prevent loading settings", MissingTargetLoads),
            ("Missing launch target fails at execution", MissingTargetExecution),
            ("Duplicate active combinations are rejected", DuplicateHotkeys),
            ("Disabled and modifier-distinct combinations coexist", DistinctHotkeys),
            ("Reserved F12 and unsupported modifiers are rejected", ReservedHotkeys),
            ("Registration failure restores the previous mapping", RegistrationRollback),
            ("Rollback failure releases every registered hotkey", FailedRollbackCleanup),
            ("Replacing mappings releases obsolete and disabled hotkeys", ReplaceBindings),
            ("Desktop actions use one-based target positions", DesktopDispatch),
            ("Disabled actions never invoke their target", DisabledDispatch),
            ("Shortcut actions dispatch the configured chord", ShortcutDispatch),
            ("Disabled shortcuts do not send keys", DisabledShortcutDispatch),
            ("Remapped shortcuts cannot trigger intercepted inputs", ShortcutRecursion),
            ("Native macro defaults do not register or synthesize input", NativeMacroDefaults),
            ("F24 outputs and native pass-through targets are supported", ExtendedShortcutOutputs),
            ("Shortcut settings round-trip and legacy defaults survive", ShortcutPersistence),
            ("Shortcut inputs match the x64 ABI and reverse release order", ShortcutInputLayout),
            ("IPC requests run on the owning thread", RuntimeServerTests.RequestRunsOnOwnerThread),
            ("IPC recovers after malformed input and handler failures", RuntimeServerTests.MalformedRequestAndHandlerErrorRecover),
            ("IPC recovers after a client disconnect", RuntimeServerTests.DisconnectedClientDoesNotStopListener),
            ("IPC idle cancellation completes without faulting", RuntimeServerTests.IdleCancellationCompletesCleanly),
            ("IPC listener creation failure reports once", RuntimeServerTests.ListenerFailureReportsOnce)
        };
        var failures = 0;
        foreach (var test in tests)
        {
            try
            {
                test.Run();
                Console.WriteLine($"PASS {test.Name}");
            }
            catch (Exception error)
            {
                failures++;
                Console.Error.WriteLine($"FAIL {test.Name}: {error}");
            }
        }
        if (args.Contains("--integration"))
        {
            try
            {
                Integration();
                Console.WriteLine("PASS interactive Windows API checks (no desktop changes)");
            }
            catch (Exception error)
            {
                failures++;
                Console.Error.WriteLine($"FAIL interactive Windows API checks: {error}");
            }
        }
        Console.WriteLine($"{tests.Length} regression checks, {failures} failures.");
        return failures == 0 ? 0 : 1;
    }

    private static void SettingsRoundTrip() => InTemporaryDirectory(directory =>
    {
        var store = new SettingsStore(Path.Combine(directory, "nested", "settings.json"));
        var target = Path.Combine(directory, "example.txt");
        File.WriteAllText(target, "fixture");
        var expected = new AppSettings
        {
            StartWithWindows = true,
            ShowTrayIcon = true,
            Bindings =
            [
                new() { Label = "M1", Desktop = 5 },
                new() { Label = "Website", KeyCode = 0x7D, Modifiers = 3,
                    Action = ActionKind.OpenUrl, Target = "https://example.com/docs" },
                new() { Label = "File", KeyCode = 0x7E, Action = ActionKind.OpenPath,
                    Target = target, Arguments = "--example \"two words\"" },
                new() { Label = "Paused", KeyCode = 0x7F, Enabled = false }
            ]
        };
        store.Save(expected);
        var actual = store.Load();
        Equal(expected.StartWithWindows, actual.StartWithWindows);
        Equal(expected.ShowTrayIcon, actual.ShowTrayIcon);
        SequenceEqual(expected.Bindings, actual.Bindings);
        Assert(!File.Exists(store.FilePath + ".tmp"), "Temporary save file was left behind.");
    });

    private static void InvalidSavePreservesConfiguration() => InTemporaryDirectory(directory =>
    {
        var store = new SettingsStore(Path.Combine(directory, "settings.json"));
        store.Save(new AppSettings());
        var original = File.ReadAllBytes(store.FilePath);
        Throws<InvalidOperationException>(() => store.Save(new AppSettings { Version = 99 }));
        SequenceEqual(original, File.ReadAllBytes(store.FilePath));
    });

    private static void UnsupportedConfiguration() => InTemporaryDirectory(directory =>
    {
        var path = Path.Combine(directory, "settings.json");
        const string content = "{\"Version\":42,\"Bindings\":[]}";
        File.WriteAllText(path, content);
        Throws<InvalidOperationException>(() => new SettingsStore(path).Load());
        Equal(content, File.ReadAllText(path));
    });

    private static void MalformedConfiguration() => InTemporaryDirectory(directory =>
    {
        var path = Path.Combine(directory, "settings.json");
        const string content = "{broken";
        File.WriteAllText(path, content);
        Throws<JsonException>(() => new SettingsStore(path).Load());
        Equal(content, File.ReadAllText(path));
    });

    private static void DuplicateHotkeys()
    {
        var settings = new AppSettings { Bindings = [new(), new()] };
        Throws<InvalidOperationException>(() => SettingsValidator.Validate(settings));
    }

    private static void MissingTargetLoads() => InTemporaryDirectory(directory =>
    {
        var store = new SettingsStore(Path.Combine(directory, "settings.json"));
        var target = Path.Combine(directory, "removed.exe");
        File.WriteAllText(target, "fixture");
        var binding = new HotkeyBinding { Action = ActionKind.OpenPath, Target = target };
        store.Save(new AppSettings { Bindings = [binding] });
        File.Delete(target);
        Equal(binding, store.Load().Bindings.Single());
    });

    private static void MissingTargetExecution() => InTemporaryDirectory(directory =>
    {
        var binding = new HotkeyBinding
        {
            Action = ActionKind.OpenPath,
            Target = Path.Combine(directory, "missing.exe")
        };
        Throws<InvalidOperationException>(() => new ActionDispatcher(new FakeDesktops(), new FakeShortcuts()).Execute(binding));
    });

    private static void DistinctHotkeys()
    {
        SettingsValidator.Validate(new AppSettings
        {
            Bindings = [new(), new() { Enabled = false }, new() { Modifiers = 2 }]
        });
    }

    private static void ReservedHotkeys()
    {
        Throws<InvalidOperationException>(() => SettingsValidator.ValidateBinding(new() { KeyCode = 0x7B }));
        Throws<InvalidOperationException>(() => SettingsValidator.ValidateBinding(new() { Modifiers = 0x4000 }));
    }

    private static void RegistrationRollback()
    {
        var backend = new FakeBackend();
        using var registry = new HotkeyRegistry(backend);
        var original = new AppSettings().Bindings.Take(2).Select(binding => binding with { Action = ActionKind.Desktop }).ToArray();
        registry.Apply(original);
        backend.FailWhen = key => key == 0x87;
        Throws<InvalidOperationException>(() => registry.Apply(
            [new() { KeyCode = 0x86 }, new() { KeyCode = 0x87 }]));
        Equal(2, registry.Count);
        Equal(original[0], registry.Find(1));
        Equal(original[1], registry.Find(2));
        Equal(0x7C, backend.Active[1].Key);
        Equal(0x7D, backend.Active[2].Key);
        Assert(backend.Unregistered.Contains((1, 0x86)), "Partially installed mapping was not released.");
    }

    private static void FailedRollbackCleanup()
    {
        var backend = new FakeBackend();
        using var registry = new HotkeyRegistry(backend);
        registry.Apply(new AppSettings().Bindings.Take(2).Select(binding => binding with { Action = ActionKind.Desktop }));
        backend.FailWhen = key => key is 0x87 or 0x7D;
        var error = Throws<AggregateException>(() => registry.Apply(
            [new() { KeyCode = 0x86 }, new() { KeyCode = 0x87 }]));
        Equal(2, error.InnerExceptions.Count);
        Equal(0, registry.Count);
        Equal(0, backend.Active.Count);
    }

    private static void ReplaceBindings()
    {
        var backend = new FakeBackend();
        var registry = new HotkeyRegistry(backend);
        registry.Apply(new AppSettings().Bindings.Select(binding => binding with { Action = ActionKind.Desktop }));
        var replacement = new HotkeyBinding { KeyCode = 0x87 };
        registry.Apply([replacement, new() { KeyCode = 0x86, Enabled = false }]);
        Equal(1, registry.Count);
        Equal(replacement, registry.Find(1));
        Equal(1, backend.Active.Count);
        registry.Dispose();
        Equal(0, backend.Active.Count);
        Equal(0, registry.Count);
    }

    private static void DesktopDispatch()
    {
        var desktops = new FakeDesktops();
        var dispatcher = new ActionDispatcher(desktops, new FakeShortcuts());
        dispatcher.Execute(new HotkeyBinding { Desktop = 5 });
        SequenceEqual(new[] { 5 }, desktops.Switches);
    }

    private static void DisabledDispatch()
    {
        var desktops = new FakeDesktops();
        new ActionDispatcher(desktops, new FakeShortcuts()).Execute(new HotkeyBinding { Enabled = false, Desktop = 5 });
        Equal(0, desktops.Switches.Count);
    }

    private static void ShortcutDispatch()
    {
        var shortcuts = new FakeShortcuts();
        new ActionDispatcher(new FakeDesktops(), shortcuts).Execute(new HotkeyBinding
        {
            Action = ActionKind.Shortcut, OutputKeyCode = 0x53, OutputModifiers = 6
        });
        SequenceEqual(new[] { (0x53, 6) }, shortcuts.Sent);
        SettingsValidator.ValidateShortcut(0x7B, 8); // F12 is valid as output, unlike global input.
    }

    private static void DisabledShortcutDispatch()
    {
        var shortcuts = new FakeShortcuts();
        var binding = new HotkeyBinding { Action = ActionKind.Shortcut };
        new ActionDispatcher(new FakeDesktops(), shortcuts).Execute(binding with { Enabled = false });
        Equal(0, shortcuts.Sent.Count);
    }

    private static void ShortcutRecursion()
    {
        for (var key = 0x7C; key <= 0x87; key++)
            SettingsValidator.ValidateShortcut(key, 0);
        Throws<InvalidOperationException>(() => SettingsValidator.ValidateShortcut(0x41, 16));
        Throws<InvalidOperationException>(() => SettingsValidator.ValidateShortcut(0x10, 0));
        SettingsValidator.ValidateBinding(new HotkeyBinding
        {
            KeyCode = 0x70, Modifiers = 2, Action = ActionKind.Shortcut,
            OutputKeyCode = 0x70, OutputModifiers = 2
        });
        Throws<InvalidOperationException>(() => SettingsValidator.Validate(new AppSettings
        {
            Bindings =
            [
                new() { KeyCode = 0x70, Modifiers = 2 },
                new() { Action = ActionKind.Shortcut, OutputKeyCode = 0x70, OutputModifiers = 2 }
            ]
        }));
    }

    private static void NativeMacroDefaults()
    {
        var settings = new AppSettings();
        SettingsValidator.Validate(settings);
        SequenceEqual(Enumerable.Range(0x7C, 5), settings.Bindings.Select(binding => binding.OutputKeyCode));
        Assert(settings.Bindings.All(binding => binding.IsPassthrough), "Defaults must preserve hardware signals.");
        var backend = new FakeBackend();
        using var registry = new HotkeyRegistry(backend);
        registry.Apply(settings.Bindings);
        Equal(0, registry.Count);
        Equal(0, backend.Active.Count);
        var shortcuts = new FakeShortcuts();
        var dispatcher = new ActionDispatcher(new FakeDesktops(), shortcuts);
        Equal("Native F13", dispatcher.Execute(settings.Bindings[0]));
        Equal(0, shortcuts.Sent.Count);
        var json = JsonSerializer.Serialize(settings);
        Assert(!json.Contains("IsPassthrough"), "Derived pass-through state must not be persisted.");
    }

    private static void ExtendedShortcutOutputs()
    {
        var nativeTarget = new HotkeyBinding
        {
            KeyCode = 0x7D, Action = ActionKind.Shortcut,
            OutputKeyCode = 0x7D, OutputModifiers = 0
        };
        var remapped = new HotkeyBinding
        {
            Action = ActionKind.Shortcut, OutputKeyCode = 0x7D, OutputModifiers = 0
        };
        SettingsValidator.Validate(new AppSettings { Bindings = [remapped, nativeTarget] });
        var backend = new FakeBackend();
        using var registry = new HotkeyRegistry(backend);
        registry.Apply([remapped, nativeTarget]);
        Equal(1, registry.Count);
        Equal(remapped, registry.Find(1));
        var shortcuts = new FakeShortcuts();
        var dispatcher = new ActionDispatcher(new FakeDesktops(), shortcuts);
        dispatcher.Execute(remapped with { OutputKeyCode = 0x87 });
        SequenceEqual(new[] { (0x87, 0) }, shortcuts.Sent);
        Throws<InvalidOperationException>(() => SettingsValidator.Validate(new AppSettings
        {
            Bindings = [remapped, nativeTarget with { OutputKeyCode = 0x7C }]
        }));
    }

    private static void ShortcutPersistence() => InTemporaryDirectory(directory =>
    {
        var store = new SettingsStore(Path.Combine(directory, "settings.json"));
        var binding = new HotkeyBinding { Action = ActionKind.Shortcut, OutputKeyCode = 0x7B, OutputModifiers = 8 };
        store.Save(new AppSettings { Bindings = [binding] });
        Equal(binding, store.Load().Bindings.Single());
        File.WriteAllText(store.FilePath, "{\"Version\":1,\"Bindings\":[{\"Label\":\"M1\",\"Action\":0,\"Desktop\":3}]}");
        var legacy = store.Load().Bindings.Single();
        Equal(ActionKind.Desktop, legacy.Action);
        Equal(3, legacy.Desktop);
        Equal(0x41, legacy.OutputKeyCode);
        Equal(2, legacy.OutputModifiers);
    });

    private static void ShortcutInputLayout()
    {
        Equal(40, Marshal.SizeOf<ShortcutService.KeyboardInput>());
        Equal((nint)8, Marshal.OffsetOf<ShortcutService.KeyboardInput>(nameof(ShortcutService.KeyboardInput.VirtualKey)));
        Equal((nint)24, Marshal.OffsetOf<ShortcutService.KeyboardInput>(nameof(ShortcutService.KeyboardInput.ExtraInfo)));
        var inputs = ShortcutService.BuildInputs(0x27, 10);
        SequenceEqual(new ushort[] { 0x11, 0x5B, 0x27, 0x27, 0x5B, 0x11 }, inputs.Select(input => input.VirtualKey));
        SequenceEqual(new uint[] { 0, 1, 1, 3, 3, 2 }, inputs.Select(input => input.Flags));
        Assert(inputs.All(input => input.Type == 1), "Non-keyboard INPUT emitted.");
    }

    private static void Integration()
    {
        var desktops = new DesktopService();
        var count = desktops.Count;
        var current = desktops.Current;
        Assert(count > 0 && current >= 1 && current <= count, "Invalid live desktop state.");
        const int id = 0x5D31;
        if (!RegisterHotKey(0, id, 0x4000 | 1 | 2 | 4, 0x87))
            throw new Win32Exception(Marshal.GetLastWin32Error());
        try { Console.WriteLine($"Windows reports desktop {current}/{count}; Ctrl+Alt+Shift+F24 registered."); }
        finally
        {
            if (!UnregisterHotKey(0, id)) throw new Win32Exception(Marshal.GetLastWin32Error());
        }
    }

    private static void InTemporaryDirectory(Action<string> action)
    {
        var directory = Path.Combine(Path.GetTempPath(), "RazerMacroUnlocker.Tests", Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        try { action(directory); }
        finally { Directory.Delete(directory, recursive: true); }
    }

    private static void Assert(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }

    private static void Equal<T>(T expected, T actual) =>
        Assert(EqualityComparer<T>.Default.Equals(expected, actual), $"Expected {expected}, got {actual}.");

    private static void SequenceEqual<T>(IEnumerable<T> expected, IEnumerable<T> actual) =>
        Assert(expected.SequenceEqual(actual), "Sequences differ.");

    private static T Throws<T>(Action action) where T : Exception
    {
        try { action(); }
        catch (T error) { return error; }
        throw new InvalidOperationException($"Expected {typeof(T).Name}.");
    }

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool RegisterHotKey(nint window, int id, uint modifiers, uint key);
    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool UnregisterHotKey(nint window, int id);

    private sealed class FakeBackend : IHotkeyBackend
    {
        public Dictionary<int, (int Key, int Modifiers)> Active { get; } = new();
        public List<(int Id, int Key)> Unregistered { get; } = new();
        public Func<int, bool> FailWhen { get; set; } = _ => false;

        public void Register(int id, int keyCode, int modifiers)
        {
            if (FailWhen(keyCode)) throw new InvalidOperationException("Simulated external hotkey conflict.");
            Active.Add(id, (keyCode, modifiers));
        }

        public void Unregister(int id)
        {
            if (!Active.Remove(id, out var binding)) throw new InvalidOperationException("Unknown hotkey ID.");
            Unregistered.Add((id, binding.Key));
        }
    }

    private sealed class FakeDesktops : IDesktopService
    {
        public int Count => 5;
        public int Current => 1;
        public List<int> Switches { get; } = new();
        public void Switch(int number) => Switches.Add(number);
    }

    private sealed class FakeShortcuts : IShortcutService
    {
        public List<(int Key, int Modifiers)> Sent { get; } = new();
        public void Send(int keyCode, int modifiers) => Sent.Add((keyCode, modifiers));
    }
}
