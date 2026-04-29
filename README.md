# QR-Scanner
A robust, cross-platform QR-Code and Barcode scanner application.

## Overview
This is a lightweight Python application built to reliably scan QR codes, Data Matrix codes, and traditional 1D barcodes from images. It features both a modern, user-friendly Graphical User Interface (GUI) and a quick Command-Line Interface (CLI) for terminal users. 

Built with beginners in mind, the source code (`qrscanner.py`) is heavily documented and serves as an educational tool for learning Python GUI development, image processing, generator functions, and CLI argument parsing.

## Features
- **Dual Interface**: Seamlessly switch between a visual GUI and a headless CLI.
- **Advanced Recognition**: If a code is blurry, too small, or too large, the app automatically generates multiple enhanced variations (grayscale, high contrast, resized, binarized) to force a successful read.
- **Multi-Format Support**: Reads standard QR codes, EAN/UPC barcodes, and Data Matrix codes.
- **Clipboard Integration**: Paste images directly from your system clipboard or copy decoded text with a single click.
- **Standalone Setup**: Includes an `init.bat` script that automatically handles creating virtual environments and installing dependencies.

## Installation
The project includes a bootstrap batch script that handles all setup for you.

1. Clone or download this repository.
2. Run the initialization script in your terminal:
   ```cmd
   init.bat
   ```
   *(This will automatically create a Python virtual environment named `qrenv` and install the required dependencies like `Pillow`, `pyzbar`, and `pylibdmtx`).*

## Usage

### 1. Graphical User Interface (GUI)
To launch the visual application, simply run the batch file with no arguments:
```cmd
init.bat
```
- **Open Image**: Opens a file explorer to select an image from your computer.
- **Paste Image**: Scans whatever image is currently copied to your system clipboard (useful for taking quick screenshots using `Win + Shift + S`).
- **Copy Text**: Puts the successfully decoded text into your clipboard.

### 2. Command Line Interface (CLI)
You can use the scanner headless directly from your terminal. Just pass the path of the image you want to scan:
```cmd
init.bat path\to\image.png
```
Or, if you are working within the activated Python environment:
```cmd
python qrscanner.py path\to\image.png
```
The decoded text will be printed instantly to your terminal.

## Dependencies
- `tkinter`: Built-in Python library for the GUI.
- `Pillow` (PIL): For robust cross-platform image handling and resizing.
- `pyzbar`: For decoding QR codes and 1D barcodes.
- `pylibdmtx`: Specifically for decoding Data Matrix codes.
- `setuptools`: Included to ensure compatibility with Python 3.12+.
