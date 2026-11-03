using System.ComponentModel;
using RazerMacroUnlocker.Core;
using RazerMacroUnlocker.WinUI.ViewModels;
using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Windows.Storage.Pickers;
using Windows.Graphics;

namespace RazerMacroUnlocker.WinUI;

public sealed partial class MainWindow : Window
{
    private readonly RuntimeClient client = new();
    private readonly SettingsViewModel model = new();
    private bool loaded;
    private bool busy;
    private bool allowClose;
    private bool closeDialogOpen;

    public MainWindow()
    {
        InitializeComponent();
        Root.DataContext = model;
        OutputKeyChoice.ItemsSource = BindingViewModel.OutputKeys;
        ActionChoice.ItemsSource = BindingViewModel.Actions;
        DesktopChoice.NumberFormatter = new Windows.Globalization.NumberFormatting.DecimalFormatter { FractionDigits = 0, IntegerDigits = 1 };
        Navigation.SelectedItem = BindingsNav;
        AppWindow.Resize(new SizeInt32(960, 680));
        AppWindow.Closing += Window_Closing;
        model.PropertyChanged += ModelChanged;
        Closed += (_, _) => model.PropertyChanged -= ModelChanged;
        UpdateControls();
    }

    private BindingViewModel? Selected => BindingList.SelectedItem as BindingViewModel;

    private async void Root_Loaded(object sender, RoutedEventArgs e)
    {
        if (loaded) return;
        var scale = Root.XamlRoot.RasterizationScale;
        if (AppWindow.Presenter is OverlappedPresenter presenter)
        {
            presenter.PreferredMinimumWidth = (int)(820 * scale);
            presenter.PreferredMinimumHeight = (int)(580 * scale);
        }
        AppWindow.Resize(new SizeInt32((int)(960 * scale), (int)(680 * scale)));
        SetBusy(true);
        try
        {
            var response = await client.GetAsync();
            if (!response.Success || response.Settings is null)
            {
                ShowFeedback(response.Message, InfoBarSeverity.Error);
                return;
            }
            model.Load(response.Settings);
            HardwareStatus.Text = response.HardwareRunning ? "Keyboard unlocker running" : "Keyboard unlocker starting";
            BindingList.SelectedIndex = model.Bindings.Count > 0 ? 0 : -1;
            loaded = true;
            Feedback.IsOpen = false;
        }
        catch (Exception error) { ShowFeedback(error.Message, InfoBarSeverity.Error); }
        finally { SetBusy(false); }
    }

    private async void Navigation_SelectionChanged(NavigationView sender, NavigationViewSelectionChangedEventArgs args)
    {
        if (BindingsPage is null || BackgroundPage is null) return;
        bool bindings = (args.SelectedItem as NavigationViewItem)?.Tag as string != "background";
        BindingsPage.Visibility = bindings ? Visibility.Visible : Visibility.Collapsed;
        BackgroundPage.Visibility = bindings ? Visibility.Collapsed : Visibility.Visible;
        if (!bindings && loaded)
        {
            try
            {
                var response = await client.GetAsync();
                HardwareStatus.Text = response.HardwareRunning ? "Keyboard unlocker running" : "Keyboard unlocker starting";
            }
            catch (Exception error) { HardwareStatus.Text = error.Message; }
        }
    }

