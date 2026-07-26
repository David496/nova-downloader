Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

pythonwPath = scriptDir & "\venv\Scripts\pythonw.exe"
mainScript = scriptDir & "\main_flet.py"

If fso.FileExists(pythonwPath) Then
    WshShell.Run """" & pythonwPath & """" & " """ & mainScript & """", 0, False
Else
    WshShell.Run "pythonw """ & mainScript & """", 0, False
End If
