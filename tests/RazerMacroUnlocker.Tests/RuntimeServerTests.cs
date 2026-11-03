using System.Collections.Concurrent;
using System.IO.Pipes;
using System.Text;
using System.Text.Json;
using RazerMacroUnlocker.Core;
using RazerMacroUnlocker.Windows;

namespace RazerMacroUnlocker.Tests;

internal static class RuntimeServerTests
{
    public static void RequestRunsOnOwnerThread() => Run(async () =>
    {
        var handlerThread = 0;
        using var fixture = new Fixture(request =>
        {
            handlerThread = Environment.CurrentManagedThreadId;
            return new(true, request.Command, new AppSettings());
        });
        var response = await Exchange(fixture.Name, "{\"Command\":\"get\"}");
        Check(response.Success && response.Settings?.Bindings.Count == 5, "Get response lost settings.");
        Check(handlerThread == fixture.Context.ThreadId, "Handler ran outside its owner thread.");
    });

    public static void MalformedRequestAndHandlerErrorRecover() => Run(async () =>
    {
        using var fixture = new Fixture(request => request.Command == "save"
            ? throw new InvalidOperationException("Cannot save fixture.")
            : new(true, "Ready"));
        var malformed = await Exchange(fixture.Name, "{broken");
        Check(!malformed.Success && !string.IsNullOrWhiteSpace(malformed.Message), "Malformed input was not rejected.");
        var rejected = await Exchange(fixture.Name, "{\"Command\":\"save\"}");
        Check(!rejected.Success && rejected.Message == "Cannot save fixture.", "Handler error was not returned.");
        var recovered = await Exchange(fixture.Name, "{\"Command\":\"get\"}");
        Check(recovered.Success, "Server stopped accepting requests after errors.");
    });

    public static void DisconnectedClientDoesNotStopListener() => Run(async () =>
    {
        using var fixture = new Fixture(_ => new(true, "Ready"));
        using (var abandoned = NewClient(fixture.Name))
            await abandoned.ConnectAsync(3000);
        var response = await Exchange(fixture.Name, "{\"Command\":\"get\"}");
        Check(response.Success, "Disconnected client prevented next request.");
    });

    public static void IdleCancellationCompletesCleanly() => Run(async () =>
    {
        using var fixture = new Fixture(_ => new(true, "Ready"));
        fixture.Server.Dispose();
        fixture.Server.Dispose();
        await fixture.Server.Completion.WaitAsync(TimeSpan.FromSeconds(3));
        Check(fixture.Server.Completion.IsCompletedSuccessfully, "Canceled listener faulted.");
    });

    public static void ListenerFailureReportsOnce() => Run(async () =>
    {
        var name = "RazerMacroUnlocker.Tests." + Guid.NewGuid().ToString("N");
        using var occupied = new NamedPipeServerStream(name, PipeDirection.InOut, 1,
            PipeTransmissionMode.Byte, PipeOptions.Asynchronous | PipeOptions.CurrentUserOnly);
        using var context = new OwnerContext();
        var errors = new ConcurrentQueue<string>();
        var reported = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        using var server = new RuntimeServer(name, context, _ => new(true, "unused"), () => { }, message =>
        {
            errors.Enqueue(message);
            reported.TrySetResult();
        });
        await server.Completion.WaitAsync(TimeSpan.FromSeconds(3));
        await reported.Task.WaitAsync(TimeSpan.FromSeconds(3));
        Check(errors.Count == 1, "Listener failure was not reported exactly once.");
    });

    private static NamedPipeClientStream NewClient(string name) => new(".", name,
        PipeDirection.InOut, PipeOptions.Asynchronous | PipeOptions.CurrentUserOnly);

    private static async Task<RuntimeResponse> Exchange(string name, string line)
    {
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(3));
        await using var client = NewClient(name);
        await client.ConnectAsync(timeout.Token);
        using var writer = new StreamWriter(client, new UTF8Encoding(false), leaveOpen: true) { AutoFlush = true };
        using var reader = new StreamReader(client, Encoding.UTF8, leaveOpen: true);
        await writer.WriteLineAsync(line.AsMemory(), timeout.Token);
        var response = await reader.ReadLineAsync(timeout.Token);
        return JsonSerializer.Deserialize<RuntimeResponse>(response ?? "null")
               ?? throw new InvalidOperationException("No response received.");
    }

    private static void Run(Func<Task> test) => test().GetAwaiter().GetResult();
    private static void Check(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }

    private sealed class Fixture : IDisposable
    {
        public string Name { get; } = "RazerMacroUnlocker.Tests." + Guid.NewGuid().ToString("N");
        public OwnerContext Context { get; } = new();
        public RuntimeServer Server { get; }

        public Fixture(Func<RuntimeRequest, RuntimeResponse> handler)
        {
            Server = new RuntimeServer(Name, Context, handler, () => { }, _ => { });
        }

        public void Dispose()
        {
            Server.Dispose();
            try { Server.Completion.WaitAsync(TimeSpan.FromSeconds(3)).GetAwaiter().GetResult(); }
            finally { Context.Dispose(); }
        }
    }

    private sealed class OwnerContext : SynchronizationContext, IDisposable
    {
        private readonly BlockingCollection<(SendOrPostCallback Callback, object? State)> work = new();
        private readonly Thread thread;
        public int ThreadId => thread.ManagedThreadId;

        public OwnerContext()
        {
            thread = new Thread(() =>
            {
                SetSynchronizationContext(this);
                foreach (var item in work.GetConsumingEnumerable()) item.Callback(item.State);
            }) { IsBackground = true, Name = "RazerMacroUnlocker IPC test owner" };
            thread.SetApartmentState(ApartmentState.STA);
            thread.Start();
        }

        public override void Post(SendOrPostCallback callback, object? state) => work.Add((callback, state));

        public void Dispose()
        {
            work.CompleteAdding();
            if (!thread.Join(TimeSpan.FromSeconds(3))) throw new InvalidOperationException("Owner thread did not stop.");
            work.Dispose();
        }
    }
}
