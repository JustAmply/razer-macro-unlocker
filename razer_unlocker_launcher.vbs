Set FSO = CreateObject("Scripting.FileSystemObject")
ScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
TargetScript = FSO.BuildPath(ScriptDir, "razer_unlocker.pyw")

Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "python.exe """ & TargetScript & """", 0, False
