using System.Diagnostics;
using System.IO.Pipes;
using System.Text;
using System.Text.Json;

namespace RazerMacroUnlocker.Core;

public sealed class RuntimeClient
{
    private bool started;

    public async Task<RuntimeResponse> GetAsync()
    {
        if (!started)
        {
            var executable = Path.Combine(AppContext.BaseDirectory, "runtime", "RazerMacroUnlocker.Host.exe");
            Process.Start(new ProcessStartInfo(executable)
            {
                Arguments = "--background", UseShellExecute = false, CreateNoWindow = true
            })?.Dispose();
            started = true;
        }
        return await SendAsync(new("get"));
    }

    public Task<RuntimeResponse> SaveAsync(AppSettings settings) => SendAsync(new("save", settings));
    public Task<RuntimeResponse> TestAsync(HotkeyBinding binding) => SendAsync(new("test", Binding: binding));
    public Task<RuntimeResponse> QuitAsync() => SendAsync(new("quit"));

    private static async Task<RuntimeResponse> SendAsync(RuntimeRequest request)
    {
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(8));
        await using var pipe = new NamedPipeClientStream(".", RuntimeProtocol.PipeName,
            PipeDirection.InOut, PipeOptions.Asynchronous | PipeOptions.CurrentUserOnly);
        try
        {
            await pipe.ConnectAsync(timeout.Token);
            using var writer = new StreamWriter(pipe, new UTF8Encoding(false), leaveOpen: true) { AutoFlush = true };
            using var reader = new StreamReader(pipe, Encoding.UTF8, leaveOpen: true);
            await writer.WriteLineAsync(JsonSerializer.Serialize(request).AsMemory(), timeout.Token);
            var response = await reader.ReadLineAsync(timeout.Token);
            return JsonSerializer.Deserialize<RuntimeResponse>(response ?? "null")
                   ?? throw new IOException("The background process did not send a response.");
        }
        catch (OperationCanceledException)
        {
            throw new IOException("The background process is not responding. Reopen Razer Macro Unlocker.");
        }
    }
}
