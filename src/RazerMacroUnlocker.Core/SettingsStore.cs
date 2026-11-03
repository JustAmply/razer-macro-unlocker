using System.Text.Json;
using System.Text.Json.Serialization;

namespace RazerMacroUnlocker.Core;

public sealed class SettingsStore(string path)
{
    public string FilePath { get; } = path;
    private static readonly JsonSerializerOptions Options = new()
    {
        WriteIndented = true,
        Converters = { new JsonStringEnumConverter() }
    };

    public AppSettings Load()
    {
        if (!File.Exists(FilePath)) return new AppSettings();
        var settings = JsonSerializer.Deserialize<AppSettings>(File.ReadAllText(FilePath), Options)
                       ?? throw new InvalidOperationException("The configuration file is empty.");
        SettingsValidator.Validate(settings);
        return settings;
    }

    public void Save(AppSettings settings)
    {
        SettingsValidator.Validate(settings);
        Directory.CreateDirectory(Path.GetDirectoryName(FilePath)!);
        var temporary = FilePath + ".tmp";
        try
        {
            using (var stream = new FileStream(temporary, FileMode.Create, FileAccess.Write, FileShare.None))
            {
                JsonSerializer.Serialize(stream, settings, Options);
                stream.Flush(flushToDisk: true);
            }
            File.Move(temporary, FilePath, overwrite: true);
        }
        finally
        {
            if (File.Exists(temporary)) File.Delete(temporary);
        }
    }
}
