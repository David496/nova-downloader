# Nova Downloader

Nova Downloader es una aplicación de escritorio moderna y minimalista para descargar videos y audios de YouTube. Diseñada con una interfaz fluida y elegante inspirada en aplicaciones actuales.

## Requisitos Previos

- Python 3.12 o superior.
- **FFmpeg**: Requerido para la conversión de formatos de audio (como MP3, WAV, FLAC) y para combinar pistas de video de alta calidad (como 4K o 1080p).
  - Si no tienes FFmpeg instalado en Windows, puedes descargarlo usando un gestor de paquetes como `winget`:
    ```powershell
    winget install ffmpeg
    ```

## Instalación y Ejecución

La aplicación utiliza un entorno virtual para aislar sus dependencias (`PySide6`, `yt-dlp`).

1. **Abre tu terminal** (PowerShell o CMD).
2. **Navega a la carpeta** de la aplicación:
   ```powershell
   cd C:\Users\USER\Desktop\app
   ```
3. **Activa el entorno virtual**:
   ```powershell
   .\venv\Scripts\activate
   ```
4. **Ejecuta la aplicación**:
   ```powershell
   python main.py
   ```

## Características Principales

- **Descarga de Video**: Soporta múltiples resoluciones, desde SD (360p) hasta 4K.
- **Descarga de Audio**: Extracción directa de audio en formatos MP3 (320kbps/192kbps), WAV (Lossless) y FLAC.
- **Historial Integrado**: Pestaña de biblioteca que guarda el registro local de tus descargas (mediante SQLite), permitiéndote abrir rápidamente las carpetas de destino.
- **Descargas en Segundo Plano**: Interfaz multihilo que no se congela mientras se descargan o convierten los archivos.

## Notas

- Al descargar formatos de muy alta calidad (como 4K), YouTube entrega el video y el audio por separado. `yt-dlp` los descarga simultáneamente y luego utiliza `ffmpeg` para unirlos. Este proceso de "conversión" puede tomar unos momentos después de que la barra de descarga llegue al 100%.
