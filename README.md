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
   * ⚡ **100% Autónomo (FFmpeg incluido)**: El paquete `.zip` ya incluye los binarios portables de FFmpeg en la subcarpeta `ffmpeg/`, permitiendo unir video/audio en 1080p/4K y convertir a MP3 de inmediato sin instalar nada en Windows.
   * ⚠️ **Nota Importante**: Mantén la carpeta `_internal` y `ffmpeg` en la misma ubicación junto al ejecutable `.exe`. 
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

### 1. Reproductor en Línea & Mini-Player Global
* **Mini-Reproductor Persistente (Bottom Dock)**: Barra flotante estilo *Spotify Desktop* en la parte inferior de la ventana, visible y sincronizada en todas las pestañas (Inicio, Descargas, Biblioteca, Ajustes) con carátula, controles (Prev/Play/Next), timeline interactivo y volumen.
* **Ambient Glow Effect & Ecualizador Dinámico**: Halo de resplandor ambiental púrpura difuso detrás de la carátula y ecualizador animado en tiempo real dentro del badge de estado.
* **Reproducción Directa sin Descarga**: Motor de audio nativo basado en **PySide6 (QtMultimedia)** con pre-buffering y reconexión automática ante enlaces expirados.
* **📌 Guardado de Playlists de YouTube**: Fijado de listas de reproducción con extracción de metadatos, accesos directos y una **Ventana Modal con Buscador Integrado**.
* **Sincronización Dinámica de Audio**: Detección automática del dispositivo de salida predeterminado de Windows (HDMI, altavoces, auriculares Bluetooth) sin interrumpir la reproducción.

### 2. Gestor de Descargas Multimedia Inteligente
* **Banner Inteligente del Portapapeles**: Detección automática de enlaces compatibles en el portapapeles con opción de *Pegar y Analizar* en 1 solo clic.
* **Pill Badges Modernas**: Selectores de calidad y formato con etiquetas tipo píldora (`[ 4K UHD ]`, `[ 1080p FHD ]`, `[ MP3 320 KBPS ]`, `[ LOSSLESS ]`) y microinteracciones de elevación al pasar el cursor.
* **Incrustación de Metadatos y Carátulas**: Asignación automática de tags ID3v2/MP4 (título, artista, año) e incrustación de carátulas JPG en alta resolución sin dejar archivos temporales huérfanos.
* **Soporte de Subtítulos y Playlists**: Descarga masiva o individual de elementos de listas de reproducción públicas con barra de progreso en vivo e incrustación de subtítulos (`.srt` / `FFmpegEmbedSubtitle`).

### 3. Biblioteca Local con Reproducción Nativa
* **Alternador de Vista (Lista vs Cuadrícula / Carátulas)**: Conmutador en cabecera para alternar entre vista de lista compacta y vista en cuadrícula con tarjetas de carátula grande (190x240px).
* **Reproducción Nativa en 1 Clic**: Escucha tus canciones descargadas directamente en el reproductor interno de la aplicación sin recurrir a programas externos.
* **Base de Datos SQLite Robusta (Cero Duplicados)**: Motor de persistencia en modo WAL con deduplicación estricta por título y ruta, prevención de registros fantasma y cálculo exacto del tamaño del archivo.
* **🧹 Limpieza de Caché**: Herramienta en el panel de Ajustes para vaciar archivos temporales de streaming con un solo clic.

### 4. Sistema de Temas Épicos & Personalización Dinámica
* **7 Paletas de Color Épicas**: Cambia la atmósfera visual de la aplicación completa al instante sin reiniciar la ventana:
  - 🔮 **Nebula Violet**: Púrpura eléctrico y cyberpunk clásico original.
  - ⚡ **Cyber Matrix**: Verde esmeralda neón y terminal hacker.
  - 🩸 **Crimson Blood**: Rojo carmesí rubí y furia escarlata.
  - 🌊 **Abyssal Blue**: Azul zafiro cuántico y océano profundo.
  - 🌌 **Cosmic Cyan**: Cian glacial y turquesa aurora.
  - 👑 **Golden Eclipse**: Ámbar solar y oro cósmico de lujo.
  - 🌸 **Neon Sakura**: Magenta láser y luces de Neo-Tokio.
* **Selector Desplegable Dinámico (`ft.Dropdown`)**: Selector estilizado en Ajustes con badge interactivo de vista previa en tiempo real y persistencia inmediata.

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
