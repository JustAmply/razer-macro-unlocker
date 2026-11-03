using Microsoft.UI.Xaml;

namespace RazerMacroUnlocker.WinUI;

public partial class App : Application
{
    private MainWindow? window;

    public App()
    {
        InitializeComponent();
        UnhandledException += (_, args) =>
        {
            RecordError(args.Message + "\n" + args.Exception);
        };
    }

    private static void RecordError(string message)
    {
        var path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Razer Macro Unlocker");
        Directory.CreateDirectory(path);
        File.WriteAllText(Path.Combine(path, "startup-error.txt"), message + "\n");
    }

    public void ActivateWindow() => window?.Activate();

    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        window = new MainWindow();
        window.Activate();
    }
}
