using System.Runtime.InteropServices;
using RazerMacroUnlocker.Core;

namespace RazerMacroUnlocker.Windows;

public sealed class DesktopService : IDesktopService
{
    public int Count => Check(GetDesktopCount());
    public int Current => Check(GetCurrentDesktopNumber()) + 1;

    public void Switch(int number)
    {
        var count = Count;
        if (number < 1 || number > count)
            throw new InvalidOperationException($"Desktop {number} does not exist. Available: {count}. Create it in Windows first.");
        if (Current != number) Check(GoToDesktopNumber(number - 1));
    }

    private static int Check(int result) => result < 0
        ? throw new InvalidOperationException("The Windows desktop service is unavailable. The desktop adapter may need an update for your Windows version.")
        : result;

    [DllImport("VirtualDesktopAccessor.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern int GetDesktopCount();
    [DllImport("VirtualDesktopAccessor.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern int GetCurrentDesktopNumber();
    [DllImport("VirtualDesktopAccessor.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern int GoToDesktopNumber(int number);
}
