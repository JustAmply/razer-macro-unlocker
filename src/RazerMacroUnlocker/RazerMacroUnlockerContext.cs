using RazerMacroUnlocker.Core;
using RazerMacroUnlocker.Windows;
using System.Diagnostics;

namespace RazerMacroUnlocker;

internal sealed class RazerMacroUnlockerContext : ApplicationContext
{
    internal static string SettingsPath => Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Razer Macro Unlocker", "settings.json");
    private readonly SettingsStore store = new(SettingsPath);
    private readonly HotkeyWindow window;
    private readonly HotkeyRegistry hotkeys;
    private readonly ActionDispatcher dispatcher = new(new DesktopService(), new ShortcutService());
    private readonly Icon icon;
    private readonly RuntimeServer server;
    private NotifyIcon? tray;
    private AppSettings settings;
    private string status = "Ready";

    public AppSettings Settings => settings.Copy();
    public string Status => status;

    internal RazerMacroUnlockerContext(string title, bool background)
    {
        settings = store.Load();
        icon = Icon.ExtractAssociatedIcon(Environment.ProcessPath!) ?? (Icon)SystemIcons.Application.Clone();
        window = new HotkeyWindow(title);
        hotkeys = new HotkeyRegistry(window);
        window.HotkeyPressed += id =>
        {
            if (hotkeys.Find(id) is { } binding) Test(binding);
        };
        window.CommandReceived += command =>
        {
            if (command == 1) ShowSettings();
            if (command == 2) Quit();
        };
        try
        {
            hotkeys.Apply(settings.Bindings);
            SetStatus($"{hotkeys.Count} keys active");
        }
        catch (Exception error)
        {
            SetStatus(error.Message);
            background = false;
        }
        var synchronization = new WindowsFormsSynchronizationContext();
        SynchronizationContext.SetSynchronizationContext(synchronization);
        server = new RuntimeServer(RuntimeProtocol.PipeName, synchronization, HandleRequest, Quit, SetStatus);
        UpdateTray();
        if (!background) ShowSettings();
    }

    public void Save(AppSettings candidate)
    {
        SettingsValidator.Validate(candidate);
        var previous = settings;
        hotkeys.Apply(candidate.Bindings);
        try
        {
            StartupRegistration.Set(candidate.StartWithWindows);
            store.Save(candidate);
        }
        catch (Exception saveError)
        {
            // Restore independent resources even when one rollback operation fails.
            var errors = new List<Exception> { saveError };
            try { hotkeys.Apply(previous.Bindings); }
            catch (Exception error) { errors.Add(error); }
            try { StartupRegistration.Set(previous.StartWithWindows); }
            catch (Exception error) { errors.Add(error); }
            if (errors.Count > 1)
                throw new AggregateException("Could not save or restore settings.", errors);
            throw;
        }
        settings = candidate.Copy();
        UpdateTray();
        SetStatus($"Saved · {hotkeys.Count} keys active");
    }

    public void Test(HotkeyBinding binding)
    {
        try { SetStatus(dispatcher.Execute(binding)); }
        catch (Exception error)
        {
            SetStatus(error.Message);
            tray?.ShowBalloonTip(4000, "Razer Macro Unlocker", error.Message, ToolTipIcon.Warning);
        }
    }

    private void SetStatus(string value)
    {
        status = value;
    }

    private RuntimeResponse HandleRequest(RuntimeRequest request)
    {
        switch (request.Command)
        {
            case "get": return new(true, Status, Settings);
            case "save" when request.Settings is not null:
                Save(request.Settings);
                return new(true, Status, Settings);
            case "test" when request.Binding is not null:
                SetStatus(dispatcher.Execute(request.Binding));
                return new(true, Status);
            case "quit": return new(true, "Background process stopped.");
            default: return new(false, "Unknown or incomplete request.");
        }
    }

    private void ShowSettings()
    {
        var editor = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "RazerMacroUnlocker.exe"));
        Process.Start(new ProcessStartInfo(editor) { UseShellExecute = true })?.Dispose();
    }

    private void UpdateTray()
    {
        if (!settings.ShowTrayIcon)
        {
            if (tray is not null)
            {
                tray.Visible = false;
                tray.ContextMenuStrip?.Dispose();
                tray.Dispose();
                tray = null;
            }
            return;
        }
        if (tray is not null) return;
        var menu = new ContextMenuStrip();
        menu.Items.Add("Open settings", null, (_, _) => ShowSettings());
        menu.Items.Add("Quit", null, (_, _) => Quit());
        tray = new NotifyIcon { Icon = icon, Text = "Razer Macro Unlocker", ContextMenuStrip = menu, Visible = true };
        tray.DoubleClick += (_, _) => ShowSettings();
    }

    public void Quit()
    {
        ExitThread();
    }

    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            server.Dispose();
            tray?.ContextMenuStrip?.Dispose();
            tray?.Dispose();
            hotkeys.Dispose();
            window.Dispose();
            icon.Dispose();
        }
        base.Dispose(disposing);
    }
}
