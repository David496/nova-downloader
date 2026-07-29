# Nova Downloader

[![Última Versión](https://img.shields.io/github/v/release/David496/nova-downloader?color=8A2BE2&label=Versi%C3%B3n)](https://github.com/David496/nova-downloader/releases/latest)
[![Descargar para Windows](https://img.shields.io/badge/Descargar-Windows_.zip-8A2BE2?style=for-the-badge&logo=windows)](https://github.com/David496/nova-downloader/releases/latest/download/NovaDownloader-Windows-x64.zip)

Nova Downloader es una aplicación de escritorio multiplataforma diseñada para la descarga y reproducción en línea de contenido multimedia en alta calidad. Desarrollada en Python utilizando **Flet**, **PySide6 (QtMultimedia)** y **yt-dlp**, ofrece una arquitectura asíncrona de alto rendimiento, bajo consumo de recursos y una interfaz gráfica optimizada en modo oscuro permanente.

> Desarrollado por **David496**

---

## 🚀 Guía de Instalación y Uso

Elige la opción que prefieras según tu perfil de usuario:

### 📦 Opción 1: Ejecutar la App Portable (Para Usuarios Finales)
No requiere tener Python instalado ni ejecutar comandos.

1. **[Descargar Nova Downloader para Windows (.zip)](https://github.com/David496/nova-downloader/releases/latest/download/NovaDownloader-Windows-x64.zip)**.
2. Extrae el archivo `.zip` en la carpeta que desees en tu PC (ejemplo: `C:\NovaDownloader`).
3. Ejecuta **`NovaDownloader.exe`** para abrir la aplicación.
   * ⚠️ **Nota Importante**: Mantén la carpeta `_internal` en la misma ubicación junto al ejecutable `.exe`. 
   * 💡 **Tip para el Escritorio**: Haz clic derecho sobre `NovaDownloader.exe` ➔ **Enviar a** ➔ **Escritorio (crear acceso directo)** para abrir la app desde tu pantalla principal.

---

### 💻 Opción 2: Ejecución desde el Código Fuente (Para Desarrolladores)

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/David496/nova-downloader.git
   cd app
   ```

2. **Requisitos previos (FFmpeg)**:
   ```powershell
   winget install ffmpeg
   ```

3. **Crear y activar el entorno virtual**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

4. **Instalar dependencias**:
   ```powershell
   pip install -r requirements.txt
   ```

5. **Ejecutar la aplicación**:
   * **Modo estándar**:
     ```powershell
     python main_flet.py
     ```
   * **Modo silencioso (sin ventana de consola negra)**:
     Doble clic sobre el archivo `NovaDownloader.vbs`.
   * **Crear acceso directo en Escritorio**:
     Doble clic sobre `CrearAccesoDirecto.vbs`.

---

## Características Principales

### 1. Reproductor en Línea (Online Streaming)
* **Reproducción Directa sin Descarga**: Motor de audio desarrollado sobre **PySide6 (QtMultimedia)** con pre-caché de ultra-velocidad que permite escuchar canciones en streaming directo con cero interrupciones o cortes.
* **Sincronización Dinámica de Audio**: Detección automática del dispositivo predeterminado de Windows (pantalla HDMI, parlantes o audífonos) con conmutación en tiempo real.
* **Búsqueda y Selección Manual**: Interfaz interactiva para explorar canciones o listas de reproducción y seleccionar qué tema escuchar.
* **Descarga Directa desde la Cola**: Opción para guardar cualquier pista en calidad MP3 a 320 kbps con carátula e ID3v2 incrustados durante la reproducción.

### 2. Gestor de Descargas Multimedia
* **Incrustación de Metadatos y Carátulas (Mutagen & FFmpeg)**: Asignación automática de etiquetas ID3v2/MP4 (título, artista) e integración de portadas de álbum en formato JPG para archivos MP3 y M4A sin dejar imágenes temporales en disco.
* **Soporte de Subtítulos para Videos**: Incrustación de subtítulos multilingües dentro del contenedor MP4 (`FFmpegEmbedSubtitle`) o guardado independiente en formato `.srt` (exclusivo para descargas de video).
* **Gestión de Listas de Reproducción**: Selección individual o masiva de videos dentro de listas de reproducción públicas con barra de progreso en tiempo real y numeración limpia de archivos.
* **Descargas Asíncronas en Segundo Plano**: Control del flujo de descargas sin bloqueo del hilo principal de la interfaz de usuario.

### 3. Interfaz y Experiencia de Usuario
* **Modo Oscuro Permanente**: Interfaz visual estilizada en tema oscuro con capsules de selección en tono violeta y micro-animaciones táctiles en botones y listas.
* **Biblioteca e Historial Integrado**: Registro local persistente mediante SQLite con validación en tiempo real del archivo en disco (`os.path.exists`) y filtrado instantáneo en memoria RAM.

---

## ⚙️ Compilación Automática (CI/CD)

El proyecto incluye una automatización completa mediante **GitHub Actions** (`.github/workflows/build_release.yml`):
* Cada vez que se suben cambios (`git push`) a la rama `main` o se publica una etiqueta de versión (`tag`), GitHub compila automáticamente el ejecutable independiente en Windows y publica el paquete `.zip` en la sección de **GitHub Releases**.

---

## 📚 Arquitectura Técnica

* **Interfaz Gráfica (UI)**: [Flet](https://flet.dev/) (Engine de Flutter sobre Python).
* **Motor de Audio**: [PySide6 QtMultimedia](https://wiki.qt.io/Qt_for_Python).
* **Motor de Extracción**: [yt-dlp](https://github.com/yt-dlp/yt-dlp) + [FFmpeg](https://ffmpeg.org/).
* **Etiquetado de Audio**: [Mutagen](https://mutagen.readthedocs.io/).
* **Base de Datos**: SQLite3.
* **Procesamiento de Imágenes**: Pillow.

---

## 📄 Licencia y Uso

Proyecto concebido para uso personal y educativo. El usuario es responsable de garantizar el cumplimiento de los términos de servicio de las plataformas origen y de las leyes de propiedad intelectual aplicables.
