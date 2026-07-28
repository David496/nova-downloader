# Nova Downloader

Nova Downloader es una aplicación de escritorio multiplataforma diseñada para la descarga y reproducción en línea de contenido multimedia en alta calidad. Desarrollada en Python utilizando **Flet** y **yt-dlp**, ofrece una arquitectura asíncrona de alto rendimiento, bajo consumo de recursos y una interfaz gráfica optimizada en modo oscuro permanente.

> Desarrollado por **David496**

---

## Características Principales

### 1. Reproductor en Línea (Online Streaming)
* **Reproducción Directa sin Descarga**: Motor de audio desarrollado sobre **PySide6 (QtMultimedia)** que permite escuchar canciones en streaming directo sin consumir almacenamiento local.
* **Búsqueda y Selección Manual**: Interfaz interactiva para explorar canciones o listas de reproducción y seleccionar qué tema escuchar.
* **Renovación Automática de Enlaces Expira**: Gestión transparente de enlaces CDN de YouTube que renueva tokens expirados sin interrumpir la cola de reproducción.
* **Micro-interacciones Táctiles**: Iluminación fluida y respuestas visuales al interactuar con las pistas de la cola de reproducción.
* **Descarga Directa desde la Cola**: Opción para guardar cualquier pista en calidad MP3 a 320 kbps con metadatos incrustados durante la reproducción.

### 2. Gestor de Descargas Multimedia
* **Incrustación de Metadatos y Carátulas**: Asignación automática de etiquetas ID3v2 (título, artista) e integración de portadas de álbum en formato JPG/PNG para archivos MP3 y M4A.
* **Soporte de Subtítulos para Videos**: Incrustación de subtítulos multilingües dentro del contenedor MP4 (`FFmpegEmbedSubtitle`) o guardado independiente en formato `.srt` (exclusivo para descargas de video).
* **Gestión de Listas de Reproducción**: Selección individual o masiva de videos dentro de listas de reproducción públicas.
* **Descargas Asíncronas en Segundo Plano**: Control del flujo de descargas sin bloqueo del hilo principal de la interfaz de usuario.

### 3. Interfaz y Experiencia de Usuario
* **Modo Oscuro Permanente**: Interfaz bloqueada en tema oscuro de alto contraste para minimizar la fatiga visual.
* **Biblioteca y Historial Integrado**: Registro local persistente mediante SQLite con validación en tiempo real del archivo en disco (`os.path.exists`), permitiendo filtrar, buscar y reproducir contenido local descargado.
* **Ejecución Silenciosa y Portabilidad**: Incluye un ejecutable en VBScript (`NovaDownloader.vbs`) para iniciar la aplicación sin abrir ventanas de consola adicionales, así como un script de creación de acceso directo (`CrearAccesoDirecto.vbs`).

---

## Requisitos del Sistema

* **Python 3.10** o superior.
* **FFmpeg**: Necesario para el procesamiento de audio, extracción de portadas, incrustación de subtítulos y combinación de formatos de video HD/4K.
  * Instalación en Windows mediante PowerShell:
    ```powershell
    winget install ffmpeg
    ```

---

## Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd app
   ```

2. **Crear y activar el entorno virtual**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instalar dependencias requeridas**:
   ```powershell
   pip install -r requirements.txt
   ```

---

## Formas de Ejecución

* **Modo Recomendado (Silencioso en Windows)**:
  Ejecutar el archivo `NovaDownloader.vbs` ubicado en la raíz del proyecto para iniciar el programa sin ventana de terminal.

* **Crear Acceso Directo en el Escritorio**:
  Ejecutar el script `CrearAccesoDirecto.vbs` para generar un acceso directo con el icono oficial de Nova Downloader en el Escritorio.

* **Desde la Línea de Comandos**:
  ```powershell
  python main_flet.py
  ```

---

## Arquitectura Técnica

* **Interfaz Gráfica (UI)**: [Flet](https://flet.dev/) (Flutter engine sobre Python).
* **Motor de Audio**: [PySide6 QtMultimedia](https://wiki.qt.io/Qt_for_Python).
* **Motor de Extracción**: [yt-dlp](https://github.com/yt-dlp/yt-dlp) + [FFmpeg](https://ffmpeg.org/).
* **Base de Datos**: SQLite3.
* **Procesamiento de Imágenes**: Pillow.

---

## Licencia y Uso

Proyecto concebido para uso personal y educativo. El usuario es responsable de garantizar el cumplimiento de los términos de servicio de las plataformas origen y de las leyes de propiedad intelectual aplicables.
