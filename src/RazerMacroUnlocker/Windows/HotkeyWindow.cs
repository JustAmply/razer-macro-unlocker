using System.ComponentModel;
using System.Runtime.InteropServices;
using RazerMacroUnlocker.Core;

namespace RazerMacroUnlocker.Windows;

internal sealed class HotkeyWindow : NativeWindow, IHotkeyBackend, IDisposable
{
    public static readonly uint CommandMessage = RegisterWindowMessage("RazerMacroUnlocker.Command.v1");
    public event Action<int>? HotkeyPressed;
    public event Action<int>? CommandReceived;

    public HotkeyWindow(string title) => CreateHandle(new CreateParams { Caption = title });

    public void Register(int id, int keyCode, int modifiers)
    {
        if (!RegisterHotKey(Handle, id, (uint)modifiers | 0x4000, (uint)keyCode))
            throw new Win32Exception(Marshal.GetLastWin32Error(),
                $"F{keyCode - 0x6F}: The hotkey is already assigned or unavailable.");
    }

    public void Unregister(int id) => UnregisterHotKey(Handle, id);

    protected override void WndProc(ref Message message)
    {
        if (message.Msg == 0x0312) HotkeyPressed?.Invoke((int)message.WParam);
        else if ((uint)message.Msg == CommandMessage) CommandReceived?.Invoke((int)message.WParam);
        base.WndProc(ref message);
    }

    public void Dispose() => DestroyHandle();

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool RegisterHotKey(nint hWnd, int id, uint modifiers, uint key);
    [DllImport("user32.dll")]
    private static extern bool UnregisterHotKey(nint hWnd, int id);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    private static extern uint RegisterWindowMessage(string message);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    internal static extern nint FindWindow(string? className, string title);
    [DllImport("user32.dll", SetLastError = true)]
    internal static extern bool PostMessage(nint hWnd, uint message, nint wParam, nint lParam);
    [DllImport("user32.dll")]
    internal static extern uint GetWindowThreadProcessId(nint hWnd, out uint processId);
    [DllImport("user32.dll")]
    internal static extern bool AllowSetForegroundWindow(uint processId);
}
