using System.ComponentModel;
using System.Runtime.InteropServices;
using RazerMacroUnlocker.Core;

namespace RazerMacroUnlocker.Windows;

public sealed class ShortcutService : IShortcutService
{
    private static readonly (int Flag, int Key)[] Modifiers = [(2, 0x11), (1, 0x12), (4, 0x10), (8, 0x5B)];

    public void Send(int keyCode, int modifiers)
    {
        SettingsValidator.ValidateShortcut(keyCode, modifiers);
        // Do not release physical keys or accidentally add held modifiers to the requested chord.
        var held = Modifiers.Where(modifier => IsDown(modifier.Key)
            || (modifier.Flag == 8 && IsDown(0x5C))).ToArray();
        if (held.Any(modifier => (modifiers & modifier.Flag) == 0) || IsDown(keyCode))
            throw new InvalidOperationException("Release the held keys before sending this shortcut.");
        var heldFlags = held.Aggregate(0, (flags, modifier) => flags | modifier.Flag);
        var inputs = BuildInputs(keyCode, modifiers & ~heldFlags);
        var sent = SendInput((uint)inputs.Length, inputs, Marshal.SizeOf<KeyboardInput>());
        if (sent == inputs.Length) return;
        var error = Marshal.GetLastWin32Error();
        // A partially accepted sequence may leave synthesized modifiers down.
        if (sent > 0)
        {
            var releases = inputs.Where(input => (input.Flags & 2) != 0).ToArray();
            SendInput((uint)releases.Length, releases, Marshal.SizeOf<KeyboardInput>());
        }
        throw new Win32Exception(error, "Windows could not send the shortcut. The target may run with elevated privileges or block simulated input.");
    }

    internal static KeyboardInput[] BuildInputs(int keyCode, int modifiers)
    {
        var keys = Modifiers.Where(modifier => (modifiers & modifier.Flag) != 0)
            .Select(modifier => modifier.Key).Append(keyCode).ToArray();
        return keys.Select(key => Create(key, false))
            .Concat(keys.Reverse().Select(key => Create(key, true))).ToArray();
    }

    private static KeyboardInput Create(int key, bool release) => new()
    {
        Type = 1,
        VirtualKey = (ushort)key,
        Flags = (release ? 2u : 0u) | (key is >= 0x21 and <= 0x28 or 0x2D or 0x2E or 0x5B ? 1u : 0u)
    };

    private static bool IsDown(int key) => (GetAsyncKeyState(key) & 0x8000) != 0;

    // INPUT is 40 bytes on the x64 target; its 32-byte union starts at offset 8.
    [StructLayout(LayoutKind.Explicit, Size = 40)]
    internal struct KeyboardInput
    {
        [FieldOffset(0)] public uint Type;
        [FieldOffset(8)] public ushort VirtualKey;
        [FieldOffset(10)] public ushort ScanCode;
        [FieldOffset(12)] public uint Flags;
        [FieldOffset(16)] public uint Time;
        [FieldOffset(24)] public nuint ExtraInfo;
    }

    [DllImport("user32.dll", SetLastError = true)]
    private static extern uint SendInput(uint count, [In] KeyboardInput[] inputs, int size);
    [DllImport("user32.dll")]
    private static extern short GetAsyncKeyState(int key);
}
