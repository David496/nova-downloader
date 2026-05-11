# Nova Downloader

Nova Downloader es una aplicación de escritorio moderna para descargar videos y audios, potenciada por **Flet (Flutter for Python)**. Ofrece una interfaz fluida, elegante y totalmente asíncrona.

> [!IMPORTANT]
> **Nota:** Por el momento, la aplicación solo es compatible con la descarga de contenido de **YouTube**.

## ⚠️ Descargo de Responsabilidad (Disclaimer)

Este es un **proyecto puramente educativo y de uso personal**. El software se proporciona "tal cual", sin garantía de ningún tipo. Los desarrolladores no se hacen responsables del uso que los usuarios den a esta herramienta ni del contenido descargado. Asegúrate de cumplir con los términos de servicio de la plataforma y las leyes de derechos de autor de tu país.

## 🚀 Mejoras de la Versión Final (Flet Async)

- **Motor Asíncrono Real**: La interfaz nunca se congela durante el análisis o la descarga.
- **Gestión Inteligente de Playlists**: Elige individualmente qué videos de una playlist quieres bajar.
- **Progreso en Tiempo Real**: Barras de carga fluidas y limpias (sin caracteres extraños).
- **Interfaz Reactiva**: Cambios instantáneos de tema (Oscuro/Claro) e idioma desde Ajustes.
- **Visualización Premium**: Miniaturas en alta resolución y metadatos detallados (duración, autor, vistas).

## Requisitos Previos

- Python 3.12 o superior.
- **FFmpeg**: Requerido para la conversión de formatos de audio y para combinar pistas de video de alta calidad.
  - Instalación en Windows vía `winget`:
    ```powershell
    winget install ffmpeg
    ```

## Instalación y Ejecución

1. **Clona el repositorio**:
   ```bash
   git clone <URL_DE_TU_REPOSITORIO>
   cd app
   ```

2. **Crea y activa un entorno virtual**:
   ```powershell
   python -m venv venv
   # Activar en Windows:
   .\venv\Scripts\activate
   ```

3. **Instala las dependencias**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Ejecuta la aplicación**:
   ```powershell
   python main_flet.py
   ```

## Características Técnicas

- **Basado en Flet**: Renderizado de alta fidelidad con Material Design 3.
- **Arquitectura Async**: Implementación robusta con `asyncio` y `threading`.
- **Core Potente**: Utiliza `yt-dlp` para máxima compatibilidad.
- **Historial Local**: Base de datos SQLite para registro de descargas.

## Notas

Al descargar formatos de alta resolución (como 4K), verás el estado "Procesando archivos..." mientras `ffmpeg` une las pistas de audio y video.
