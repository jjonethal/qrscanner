"""
QR & Barcode Scanner Application

This script is a fully functional desktop application and command-line tool.
It uses 'tkinter' for the Graphical User Interface (GUI), 'Pillow' for handling images,
and 'pyzbar' + 'pylibdmtx' for decoding various types of barcodes and QR codes.

If you are learning Python, reading this file top-to-bottom will show you:
1. How to structure a Python script.
2. How to extract core logic into standalone functions (like `scan_image`).
3. How to build a class-based Object-Oriented GUI (`QRScannerApp`).
4. How to use `argparse` to handle command-line arguments.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

# Pillow (PIL) is the standard image processing library in Python.
# Image: Core image object. ImageTk: Converts images for Tkinter.
# ImageGrab: Grabs contents from the system clipboard.
# ImageEnhance: Used to adjust contrast and sharpness.
from PIL import Image, ImageTk, ImageGrab, ImageEnhance

# pyzbar is a wrapper around the zbar library, which reads standard QR codes and 1D barcodes.
from pyzbar.pyzbar import decode

# pylibdmtx is used specifically for Data Matrix codes, which pyzbar cannot read.
# We import it as 'dmtx_decode' so it doesn't conflict with pyzbar's 'decode' function.
from pylibdmtx.pylibdmtx import decode as dmtx_decode

import os
import argparse
import sys

def scan_image(pil_img):
    """
    Core logic function to extract QR/Barcodes from a Pillow Image object.
    
    Args:
        pil_img: A PIL.Image object.
        
    Returns:
        A list of strings containing the decoded text and format (e.g., "[QRCODE] Hello World").
    """
    # 1. Image Preprocessing
    # Ensure the image is in RGB format before we start processing it. 
    # Some PNGs are RGBA (with transparency) which can confuse the decoders.
    if pil_img.mode != 'RGB':
        pil_img = pil_img.convert('RGB')
        
    decoded_objects = []
    
    # 2. Generator Function
    # 'yield' creates a generator. Instead of returning all images at once and taking up
    # lots of memory, this function yields one variation of the image at a time.
    def get_variations(img):
        # Yield the original image first. Most of the time, this works perfectly!
        yield img
        
        # Convert to grayscale ('L' mode stands for Luminance).
        gray = img.convert('L')
        yield gray
        
        # Try increasing contrast and sharpness to make blurry edges pop.
        yield ImageEnhance.Contrast(gray).enhance(2.0)
        yield ImageEnhance.Sharpness(gray).enhance(2.0)
        
        w, h = img.size
        
        # If the image is very small, we scale it up.
        # LANCZOS is a high-quality resampling filter that reduces pixelation.
        if w < 500 and h < 500:
            yield gray.resize((w * 2, h * 2), Image.Resampling.LANCZOS)
            yield gray.resize((int(w * 2.5), int(h * 2.5)), Image.Resampling.LANCZOS)
        
        # If the image is huge, the scanner might fail because the blocks are too big.
        # So we scale it down to help the algorithms detect the patterns.
        if w > 800 or h > 800:
            yield gray.resize((w // 2, h // 2), Image.Resampling.LANCZOS)
            yield gray.resize((w // 3, h // 3), Image.Resampling.LANCZOS)
            
        # Finally, try a pure black-and-white (Binarized) version.
        # lambda x: ... is an anonymous inline function. It turns dark grays to black (0) and light to white (255).
        yield gray.point(lambda x: 0 if x < 128 else 255, '1')

    try:
        # Loop over our generator. This allows us to "try" different image tweaks
        # until the decoders finally find something.
        for variation in get_variations(pil_img):
            # Try to decode standard QR/Barcodes
            decoded_objects = list(decode(variation))
            
            # If pyzbar found something, break out of the loop immediately!
            # We don't want to waste time trying other variations.
            if decoded_objects:
                break
            
            # If pyzbar failed, let's try the Data Matrix scanner.
            try:
                # We use a nested try-except block here because some older versions
                # of pylibdmtx do not support the 'timeout' parameter.
                try:
                    # Timeout prevents the app from freezing on huge, complex images.
                    dmtx_objects = dmtx_decode(variation, timeout=500)
                except TypeError:
                    # Fallback if timeout is not supported.
                    dmtx_objects = dmtx_decode(variation)
                    
                # If the Data Matrix scanner found something, add it and break out!
                if dmtx_objects:
                    decoded_objects.extend(dmtx_objects)
                    break
            except Exception as ex:
                pass # Ignore Data Matrix errors and move to the next variation
                
    except Exception as e:
        # Catch any catastrophic decoding errors and return them as a string.
        return [f"Error decoding image: {e}"]
        
    # If we finished the loop and still have an empty list...
    if not decoded_objects:
        return ["No QR code or barcode found."]
        
    # 3. Format the Results
    results = []
    seen = set() # A set is used to prevent duplicate text entries.
    
    for obj in decoded_objects:
        # The data is returned as bytes, so we must decode it into a standard UTF-8 string.
        data = obj.data.decode('utf-8')
        
        # Only add the result if we haven't seen this exact text before.
        if data not in seen:
            seen.add(data)
            # Use getattr to safely get the 'type' attribute, defaulting to 'Data Matrix' if it doesn't exist.
            code_type = getattr(obj, 'type', 'Data Matrix')
            results.append(f"[{code_type}] {data}")
        
    return results


class QRScannerApp:
    """
    The main Graphical User Interface (GUI) class using Tkinter.
    Organizing GUI code into a class keeps variables encapsulated in 'self'.
    """
    def __init__(self, root):
        self.root = root # 'root' is the main window object created by tk.Tk()
        
        # Basic window configuration
        self.root.title("QR & Barcode Scanner")
        self.root.geometry("600x700")
        self.root.configure(bg="#2e2e2e")
        
        # Here we define "Style Tokens" (colors and fonts) as variables.
        # This makes it very easy to change the theme later.
        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        self.btn_color = "#4a4a4a"
        self.btn_fg = "#ffffff"
        self.font = ("Inter", 11)
        self.title_font = ("Inter", 16, "bold")
        
        # Build the user interface components
        self.setup_ui()
        
    def setup_ui(self):
        """Creates and places all the buttons, labels, and text boxes."""
        
        # --- Title Label ---
        title_lbl = tk.Label(self.root, text="QR & Barcode Scanner", font=self.title_font, bg=self.bg_color, fg=self.fg_color)
        title_lbl.pack(pady=15) # .pack() is a layout manager that stacks elements vertically or horizontally.
        
        # --- Image Display Area ---
        # A Frame acts as a container for other widgets.
        self.img_frame = tk.Frame(self.root, bg="#1e1e1e", width=500, height=400)
        self.img_frame.pack(pady=10, padx=20)
        self.img_frame.pack_propagate(False) # Prevents the frame from shrinking to fit its contents.
        
        self.img_label = tk.Label(self.img_frame, bg="#1e1e1e", text="No Image Selected", fg="#888888", font=self.font)
        self.img_label.pack(expand=True, fill=tk.BOTH)
        
        # --- Buttons Frame ---
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(pady=10)
        
        # Note the 'command=self.open_image' argument. This tells the button what function to run when clicked.
        self.btn_open = tk.Button(btn_frame, text="Open Image", font=self.font, bg=self.btn_color, fg=self.btn_fg, command=self.open_image, relief=tk.FLAT, padx=10, pady=5)
        self.btn_open.grid(row=0, column=0, padx=10) # .grid() aligns widgets in rows and columns like a spreadsheet.
        
        self.btn_paste = tk.Button(btn_frame, text="Paste Image", font=self.font, bg=self.btn_color, fg=self.btn_fg, command=self.paste_image, relief=tk.FLAT, padx=10, pady=5)
        self.btn_paste.grid(row=0, column=1, padx=10)
        
        # --- Results Area ---
        res_lbl = tk.Label(self.root, text="Decoded Result:", font=self.font, bg=self.bg_color, fg=self.fg_color)
        res_lbl.pack(anchor="w", padx=20) # 'anchor="w"' pushes the text to the West (left side).
        
        self.text_result = tk.Text(self.root, height=5, font=self.font, bg="#1e1e1e", fg=self.fg_color, relief=tk.FLAT, wrap=tk.WORD)
        self.text_result.pack(fill=tk.X, padx=20, pady=5)
        
        self.btn_copy = tk.Button(self.root, text="Copy Text", font=self.font, bg=self.btn_color, fg=self.btn_fg, command=self.copy_text, relief=tk.FLAT, padx=10, pady=5)
        self.btn_copy.pack(pady=5)
        
    def display_image(self, pil_img):
        """Scales the image down to fit the UI and displays it."""
        max_size = (500, 400)
        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS) # .thumbnail modifies the image in-place.
        
        # Tkinter requires images to be converted into a PhotoImage object.
        self.tk_image = ImageTk.PhotoImage(pil_img) 
        self.img_label.config(image=self.tk_image, text="") # Update the label to show the image instead of text.
        
    def process_image(self, pil_img):
        """Bridge between the GUI and the core scanner logic."""
        self.display_image(pil_img.copy())
        
        # Clear the text box and show a loading message
        self.text_result.delete("1.0", tk.END)
        self.text_result.insert(tk.END, "Scanning...")
        self.root.update() # Force Tkinter to redraw the screen immediately so the user sees "Scanning..."
        
        # Call our standalone function!
        results = scan_image(pil_img)
            
        # Clear the loading message and insert the final results, joined by newlines (\n).
        self.text_result.delete("1.0", tk.END)
        self.text_result.insert(tk.END, "\n".join(results))
        
    def open_image(self):
        """Triggered when 'Open Image' is clicked."""
        # Open a native Windows/Linux file selector dialog
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            try:
                img = Image.open(file_path)
                self.process_image(img)
            except Exception as e:
                # messagebox creates a popup dialog for errors
                messagebox.showerror("Error", f"Failed to open image:\n{e}")
                
    def paste_image(self):
        """Triggered when 'Paste Image' is clicked."""
        try:
            # Grabs whatever is currently on the system clipboard
            img = ImageGrab.grabclipboard()
            
            if img is None:
                messagebox.showinfo("Paste", "No image found in clipboard.")
                return
                
            # Sometimes when you copy a file in Windows Explorer, the clipboard contains
            # a list of file paths instead of raw image data. We handle that edge case here:
            if isinstance(img, list):
                if img and os.path.exists(img[0]):
                    img = Image.open(img[0])
                else:
                    messagebox.showinfo("Paste", "Clipboard contains unsupported data.")
                    return
                    
            # If it's a valid PIL Image, process it!
            if isinstance(img, Image.Image):
                self.process_image(img)
            else:
                messagebox.showinfo("Paste", "Clipboard does not contain a valid image.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste image:\n{e}")

    def copy_text(self):
        """Copies the contents of the text box back to the system clipboard."""
        # Extract text from line 1, character 0 ("1.0") to the END. .strip() removes trailing whitespace.
        text = self.text_result.get("1.0", tk.END).strip()
        
        if text and text != "No QR code or barcode found." and not text.startswith("Error decoding"):
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update() # Required in Tkinter to finalize the clipboard transfer
            messagebox.showinfo("Copied", "Text copied to clipboard.")


def main():
    """
    The entry point of the script.
    It uses argparse to figure out if the user ran the script from a terminal with arguments.
    """
    # argparse automatically builds a beautiful help menu if you type `python qrscanner.py -h`
    parser = argparse.ArgumentParser(description="QR & Barcode Scanner")
    parser.add_argument("image_path", nargs="?", help="Path to an image file to scan. If omitted, launches the GUI.")
    args = parser.parse_args()

    if args.image_path:
        # CLI Mode: An image path was provided!
        if not os.path.exists(args.image_path):
            print(f"Error: File not found: {args.image_path}")
            sys.exit(1) # Exit with an error code
            
        try:
            img = Image.open(args.image_path)
        except Exception as e:
            print(f"Error: Failed to open image: {e}")
            sys.exit(1)
            
        print(f"Scanning {args.image_path}...")
        results = scan_image(img)
        for res in results:
            print(res)
    else:
        # GUI Mode: No arguments provided, launch the Tkinter window.
        root = tk.Tk()
        app = QRScannerApp(root)
        root.mainloop() # This starts the infinite event loop that keeps the window open.

# This is a classic Python idiom.
# It ensures that main() is only called if this script is executed directly 
# (e.g. `python qrscanner.py`), and NOT if it is imported as a module into another script.
if __name__ == "__main__":
    main()
