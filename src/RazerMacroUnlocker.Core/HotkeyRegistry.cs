namespace RazerMacroUnlocker.Core;

public interface IHotkeyBackend
{
    void Register(int id, int keyCode, int modifiers);
    void Unregister(int id);
}

public sealed class HotkeyRegistry(IHotkeyBackend backend) : IDisposable
{
    private readonly Dictionary<int, HotkeyBinding> active = new();
    public int Count => active.Count;
    public HotkeyBinding? Find(int id) => active.GetValueOrDefault(id);

    public void Apply(IEnumerable<HotkeyBinding> bindings)
    {
        var previous = active.Values.ToArray();
        Clear();
        try
        {
            Register(bindings);
        }
        catch (Exception registrationError)
        {
            Clear();
            try { Register(previous); }
            catch (Exception rollbackError)
            {
                Clear();
                throw new AggregateException("The previous hotkeys could not be restored.", registrationError, rollbackError);
            }
            throw;
        }
    }

    private void Register(IEnumerable<HotkeyBinding> bindings)
    {
        foreach (var binding in bindings.Where(b => b.Enabled))
        {
            var id = active.Count + 1;
            backend.Register(id, binding.KeyCode, binding.Modifiers);
            active.Add(id, binding);
        }
    }

    private void Clear()
    {
        foreach (var id in active.Keys) backend.Unregister(id);
        active.Clear();
    }

    public void Dispose() => Clear();
}
