using System.IO.Pipes;
using System.Text;
using System.Text.Json;
using RazerMacroUnlocker.Core;

namespace RazerMacroUnlocker.Windows;

internal sealed class RuntimeServer : IDisposable
{
    private readonly CancellationTokenSource stop = new();
    private readonly SynchronizationContext context;
    private readonly Func<RuntimeRequest, RuntimeResponse> handle;
    private readonly Action quit;
    private readonly Action<string> reportError;
    private readonly string pipeName;
    private int disposed;
    public Task Completion { get; }

    public RuntimeServer(string pipeName, SynchronizationContext context, Func<RuntimeRequest, RuntimeResponse> handle,
        Action quit, Action<string> reportError)
    {
        this.pipeName = pipeName;
        this.context = context;
        this.handle = handle;
        this.quit = quit;
        this.reportError = reportError;
        Completion = RunAsync();
    }

    private async Task RunAsync()
    {
        while (!stop.IsCancellationRequested)
        {
            NamedPipeServerStream pipe;
            try
            {
                pipe = new NamedPipeServerStream(pipeName, PipeDirection.InOut, 1,
                    PipeTransmissionMode.Byte, PipeOptions.Asynchronous | PipeOptions.CurrentUserOnly);
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException)
            {
                // A failed listener cannot recover by spinning and flooding the UI queue.
                context.Post(_ => reportError($"The settings connection could not be started: {error.Message}"), null);
                return;
            }
            await using var ownedPipe = pipe;
            try
            {
                await pipe.WaitForConnectionAsync(stop.Token).ConfigureAwait(false);
                using var requestTimeout = CancellationTokenSource.CreateLinkedTokenSource(stop.Token);
                requestTimeout.CancelAfter(TimeSpan.FromSeconds(10));
                using var reader = new StreamReader(pipe, Encoding.UTF8, leaveOpen: true);
                using var writer = new StreamWriter(pipe, new UTF8Encoding(false), leaveOpen: true) { AutoFlush = true };
                RuntimeRequest? request = null;
                RuntimeResponse response;
                try
                {
                    var line = await reader.ReadLineAsync(requestTimeout.Token).ConfigureAwait(false);
                    request = JsonSerializer.Deserialize<RuntimeRequest>(line ?? "null")
                              ?? throw new JsonException("Empty request.");
                    var completion = new TaskCompletionSource<RuntimeResponse>(TaskCreationOptions.RunContinuationsAsynchronously);
                    context.Post(_ =>
                    {
                        if (requestTimeout.IsCancellationRequested) return;
                        try { completion.SetResult(handle(request)); }
                        catch (Exception error) { completion.SetResult(new(false, error.Message)); }
                    }, null);
                    response = await completion.Task.WaitAsync(requestTimeout.Token).ConfigureAwait(false);
                }
                catch (JsonException error) { response = new(false, error.Message); }
                await writer.WriteLineAsync(JsonSerializer.Serialize(response).AsMemory(), requestTimeout.Token).ConfigureAwait(false);
                if (request?.Command == "quit" && response.Success) context.Post(_ => quit(), null);
            }
            catch (OperationCanceledException) when (stop.IsCancellationRequested) { break; }
            catch (Exception error) when (error is IOException or OperationCanceledException)
            {
                context.Post(_ => reportError($"Settings connection: {error.Message}"), null);
            }
        }
    }

    public void Dispose()
    {
        if (Interlocked.Exchange(ref disposed, 1) != 0) return;
        stop.Cancel();
        _ = Completion.ContinueWith(_ => stop.Dispose(), CancellationToken.None,
            TaskContinuationOptions.ExecuteSynchronously, TaskScheduler.Default);
    }
}
