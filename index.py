import os
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageEnhance, ImageOps
import colorsys

class HSBEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HSB Image Editor")
        self.image_list = []  # List of image paths from selected folder
        self.current_images = []  # Stores tuples of (original, processed) images
        self.real_time_toggle = False  # For the toggle button

        self.create_ui()

    def create_ui(self):
        # Folder selection button
        folder_btn = tk.Button(self.root, text="フォルダを選択", command=self.load_images_from_folder, width=18, height=1, font=("MS Gothic", 17))
        folder_btn.pack(pady=10, padx=5)

        # Toggle button for real-time image change
        self.toggle_button = tk.Button(self.root, text="リアルタイム変換: OFF", command=self.toggle_real_time, width=24, height=1, font=("MS Gothic", 17))
        self.toggle_button.pack(pady=7, padx=5)

        # Sliders for Hue, Saturation, and Brightness (default values set)
        self.hue_slider = tk.Scale(self.root, from_=0, to=360, orient=tk.HORIZONTAL, label="Hue", command=self.update_images)
        self.hue_slider.set(0)  # Default Hue value
        self.hue_slider.pack(fill='x')

        self.saturation_slider = tk.Scale(self.root, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL, label="Saturation", command=self.update_images)
        self.saturation_slider.set(1.0)  # Default Saturation value
        self.saturation_slider.pack(fill='x')

        self.brightness_slider = tk.Scale(self.root, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL, label="Brightness", command=self.update_images)
        self.brightness_slider.set(1.0)  # Default Brightness value
        self.brightness_slider.pack(fill='x')

        # Scrollable frame for images
        self.scroll_frame = tk.Frame(self.root)
        self.scroll_frame.pack(expand=True, fill='both')

        self.canvas = tk.Canvas(self.scroll_frame)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Apply changes button
        apply_btn = tk.Button(self.root, text="変換適用", command=self.apply_changes,  width=13, height=1, font=("MS Gothic", 17))
        apply_btn.pack(pady=10, padx=5)

        # Save all images button
        save_btn = tk.Button(self.root, text="保存", command=self.save_all_images,  width=8, height=1, font=("MS Gothic", 17))
        save_btn.pack(pady=10, padx=5)

    def load_images_from_folder(self):
        """Load all images from the selected folder."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            # Get all valid image files in the folder
            self.image_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
            if self.image_list:
                self.current_images = []
                for image_path in self.image_list:
                    img = Image.open(image_path)
                    self.current_images.append((img, img.copy()))  # Store original and processed copies
                self.display_images()

    def display_images(self):
        """Display all images in a scrollable format while maintaining aspect ratio."""
        # Clear any previous images in the inner frame
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        for i, (original_img, processed_img) in enumerate(self.current_images):
            # Display original and processed image side by side in the scrollable frame
            original_img_resized = self.resize_image_to_fit(original_img)
            processed_img_resized = self.apply_hsb_changes(original_img).resize(original_img_resized.size)

            original_photo = ImageTk.PhotoImage(original_img_resized)
            processed_photo = ImageTk.PhotoImage(processed_img_resized)

            original_label = tk.Label(self.inner_frame, image=original_photo)
            original_label.image = original_photo  # Keep a reference
            original_label.grid(row=i, column=0, padx=10, pady=10)

            processed_label = tk.Label(self.inner_frame, image=processed_photo)
            processed_label.image = processed_photo  # Keep a reference
            processed_label.grid(row=i, column=1, padx=10, pady=10)

    def resize_image_to_fit(self, img, max_size=300):
        """Resize an image to fit within max_size while maintaining aspect ratio."""
        w, h = img.size
        aspect_ratio = w / h
        if w > h:
            new_w = max_size
            new_h = int(new_w / aspect_ratio)
        else:
            new_h = max_size
            new_w = int(new_h * aspect_ratio)
        return img.resize((new_w, new_h))

    def apply_hsb_changes(self, image):
        """Apply hue, saturation, and brightness changes to an image."""
        # Get slider values
        hue = self.hue_slider.get()
        saturation = self.saturation_slider.get()
        brightness = self.brightness_slider.get()

        # Adjust brightness
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness)

        # Adjust saturation
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(saturation)

        # Adjust hue
        image = self.adjust_hue(image, hue)

        return image

    def adjust_hue(self, image, hue):
        """Adjust the hue of an image."""
        # Convert image to HSV color space
        img = image.convert('RGBA')
        img_data = img.getdata()

        new_data = []
        for item in img_data:
            r, g, b, a = item
            # Convert RGB to HSV
            h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

            # Adjust hue
            h = (h + hue / 360.0) % 1.0

            # Convert HSV back to RGB
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            new_data.append((int(r * 255), int(g * 255), int(b * 255), a))

        # Create a new image with the modified data
        img.putdata(new_data)
        return img

    def apply_changes(self):
        """Apply changes to all images in the folder."""
        if self.current_images:
            for i, (original_img, _) in enumerate(self.current_images):
                processed_img = self.apply_hsb_changes(original_img)
                self.current_images[i] = (original_img, processed_img)
            self.display_images()  # Update the displayed images

    def save_all_images(self):
        """Save all processed images to a selected folder."""
        if self.current_images:
            save_folder = filedialog.askdirectory(title="Select Folder to Save Images")
            if save_folder:
                for i, (original_img, processed_img) in enumerate(self.current_images):
                    base_name = os.path.basename(self.image_list[i])
                    file_name, file_ext = os.path.splitext(base_name)
                    save_path = os.path.join(save_folder, f"processed_{file_name}{file_ext}")

                    # Convert to 'RGB' if the image is in 'RGBA' mode
                    if processed_img.mode == 'RGBA':
                        processed_img = processed_img.convert('RGB')

                    # If the file already exists, append a unique number to avoid overwriting
                    counter = 1
                    while os.path.exists(save_path):
                        save_path = os.path.join(save_folder, f"processed_{file_name}_{counter}{file_ext}")
                        counter += 1

                    processed_img.save(save_path)  # Save the processed image
                print(f"All images saved to {save_folder}!")


    def toggle_real_time(self):
        """Toggle real-time image adjustment functionality."""
        self.real_time_toggle = not self.real_time_toggle
        if self.real_time_toggle:
            self.toggle_button.config(text="リアルタイム変換: ON")
        else:
            self.toggle_button.config(text="リアルタイム変換: OFF")

    def update_images(self, event=None):
        """Update the images in real-time if the toggle is on."""
        if self.real_time_toggle:
            self.apply_changes()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x850")
    app = HSBEditorApp(root)
    root.mainloop()
