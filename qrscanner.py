import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab, ImageEnhance
from pyzbar.pyzbar import decode
from pylibdmtx.pylibdmtx import decode as dmtx_decode
import os

class QRScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR & Barcode Scanner")
        self.root.geometry("600x700")
        self.root.configure(bg="#2e2e2e")
        
        # Style configurations
        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        self.btn_color = "#4a4a4a"
        self.btn_fg = "#ffffff"
        self.font = ("Inter", 11)
        self.title_font = ("Inter", 16, "bold")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_lbl = tk.Label(self.root, text="QR & Barcode Scanner", font=self.title_font, bg=self.bg_color, fg=self.fg_color)
        title_lbl.pack(pady=15)
        
        # Image Display Area
        self.img_frame = tk.Frame(self.root, bg="#1e1e1e", width=500, height=400)
        self.img_frame.pack(pady=10, padx=20)
        self.img_frame.pack_propagate(False) # Don't shrink
        
        self.img_label = tk.Label(self.img_frame, bg="#1e1e1e", text="No Image Selected", fg="#888888", font=self.font)
        self.img_label.pack(expand=True, fill=tk.BOTH)
        
        # Buttons Frame
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(pady=10)
        
        self.btn_open = tk.Button(btn_frame, text="Open Image", font=self.font, bg=self.btn_color, fg=self.btn_fg, command=self.open_image, relief=tk.FLAT, padx=10, pady=5)
        self.btn_open.grid(row=0, column=0, padx=10)
        
        self.btn_paste = tk.Button(btn_frame, text="Paste Image", font=self.font, bg=self.btn_color, fg=self.btn_fg, command=self.paste_image, relief=tk.FLAT, padx=10, pady=5)
        self.btn_paste.grid(row=0, column=1, padx=10)
        
        # Results Area
        res_lbl = tk.Label(self.root, text="Decoded Result:", font=self.font, bg=self.bg_color, fg=self.fg_color)
        res_lbl.pack(anchor="w", padx=20)
        
        self.text_result = tk.Text(self.root, height=5, font=self.font, bg="#1e1e1e", fg=self.fg_color, relief=tk.FLAT, wrap=tk.WORD)
        self.text_result.pack(fill=tk.X, padx=20, pady=5)
        
        self.btn_copy = tk.Button(self.root, text="Copy Text", font=self.font, bg=self.btn_color, fg=self.btn_fg, command=self.copy_text, relief=tk.FLAT, padx=10, pady=5)
        self.btn_copy.pack(pady=5)
        
    def display_image(self, pil_img):
        # Resize image to fit
        max_size = (500, 400)
        # Using LANCZOS for resizing
        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        self.tk_image = ImageTk.PhotoImage(pil_img)
        self.img_label.config(image=self.tk_image, text="")
        
    def process_image(self, pil_img):
        self.display_image(pil_img.copy())
        
        self.text_result.delete("1.0", tk.END)
        self.text_result.insert(tk.END, "Scanning...")
        self.root.update()
        
        # Ensure we start with RGB
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')
            
        decoded_objects = []
        
        # Helper to yield multiple image variations to improve recognition 
        def get_variations(img):
            yield img
            gray = img.convert('L')
            yield gray
            yield ImageEnhance.Contrast(gray).enhance(2.0)
            yield ImageEnhance.Sharpness(gray).enhance(2.0)
            
            w, h = img.size
            yield gray.resize((w * 2, h * 2), Image.Resampling.LANCZOS)
            yield gray.resize((int(w * 2.5), int(h * 2.5)), Image.Resampling.LANCZOS)
            
            if w > 800 or h > 800:
                yield gray.resize((w // 2, h // 2), Image.Resampling.LANCZOS)
                yield gray.resize((w // 3, h // 3), Image.Resampling.LANCZOS)
                
            yield gray.point(lambda x: 0 if x < 128 else 255, '1')

        try:
            for variation in get_variations(pil_img):
                decoded_objects = list(decode(variation))
                
                # Try Data Matrix decoding as well
                try:
                    dmtx_objects = dmtx_decode(variation)
                    decoded_objects.extend(dmtx_objects)
                except Exception as ex:
                    pass
                
                if decoded_objects:
                    break # Found something!
        except Exception as e:
            self.text_result.delete("1.0", tk.END)
            self.text_result.insert(tk.END, f"Error decoding image: {e}")
            return
            
        self.text_result.delete("1.0", tk.END)
        
        if not decoded_objects:
            self.text_result.insert(tk.END, "No QR code or barcode found.")
            return
            
        results = []
        seen = set()
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            if data not in seen:
                seen.add(data)
                code_type = getattr(obj, 'type', 'Data Matrix')
                results.append(f"[{code_type}] {data}")
            
        self.text_result.insert(tk.END, "\n".join(results))
        
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            try:
                img = Image.open(file_path)
                self.process_image(img)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image:\n{e}")
                
    def paste_image(self):
        try:
            img = ImageGrab.grabclipboard()
            if img is None:
                messagebox.showinfo("Paste", "No image found in clipboard.")
                return
                
            # If a list of files was copied instead of an image
            if isinstance(img, list):
                if img and os.path.exists(img[0]):
                    img = Image.open(img[0])
                else:
                    messagebox.showinfo("Paste", "Clipboard contains unsupported data.")
                    return
                    
            if isinstance(img, Image.Image):
                self.process_image(img)
            else:
                messagebox.showinfo("Paste", "Clipboard does not contain a valid image.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste image:\n{e}")

    def copy_text(self):
        text = self.text_result.get("1.0", tk.END).strip()
        if text and text != "No QR code or barcode found." and not text.startswith("Error decoding"):
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update() # Keep it on clipboard
            messagebox.showinfo("Copied", "Text copied to clipboard.")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRScannerApp(root)
    root.mainloop()