    private void BindingList_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (Editor is null) return;
        Editor.DataContext = Selected;
        EditorScroll.Visibility = Selected is null ? Visibility.Collapsed : Visibility.Visible;
        EmptyEditor.Visibility = Selected is null ? Visibility.Visible : Visibility.Collapsed;
        EditorScroll.ChangeView(null, 0, null, true);
    }

    private void Add_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            var item = model.Add();
            BindingList.SelectedItem = item;
            BindingList.ScrollIntoView(item);
            UpdateControls();
        }
        catch (InvalidOperationException error) { ShowFeedback(error.Message, InfoBarSeverity.Warning); }
    }

    private async void Remove_Click(object sender, RoutedEventArgs e)
    {
        if (Selected is not { } selected || busy || closeDialogOpen) return;
        var dialog = new ContentDialog
        {
            XamlRoot = Root.XamlRoot, Title = "Remove key?",
            Content = $"Remove {selected.InputName}?",
            PrimaryButtonText = "Remove", CloseButtonText = "Cancel", DefaultButton = ContentDialogButton.Close
        };
        closeDialogOpen = true;
        ContentDialogResult choice;
        try { choice = await dialog.ShowAsync(); }
        finally { closeDialogOpen = false; }
        if (choice != ContentDialogResult.Primary) return;
        var index = BindingList.SelectedIndex;
        model.Remove(selected);
        BindingList.SelectedIndex = model.Bindings.Count > 0 ? Math.Min(index, model.Bindings.Count - 1) : -1;
        UpdateControls();
    }

    private async void Save_Click(object sender, RoutedEventArgs e) => await SaveAsync();

    private async Task<bool> SaveAsync()
    {
        if (busy || !loaded) return false;
        SetBusy(true);
        try
        {
            var index = BindingList.SelectedIndex;
            var response = await client.SaveAsync(model.ToSettings());
            if (!response.Success || response.Settings is null)
            {
                ShowFeedback(response.Message, InfoBarSeverity.Error);
                return false;
            }
            model.Load(response.Settings);
            BindingList.SelectedIndex = model.Bindings.Count > 0 ? Math.Clamp(index, 0, model.Bindings.Count - 1) : -1;
            Feedback.IsOpen = false;
            return true;
        }
        catch (Exception error) { ShowFeedback(error.Message, InfoBarSeverity.Error); return false; }
        finally { SetBusy(false); }
    }

    private async void Test_Click(object sender, RoutedEventArgs e)
    {
        if (Selected is not { } selected || busy) return;
        SetBusy(true);
        try
        {
            var response = await client.TestAsync(selected.ToBinding());
            ShowFeedback(response.Message, response.Success ? InfoBarSeverity.Success : InfoBarSeverity.Error);
        }
        catch (Exception error) { ShowFeedback(error.Message, InfoBarSeverity.Error); }
        finally { SetBusy(false); }
    }

    private async void Reconnect_Click(object sender, RoutedEventArgs e)
    {
        if (busy) return;
        SetBusy(true);
        try
        {
            var response = await client.ReconnectAsync();
            HardwareStatus.Text = !response.Success ? response.Message
                : response.HardwareRunning ? "Keyboard unlocker running" : "Keyboard reconnection requested";
        }
        catch (Exception error) { ShowFeedback(error.Message, InfoBarSeverity.Error); }
        finally { SetBusy(false); }
    }

    private async void PickFile_Click(object sender, RoutedEventArgs e)
    {
        if (Selected is not { } selected) return;
        try
        {
            var picker = new FileOpenPicker();
            WinRT.Interop.InitializeWithWindow.Initialize(picker, WinRT.Interop.WindowNative.GetWindowHandle(this));
            picker.FileTypeFilter.Add("*");
            var file = await picker.PickSingleFileAsync();
            if (file is not null) selected.Target = file.Path;
        }
        catch (Exception error) { ShowFeedback(error.Message, InfoBarSeverity.Error); }
    }

    private async void PickFolder_Click(object sender, RoutedEventArgs e)
    {
        if (Selected is not { } selected) return;
        try
        {
            var picker = new FolderPicker();
            WinRT.Interop.InitializeWithWindow.Initialize(picker, WinRT.Interop.WindowNative.GetWindowHandle(this));
            picker.FileTypeFilter.Add("*");
            var folder = await picker.PickSingleFolderAsync();
            if (folder is not null) selected.Target = folder.Path;
        }
        catch (Exception error) { ShowFeedback(error.Message, InfoBarSeverity.Error); }
    }

    private async void Quit_Click(object sender, RoutedEventArgs e)
    {
        if (busy || closeDialogOpen || !await ConfirmUnsavedAsync()) return;
        SetBusy(true);
        try
        {
            var response = await client.QuitAsync();
            if (!response.Success) { ShowFeedback(response.Message, InfoBarSeverity.Error); return; }
            allowClose = true;
            Close();
        }
        catch (Exception error) { ShowFeedback(error.Message, InfoBarSeverity.Error); }
        finally { SetBusy(false); }
    }

    private async void Window_Closing(AppWindow sender, AppWindowClosingEventArgs args)
    {
        if (allowClose) return;
        if (!busy && !closeDialogOpen && !model.IsDirty) return;
        args.Cancel = true;
        if (busy || closeDialogOpen) return;
        if (await ConfirmUnsavedAsync())
        {
            allowClose = true;
            Close();
        }
    }

    private async Task<bool> ConfirmUnsavedAsync()
    {
        if (!model.IsDirty) return true;
        closeDialogOpen = true;
        try
        {
            var dialog = new ContentDialog
            {
                XamlRoot = Root.XamlRoot, Title = "Save changes?",
                Content = "",
                PrimaryButtonText = "Save", SecondaryButtonText = "Discard", CloseButtonText = "Cancel",
                DefaultButton = ContentDialogButton.Primary
            };
            var choice = await dialog.ShowAsync();
            return choice == ContentDialogResult.Secondary || choice == ContentDialogResult.Primary && await SaveAsync();
        }
        finally { closeDialogOpen = false; }
    }

    private void ModelChanged(object? sender, PropertyChangedEventArgs e) => UpdateControls();

    private void SetBusy(bool value)
    {
        busy = value;
        BusyRing.IsActive = value;
        BusyRing.Visibility = value ? Visibility.Visible : Visibility.Collapsed;
        UpdateControls();
    }

    private void UpdateControls()
    {
        SaveButton.IsEnabled = loaded && !busy && model.IsDirty;
        Navigation.IsEnabled = loaded && !busy;
        AddButton.IsEnabled = loaded && !busy && model.Bindings.Count < 12;
        RetryButton.Visibility = loaded ? Visibility.Collapsed : Visibility.Visible;
        RetryButton.IsEnabled = !busy;
        Title = "Razer Macro Unlocker";
    }

    private void ShowFeedback(string message, InfoBarSeverity severity)
    {
        Feedback.Title = "";
        Feedback.Message = message;
        Feedback.Severity = severity;
        Feedback.IsOpen = !string.IsNullOrWhiteSpace(message);
    }
}
