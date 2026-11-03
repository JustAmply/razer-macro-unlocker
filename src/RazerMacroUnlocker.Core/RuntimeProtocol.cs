using System.Diagnostics;
using System.Security.Principal;

namespace RazerMacroUnlocker.Core;

public sealed record RuntimeRequest(string Command, AppSettings? Settings = null, HotkeyBinding? Binding = null);
public sealed record RuntimeResponse(bool Success, string Message, AppSettings? Settings = null, bool HardwareRunning = false);

public static class RuntimeProtocol
{
    public static string PipeName => $"RazerMacroUnlocker-{WindowsIdentity.GetCurrent().User!.Value}-{Process.GetCurrentProcess().SessionId}";
}
