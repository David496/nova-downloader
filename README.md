# Nova Downloader

Nova Downloader es una aplicación de escritorio moderna y elegante para descargar videos y música en alta calidad, desarrollada en Python utilizando **Flet** y **yt-dlp**. Ofrece una interfaz fluida, intuitiva, compacta y totalmente asíncrona.

> **Desarrollado por David496**

---

## 🚀 Características Principales

- **Descarga de Música con Portada y Metadatos**: Incrusta automáticamente la portada del álbum (cover art) y etiquetas ID3 (título, artista, año) en archivos MP3 y M4A/AAC.
- **Soporte para Subtítulos (Solo en Videos)**: Descarga e incrusta subtítulos dentro del video MP4 (`FFmpegEmbedSubtitle`) o guárdalos como archivos independientes `.srt`. Soporta múltiples idiomas (`es`, `en`, etc.).
- **Lanzador Portátil de 1 Clic (`NovaDownloader.vbs`)**: Inicia la aplicación en segundo plano sin mostrar ninguna ventana de consola negra.
- **Icono Personalizado Transparente**: Marca visual propia en la ventana, barra de tareas de Windows y acceso directo.
- **Creador de Acceso Directo (`CrearAccesoDirecto.vbs`)**: Genera automáticamente un acceso directo en tu Escritorio de Windows con el ícono personalizado del proyecto.
- **Biblioteca en Lista Vertical**: Historial de descargas organizado en lista con:
  - Búsqueda en tiempo real por título o URL.
  - Filtros por tipo (**Música**, **Videos**, **Todos**).
  - Acciones rápidas para **reproducir/abrir archivo**, **abrir carpeta** o **eliminar del historial**.
- **Pegar enlace con 1 Clic**: Botón integrado para pegar URLs directamente desde el portapapeles.
- **Gestión Inteligente de Playlists**: Selecciona individualmente qué elementos de una lista quieres descargar.
- **Motor Asíncrono Real**: La interfaz nunca se bloquea durante el análisis, descarga o conversión con FFmpeg.
- **Diseño Compacto y Personalizable**: Cambio de tema (Oscuro/Claro) e idioma (Español/Inglés) desde el panel de Configuración.

---

## ⚠️ Descargo de Responsabilidad (Disclaimer)

Este es un **proyecto puramente educativo y de uso personal**. El software se proporciona "tal cual", sin garantía de ningún tipo. Los desarrolladores no se hacen responsables del uso que los usuarios den a esta herramienta ni del contenido descargado. Asegúrate de cumplir con los términos de servicio de la plataforma y las leyes de derechos de autor de tu país.

---

## 🛠️ Requisitos Previos

- **Python 3.10** o superior.
- **FFmpeg**: Requerido para la conversión de audio, incrustación de portadas/subtítulos y combinación de pistas 4K/HD.
  - Instalación en Windows vía `winget`:
    ```powershell
    winget install ffmpeg
    ```

---

## 📦 Instalación y Ejecución

1. **Clona el repositorio**:
   ```bash
   git clone <URL_DE_TU_REPOSITORIO>
   cd app
   ```

2. **Crea y activa un entorno virtual**:
   ```powershell
   python -m venv venv
   # En Windows (PowerShell):
   .\venv\Scripts\activate
   ```

3. **Instala las dependencias**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Ejecuta la aplicación**:
   - **Opción A (Silencioso - Recomendado sin consola)**:
     Haz doble clic en el archivo **`NovaDownloader.vbs`** en la raíz del proyecto. La aplicación se abrirá de inmediato sin mostrar ninguna ventana de consola negra.
   
   - **Opción B (Crear acceso directo en el Escritorio)**:
     Haz doble clic en **`CrearAccesoDirecto.vbs`** para colocar un acceso directo en tu Escritorio con el ícono personalizado de Nova Downloader.

   - **Opción C (Desde terminal)**:
     ```powershell
     python main_flet.py
     ```

---

## 🏗️ Arquitectura Técnica

- **Frontend / UI**: [Flet](https://flet.dev/) (Flutter renderizado en Python).
- **Core de Descargas**: [yt-dlp](https://github.com/yt-dlp/yt-dlp) + [FFmpeg](https://ffmpeg.org/).
- **Base de Datos**: SQLite (`history.db`) con deduplicación automática de registros.
- **Procesamiento de Imágenes**: Pillow (generación de icono PNG transparente y multirresolución ICO).

---

## 👤 Créditos

Desarrollado por **David496**.
