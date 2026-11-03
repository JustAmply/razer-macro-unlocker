using System.Security.Principal;
using RazerMacroUnlocker.Windows;

namespace RazerMacroUnlocker;

internal static class Program
{
    [STAThread]
    private static void Main(string[] args)
    {
        ApplicationConfiguration.Initialize();
        if (args.Any(arg => arg is not ("--background" or "--quit")))
        {
            MessageBox.Show("RazerMacroUnlocker.exe [--background | --quit]\n\nRun without arguments to open settings.", "Razer Macro Unlocker");
            return;
        }
        var identity = WindowsIdentity.GetCurrent().User!.Value;
        var title = $"RazerMacroUnlocker.Host.{identity}";
        using var mutex = new Mutex(true, $"Local\\{title}", out var ownsInstance);
        if (!ownsInstance)
        {
            nint handle = 0;
            for (var attempt = 0; attempt < 20 && handle == 0; attempt++)
            {
                handle = HotkeyWindow.FindWindow(null, title);
                if (handle == 0) Thread.Sleep(100);
            }
            if (handle == 0)
            {
                MessageBox.Show("Razer Macro Unlocker is starting. Please try again.", "Razer Macro Unlocker");
                return;
            }
            if (!args.Contains("--background"))
            {
                HotkeyWindow.GetWindowThreadProcessId(handle, out var processId);
                HotkeyWindow.AllowSetForegroundWindow(processId);
                if (!HotkeyWindow.PostMessage(handle, HotkeyWindow.CommandMessage,
                        args.Contains("--quit") ? 2 : 1, 0))
                    MessageBox.Show("Could not reach the running application.", "Razer Macro Unlocker");
            }
            return;
        }
        try
        {
            if (args.Contains("--quit")) return;
            using var context = new RazerMacroUnlockerContext(title, args.Contains("--background"));
            Application.Run(context);
        }
        catch (Exception error)
        {
            MessageBox.Show($"Razer Macro Unlocker could not start.\n\n{error.Message}\n\n" +
                $"Settings: {RazerMacroUnlockerContext.SettingsPath}", "Razer Macro Unlocker", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
        finally { mutex.ReleaseMutex(); }
    }
}
