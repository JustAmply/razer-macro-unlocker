using System.Collections.ObjectModel;
using System.ComponentModel;
using RazerMacroUnlocker.Core;

namespace RazerMacroUnlocker.WinUI.ViewModels;

public sealed class SettingsViewModel : INotifyPropertyChanged
{
    private AppSettings original = new();
    private bool startWithWindows;
    private bool showTrayIcon;
    private bool dirty;
    public ObservableCollection<BindingViewModel> Bindings { get; } = [];
    public bool StartWithWindows
    {
        get => startWithWindows;
        set { if (value == startWithWindows) return; startWithWindows = value; Changed(nameof(StartWithWindows)); MarkDirty(); }
    }
    public bool ShowTrayIcon
    {
        get => showTrayIcon;
        set { if (value == showTrayIcon) return; showTrayIcon = value; Changed(nameof(ShowTrayIcon)); MarkDirty(); }
    }
    public bool IsDirty { get => dirty; private set { dirty = value; Changed(nameof(IsDirty)); Changed(nameof(SaveHint)); } }
    public string SaveHint => IsDirty ? "Unsaved changes" : "";

    public void Load(AppSettings settings)
    {
        original = settings.Copy();
        foreach (var item in Bindings) item.Edited -= MarkDirty;
        Bindings.Clear();
        foreach (var binding in settings.Bindings)
        {
            var item = new BindingViewModel(binding);
            item.Edited += MarkDirty;
            Bindings.Add(item);
        }
        startWithWindows = settings.StartWithWindows;
        showTrayIcon = settings.ShowTrayIcon;
        Changed(nameof(StartWithWindows));
        Changed(nameof(ShowTrayIcon));
        IsDirty = false;
    }

    public BindingViewModel Add()
    {
        if (Bindings.Count >= 12) throw new InvalidOperationException("All 12 macro keys are assigned.");
        var next = Enumerable.Range(13, 12).FirstOrDefault(n => !Bindings.Any(b => b.InputKeyCode == 0x6F + n));
        if (next == 0) throw new InvalidOperationException("All 12 macro keys are assigned.");
        var item = new BindingViewModel(new HotkeyBinding
        {
            Label = $"M{next - 12}", KeyCode = 0x6F + next, Action = (ActionKind)3
        });
        item.Edited += MarkDirty;
        Bindings.Add(item);
        MarkDirty();
        return item;
    }

    public void Remove(BindingViewModel binding)
    {
        binding.Edited -= MarkDirty;
        Bindings.Remove(binding);
        MarkDirty();
    }

    public AppSettings ToSettings() => original with
    {
        StartWithWindows = StartWithWindows, ShowTrayIcon = ShowTrayIcon,
        Bindings = Bindings.Select(b => b.ToBinding()).ToList()
    };

    public event PropertyChangedEventHandler? PropertyChanged;
    private void Changed(string name) => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    private void MarkDirty() => IsDirty = true;
}
