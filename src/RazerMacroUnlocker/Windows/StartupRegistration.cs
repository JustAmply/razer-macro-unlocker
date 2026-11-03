using Microsoft.Win32;

namespace RazerMacroUnlocker.Windows;

internal static class StartupRegistration
{
    private const string Key = @"Software\Microsoft\Windows\CurrentVersion\Run";
    public static void Set(bool enabled)
    {
        using var registry = Registry.CurrentUser.CreateSubKey(Key);
        if (enabled)
            registry.SetValue("Razer Macro Unlocker", $"\"{Environment.ProcessPath}\" --background");
        else
            registry.DeleteValue("Razer Macro Unlocker", throwOnMissingValue: false);
    }
}
