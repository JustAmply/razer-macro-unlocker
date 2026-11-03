using Microsoft.Win32;

namespace RazerMacroUnlocker.Windows;

internal static class StartupRegistration
{
    private const string Key = @"Software\Microsoft\Windows\CurrentVersion\Run";
    internal sealed record Snapshot(string? App, string? Legacy);

    public static Snapshot Capture()
    {
        using var registry = Registry.CurrentUser.OpenSubKey(Key);
        return new(registry?.GetValue("Razer Macro Unlocker") as string,
            registry?.GetValue("RazerUnlocker") as string);
    }

    public static void Restore(Snapshot snapshot)
    {
        using var registry = Registry.CurrentUser.CreateSubKey(Key);
        RestoreValue("Razer Macro Unlocker", snapshot.App);
        RestoreValue("RazerUnlocker", snapshot.Legacy);
        void RestoreValue(string name, string? value)
        {
            if (value is null) registry.DeleteValue(name, throwOnMissingValue: false);
            else registry.SetValue(name, value);
        }
    }
    public static void Set(bool enabled)
    {
        using var registry = Registry.CurrentUser.CreateSubKey(Key);
        if (enabled)
            registry.SetValue("Razer Macro Unlocker", $"\"{Environment.ProcessPath}\" --background");
        else
            registry.DeleteValue("Razer Macro Unlocker", throwOnMissingValue: false);
        // Replace the legacy helper-only startup entry with the unified app setting.
        registry.DeleteValue("RazerUnlocker", throwOnMissingValue: false);
    }
}
