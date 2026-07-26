Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
desktopDir = WshShell.SpecialFolders("Desktop")

shortcutPath = desktopDir & "\Nova Downloader.lnk"
Set shortcut = WshShell.CreateShortcut(shortcutPath)
shortcut.TargetPath = scriptDir & "\NovaDownloader.vbs"
shortcut.WorkingDirectory = scriptDir
shortcut.IconLocation = scriptDir & "\assets\icon.ico, 0"
shortcut.Description = "Nova Downloader por David496"
shortcut.Save

WScript.Echo "¡Acceso directo de Nova Downloader creado en el Escritorio con éxito!"
