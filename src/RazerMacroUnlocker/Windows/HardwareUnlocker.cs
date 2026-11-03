using System.Diagnostics;
using System.Runtime.InteropServices;

namespace RazerMacroUnlocker.Windows;

internal sealed class HardwareUnlocker : IDisposable
{
    private const string WindowClass = "RazerUnlockerServiceClass";
    private const string WindowTitle = "RazerUnlocker";
    public bool IsRunning => FindWindow(WindowClass, WindowTitle) != 0;

    public void Start()
    {
        var window = FindWindow(WindowClass, WindowTitle);
        if (window != 0)
        {
            if (!PostMessage(window, 0x8001, 0, 0))
                throw new InvalidOperationException("Could not reconnect the keyboard unlocker.");
            return;
        }
        var executable = Path.Combine(AppContext.BaseDirectory, "RazerMacroUnlocker.Keyboard.exe");
        Process.Start(new ProcessStartInfo(executable)
        {
            UseShellExecute = false, CreateNoWindow = true
        })?.Dispose();
    }

    public void Dispose()
    {
        var window = FindWindow(WindowClass, WindowTitle);
        if (window != 0) PostMessage(window, 0x0010, 0, 0);
    }

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    private static extern nint FindWindow(string className, string windowName);
    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool PostMessage(nint window, uint message, nint wParam, nint lParam);
}
