# Nova Downloader

[![Última Versión](https://img.shields.io/github/v/release/David496/nova-downloader?color=8A2BE2&label=Versi%C3%B3n)](https://github.com/David496/nova-downloader/releases/latest)
[![Descargar para Windows](https://img.shields.io/badge/Descargar-Windows_.zip-8A2BE2?style=for-the-badge&logo=windows)](https://github.com/David496/nova-downloader/releases/latest/download/NovaDownloader-Windows-x64.zip)

Nova Downloader es una aplicación de escritorio multiplataforma diseñada para la descarga y reproducción en línea de contenido multimedia en alta calidad. Desarrollada en Python utilizando **Flet**, **PySide6 (QtMultimedia)** y **yt-dlp**, ofrece una arquitectura asíncrona de alto rendimiento, bajo consumo de recursos y una interfaz gráfica optimizada en modo oscuro permanente.

> Desarrollado por **David496**

---

## 🚀 Descarga Directa e Instalación Rápida

Para usar Nova Downloader sin necesidad de instalar Python ni dependencias manuales:

1. **[Descargar Nova Downloader para Windows](https://github.com/David496/nova-downloader/releases/latest/download/NovaDownloader-Windows-x64.zip)**
2. Extrae el archivo `.zip` en cualquier carpeta de tu equipo.
3. Ejecuta **`NovaDownloader.exe`** (o haz doble clic en `CrearAccesoDirecto.vbs` para enviarlo a tu Escritorio).

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
* **Ejecución Silenciosa y Portabilidad**: Ejecución nativa sin consola y scripts auxiliares (`NovaDownloader.vbs` y `CrearAccesoDirecto.vbs`).

---

## 🛠️ Requisitos del Sistema (Para Desarrollo)

* **Python 3.10** o superior.
* **FFmpeg**: Necesario para el procesamiento de audio, extracción de portadas, incrustación de subtítulos y combinación de formatos de video HD/4K.
  * Instalación en Windows mediante PowerShell:
    ```powershell
    winget install ffmpeg
    ```

---

## 💻 Instalación desde Código Fuente

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/David496/nova-downloader.git
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

4. **Ejecutar la aplicación**:
   ```powershell
   python main_flet.py
   ```

---

## ⚙️ Compilación Automática (CI/CD)

El proyecto incluye una automatización completa mediante **GitHub Actions** (`.github/workflows/build_release.yml`):
* Cada vez que se suben cambios (`git push`) a la rama `main` o se publica una etiqueta de versión (`tag`), GitHub compile automáticamente el ejecutable independiente en Windows y publica el paquete `.zip` en la sección de **GitHub Releases**.

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
