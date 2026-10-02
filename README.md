<p align="center">
  <img src="assets/icon128.png" width="96" height="96" alt="Large File Finder Logo" />
</p>

<h1 align="center">Large File Finder</h1>

<p align="center">
  <strong>A high-speed, lightweight Windows desktop utility to scan, locate, and clean up disk-hogging files.</strong>
</p>

<p align="center">
  <a href="https://github.com/bytewhisker/large-file-finder/releases"><img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white" alt="Windows" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.8+" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT License" /></a>
  <img src="https://img.shields.io/badge/Architecture-Threaded%20Async-orange?style=flat-square" alt="Threaded" />
</p>

---

## ⚡ Overview

When working with video production (Premiere Pro, After Effects), virtual machines, game assets, or software development, gigabytes of storage vanish silently into deep caches and temporary folders.

**Large File Finder** is a zero-bloat, standalone desktop utility engineered to recursively crawl drives and folders at maximum I/O speed, sorting and exposing the largest space consumers instantly.

---

## ✨ Key Features

* 🚀 **Non-Blocking Multi-Threaded Scanning:** Traverses hundreds of thousands of files across deep filesystem trees without locking or freezing the UI.
* 🎯 **Top Space Hogs at a Glance:** Automatically identifies and ranks the heaviest files with human-readable formatting (GB, MB, KB).
* 🗂️ **Smart File Type Filtering:** Instantly filter results by category:
  * **Video:** `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`
  * **Audio:** `.mp3`, `.wav`, `.aac`, `.flac`
  * **Archives:** `.zip`, `.rar`, `.7z`, `.tar.gz`, `.iso`
  * **Images & Creative Assets:** `.png`, `.jpg`, `.tiff`, `.webp`
  * **Executables & Installers:** `.exe`, `.msi`, `.bat`
  * **Documents & Code**
* 🖱️ **Explorer Integration:** Right-click any file to:
  * **Open Location:** Highlights the exact file in Windows File Explorer.
  * **Copy Full Path:** One-click path clipboard export.
  * **Safe Deletion:** Delete redundant files directly from the app with confirmation guards.
* 🎨 **Clean Dark-Mode UI:** Custom-tuned high-contrast theme built with native UI toolkits for instant startup and negligible RAM usage.

---

## 🛠️ Quick Start

### 1. Prerequisites
* Python 3.8 or higher installed on Windows.

### 2. Installation & Running

```bash
# Clone the repository
git clone https://github.com/bytewhisker/large-file-finder.git
cd large-file-finder

# Install lightweight dependencies
pip install -r requirements.txt

# Launch the app
python largest_file_finder.py
```

---

## 📦 Building a Standalone `.exe`

To package Large File Finder into a single portable Windows executable with its icon embedded:

```bash
pip install pyinstaller

pyinstaller --noconsole --onefile \
  --icon=assets/icon128.ico \
  --add-data "assets;assets" \
  --name "LargeFileFinder" \
  largest_file_finder.py
```

The compiled standalone binary will be generated in the `dist/` directory.

---

## 🏗️ Architecture & Technical Highlights

* **Thread-Safe Queue Pipeline:** Uses Python's `queue.Queue` coupled with `threading.Thread` to decouple disk I/O and recursion from Tkinter's main event loop.
* **Resilient I/O Walk:** Implements fault-tolerant traversal using `os.walk` with graceful permission error bypasses for protected system directories.
* **Zero Heavy Framework Bloat:** Runs entirely on Python's native GUI engine with minimal third-party dependencies (`Pillow`, `pyperclip`).

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

## 👨‍💻 Author

Developed by **[ByteWhisker](https://github.com/bytewhisker)**  
*Creative Tools & Systems Developer*
