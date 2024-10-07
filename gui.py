# gui.py

import customtkinter as ctk
from customtkinter import CTkImage
from tkinter import messagebox, filedialog
import tkinter as tk
from PIL import Image
import io
import os
import requests
import time
import json

# Import API request functions
from api_requests import (
    generate_image_request_bfl,
    get_image_result_bfl,
    generate_image_request_ideogram,
    generate_image_request_stability,
    update_api_keys,
)

# Import settings functions
from settings import (
    load_api_keys,
    save_api_keys_to_env
)

# Set up the images directory
IMAGES_DIR = 'images'
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

def create_gui():
    global app
    app = ctk.CTk()
    app.geometry("1280x720")
    app.title("Image Generator")



    global history_images
    history_images = []

    # Global variables to be used across functions
    global generated_images, current_image_index
    generated_images = []
    current_image_index = ctk.IntVar(value=0)

    # Load API keys
    global BFL_API_KEY, IDEOGRAM_API_KEY, STABILITY_API_KEY
    BFL_API_KEY, IDEOGRAM_API_KEY, STABILITY_API_KEY = load_api_keys()

    # Title label
    title_label = ctk.CTkLabel(app, text="Image Generator", font=("Arial", 24, "bold"))
    title_label.pack(pady=10)

    # Create TabView
    tabview = ctk.CTkTabview(app)
    tabview.pack(pady=20, padx=20, fill='both', expand=True)

    # Create tabs
    tab1 = tabview.add("Image Generation")
    tab2 = tabview.add("Settings")
    tab3 = tabview.add("History")

    # Content frame for tab1
    content_frame = ctk.CTkFrame(tab1)
    content_frame.pack(pady=15, padx=15, fill='both', expand=True)

    # Left frame for controls
    controls_frame = ctk.CTkFrame(content_frame, width=390, height=390)
    controls_frame.pack(side='left', fill='y', padx=35, pady=35)
    controls_frame.pack_propagate(False)

    # Align all control widgets vertically within the left frame
    controls_inner_frame = ctk.CTkFrame(controls_frame)
    controls_inner_frame.pack(padx=10, pady=10, fill='both', expand=True)

    # Prompt label and entry
    prompt_label = ctk.CTkLabel(controls_inner_frame, text="Enter your image prompt:", font=("Arial", 16))
    prompt_label.pack(anchor='w', pady=5, padx=10)

    global prompt_entry
    prompt_entry = ctk.CTkEntry(controls_inner_frame, width=370, font=("Arial", 14, "bold"))
    prompt_entry.pack(anchor='w', pady=5, padx=10)

    # Number of images input
    num_images_label = ctk.CTkLabel(controls_inner_frame, text="Number of images:", font=("Arial", 16))
    num_images_label.pack(anchor='w', pady=5, padx=10)

    global num_images_slider

    num_images_slider = ctk.CTkSlider(controls_inner_frame, from_=1, to=4, number_of_steps=3, width=370,
                                      command=lambda value: num_images_value_label.configure(text=f"Selected: {int(value)}"))
    num_images_slider.set(1)
    num_images_slider.pack(anchor='w', pady=5, padx=10)

    num_images_value_label = ctk.CTkLabel(controls_inner_frame, text="Selected: 1", font=("Arial", 14))
    num_images_value_label.pack(anchor='w', pady=5, padx=10)

    # Model selection (including Ideogram and Stability models)
    model_label = ctk.CTkLabel(controls_inner_frame, text="Select model:", font=("Arial", 16))
    model_label.pack(anchor='w', pady=5, padx=10)

    global model_selection
    model_selection = ctk.CTkComboBox(
        controls_inner_frame,
        values=["flux-pro-1.1", "flux-pro", "flux-dev", "ideogram", "stable-ultra", "stable-core", "stable-sd3"],
        font=("Arial", 14)
    )
    model_selection.set("flux-dev")
    model_selection.pack(anchor='w', pady=5, padx=10)

    # Ideogram model selection
    ideogram_model_label = ctk.CTkLabel(controls_inner_frame, text="Ideogram model:", font=("Arial", 16))
    global ideogram_model_selection
    ideogram_model_selection = ctk.CTkComboBox(controls_inner_frame, values=["V_1_5", "V_2"], font=("Arial", 14))
    ideogram_model_selection.set("V_1_5")

    # Negative Prompt label and entry
    negative_prompt_label = ctk.CTkLabel(controls_inner_frame, text="Negative Prompt (optional):", font=("Arial", 16))
    global negative_prompt_entry
    negative_prompt_entry = ctk.CTkEntry(controls_inner_frame, width=370, font=("Arial", 14))

    # Aspect Ratio label and selection
    aspect_ratio_label = ctk.CTkLabel(controls_inner_frame, text="Aspect Ratio:", font=("Arial", 16))
    global aspect_ratio_selection
    aspect_ratio_selection = ctk.CTkComboBox(
        controls_inner_frame,
        values=["16:9", "1:1", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"],
        font=("Arial", 14)
    )
    aspect_ratio_selection.set("1:1")

    # Width and Height input (only for BFL models)
    size_frame = ctk.CTkFrame(controls_inner_frame, width=380)

    width_label = ctk.CTkLabel(size_frame, text="Width:", font=("Arial", 14))
    global width_entry
    width_entry = ctk.CTkEntry(size_frame, width=100, font=("Arial", 14))
    width_entry.insert(0, "1024")

    height_label = ctk.CTkLabel(size_frame, text="Height:", font=("Arial", 14))
    global height_entry
    height_entry = ctk.CTkEntry(size_frame, width=100, font=("Arial", 14))
    height_entry.insert(0, "768")

    # Function to update UI based on selected model
    def update_ui_based_on_model(event):
        selected_model = model_selection.get()
        if selected_model == "ideogram":
            # Hide width and height inputs
            size_frame.pack_forget()
            # Show Ideogram model selection
            ideogram_model_label.pack(anchor='w', pady=5, padx=10)
            ideogram_model_selection.pack(anchor='w', pady=5, padx=10)
            # Hide aspect ratio and negative prompt
            negative_prompt_label.pack_forget()
            negative_prompt_entry.pack_forget()
            aspect_ratio_label.pack_forget()
            aspect_ratio_selection.pack_forget()
        elif selected_model.startswith("stable"):
            # Hide width and height inputs
            size_frame.pack_forget()
            # Hide Ideogram model selection
            ideogram_model_label.pack_forget()
            ideogram_model_selection.pack_forget()
            # Show aspect ratio and negative prompt
            negative_prompt_label.pack(anchor='w', pady=5, padx=10)
            negative_prompt_entry.pack(anchor='w', pady=5, padx=10)
            aspect_ratio_label.pack(anchor='w', pady=5, padx=10)
            aspect_ratio_selection.pack(anchor='w', pady=5, padx=10)
        else:
            # Show width and height inputs
            size_frame.pack(anchor='w', pady=5, padx=10)
            width_label.grid(row=0, column=0, padx=5)
            width_entry.grid(row=0, column=1, padx=5)
            height_label.grid(row=0, column=2, padx=5)
            height_entry.grid(row=0, column=3, padx=5)
            # Hide Ideogram model selection
            ideogram_model_label.pack_forget()
            ideogram_model_selection.pack_forget()
            # Hide aspect ratio and negative prompt
            negative_prompt_label.pack_forget()
            negative_prompt_entry.pack_forget()
            aspect_ratio_label.pack_forget()
            aspect_ratio_selection.pack_forget()

    model_selection.bind("<<ComboboxSelected>>", update_ui_based_on_model)
    update_ui_based_on_model(None)  # Initialize the UI

    # Initially hide these elements
    negative_prompt_label.pack_forget()
    negative_prompt_entry.pack_forget()
    aspect_ratio_label.pack_forget()
    aspect_ratio_selection.pack_forget()

    # Generate button
    generate_button = ctk.CTkButton(controls_inner_frame, text="Generate Images", command=generate_images, width=200,
                                    font=("Arial", 14, "bold"))
    generate_button.pack(anchor='w', pady=10, padx=10)

    # Right frame for image display
    image_frame = ctk.CTkFrame(content_frame, width=390, height=390, corner_radius=10)
    image_frame.pack(side='right', padx=30, pady=30, fill='both', expand=True)
    image_frame.pack_propagate(False)

    # Loading label
    global loading_label
    loading_label = ctk.CTkLabel(image_frame, text="", font=("Arial", 12))
    loading_label.pack(anchor='w', pady=5)

    global image_label
    image_label = ctk.CTkLabel(image_frame, text="", anchor="center")
    image_label.pack(expand=True)

    # Save button
    save_button = ctk.CTkButton(image_frame, text="Save Image", command=save_image, width=200,
                                font=("Arial", 14, "bold"))
    save_button.pack(pady=5)

    # Navigation buttons
    navigation_frame = ctk.CTkFrame(image_frame, fg_color="transparent")
    navigation_frame.pack(pady=10)

    prev_button = ctk.CTkButton(navigation_frame, text="Previous", command=prev_image, width=90,
                                font=("Arial", 12, "bold"))
    prev_button.grid(row=0, column=0, padx=10)

    next_button = ctk.CTkButton(navigation_frame, text="Next", command=next_image, width=90,
                                font=("Arial", 12, "bold"))
    next_button.grid(row=0, column=1, padx=10)

    # Content frame for tab2 (Settings)
    settings_frame = ctk.CTkFrame(tab2)
    settings_frame.pack(pady=20, padx=20, fill='both', expand=True)

    # BFL API Key label and entry
    bfl_api_key_label = ctk.CTkLabel(settings_frame, text="Enter your BFL API key:", font=("Arial", 16))
    bfl_api_key_label.pack(anchor='w', pady=5, padx=10)

    global bfl_api_key_entry
    bfl_api_key_entry = ctk.CTkEntry(settings_frame, width=500, font=("Arial", 14, "bold"))
    bfl_api_key_entry.pack(anchor='w', pady=5, padx=10)

    # Set the entry to the current BFL API key
    if BFL_API_KEY:
        bfl_api_key_entry.insert(0, BFL_API_KEY)

    # Ideogram API Key label and entry
    ideogram_api_key_label = ctk.CTkLabel(settings_frame, text="Enter your Ideogram API key:", font=("Arial", 16))
    ideogram_api_key_label.pack(anchor='w', pady=5, padx=10)

    global ideogram_api_key_entry
    ideogram_api_key_entry = ctk.CTkEntry(settings_frame, width=500, font=("Arial", 14, "bold"))
    ideogram_api_key_entry.pack(anchor='w', pady=5, padx=10)

    # Set the entry to the current Ideogram API key
    if IDEOGRAM_API_KEY:
        ideogram_api_key_entry.insert(0, IDEOGRAM_API_KEY)

    # Stability API Key label and entry
    stability_api_key_label = ctk.CTkLabel(settings_frame, text="Enter your Stability API key:", font=("Arial", 16))
    stability_api_key_label.pack(anchor='w', pady=5, padx=10)

    global stability_api_key_entry
    stability_api_key_entry = ctk.CTkEntry(settings_frame, width=500, font=("Arial", 14, "bold"))
    stability_api_key_entry.pack(anchor='w', pady=5, padx=10)

    # Set the entry to the current Stability API key
    if STABILITY_API_KEY:
        stability_api_key_entry.insert(0, STABILITY_API_KEY)

    # Save button
    save_api_keys_button = ctk.CTkButton(settings_frame, text="Update API Keys", command=save_api_keys, width=200,
                                         font=("Arial", 14, "bold"))
    save_api_keys_button.pack(anchor='w', pady=10, padx=10)

    # Content frame for tab3 (History)
    history_frame = ctk.CTkFrame(tab3)
    history_frame.pack(pady=20, padx=20, fill='both', expand=True)

    # Create a scrollable frame
    global scrollable_frame
    scrollable_frame = ctk.CTkScrollableFrame(history_frame, width=800)
    scrollable_frame.pack(fill='both', expand=True)

    # Load history from 'images' directory
    load_history()

    # Run the GUI main loop
    app.mainloop()

    # At the end, save history metadata to file
    save_history_metadata()

# All the functions used by the GUI

def generate_images():
    prompt = prompt_entry.get()
    if not prompt:
        messagebox.showwarning("Warning", "Please enter a prompt!")
        return

    num_images = int(num_images_slider.get())
    model = model_selection.get()

    # Show loading indicator
    loading_label.configure(text="Generating images, please wait...")
    loading_label.update_idletasks()

    generated_images.clear()

    if model != "ideogram" and not model.startswith("stable"):
        # BFL API
        width = int(width_entry.get())
        height = int(height_entry.get())
        for _ in range(num_images):
            # Create request for image generation
            request_id = generate_image_request_bfl(prompt, model, width, height)
            if not request_id:
                loading_label.configure(text="")
                return

            # Poll for result
            image_url = get_image_result_bfl(request_id)
            if image_url:
                try:
                    # Fetch the image from the URL
                    image_response = requests.get(image_url)
                    image_response.raise_for_status()
                    image_data = image_response.content
                    generated_image = Image.open(io.BytesIO(image_data))
                    generated_images.append(generated_image)

                    # Save image to 'images' directory
                    timestamp = int(time.time())
                    image_filename = f"{IMAGES_DIR}/{model}_{timestamp}.png"
                    generated_image.save(image_filename)

                    # Add to history
                    history_images.append({
                        'image_path': image_filename,
                        'prompt': prompt,
                        'model': model,
                        'timestamp': timestamp
                    })

                except requests.exceptions.RequestException as e:
                    messagebox.showerror("Error", f"Failed to load image: {e}")
                    loading_label.configure(text="")
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load image: {e}")
                    loading_label.configure(text="")
                    return
    elif model == "ideogram":
        # Ideogram API
        ideogram_model = ideogram_model_selection.get()
        data = generate_image_request_ideogram(prompt, ideogram_model, num_images)
        if not data:
            loading_label.configure(text="")
            return

        for image_info in data:
            image_url = image_info.get("url")
            if image_url:
                try:
                    # Fetch the image from the URL
                    image_response = requests.get(image_url)
                    image_response.raise_for_status()
                    image_data = image_response.content
                    generated_image = Image.open(io.BytesIO(image_data))
                    generated_images.append(generated_image)

                    # Save image to 'images' directory
                    timestamp = int(time.time())
                    image_filename = f"{IMAGES_DIR}/ideogram_{timestamp}.png"
                    generated_image.save(image_filename)

                    # Add to history
                    history_images.append({
                        'image_path': image_filename,
                        'prompt': prompt,
                        'model': model,
                        'timestamp': timestamp
                    })

                except requests.exceptions.RequestException as e:
                    messagebox.showerror("Error", f"Failed to load image: {e}")
                    loading_label.configure(text="")
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load image: {e}")
                    loading_label.configure(text="")
                    return
    elif model.startswith("stable"):
        # Stability AI API
        # Get optional parameters if needed
        aspect_ratio = aspect_ratio_selection.get()
        negative_prompt = negative_prompt_entry.get()
        stability_model = model.replace("stable-", "")
        if not STABILITY_API_KEY:
            messagebox.showwarning("Warning", "Please enter your Stability API key in the Settings tab!")
            loading_label.configure(text="")
            return
        for _ in range(num_images):
            image_bytes = generate_image_request_stability(
                prompt,
                model=stability_model,
                negative_prompt=negative_prompt,
                aspect_ratio=aspect_ratio
            )
            if image_bytes:
                try:
                    generated_image = Image.open(io.BytesIO(image_bytes))
                    generated_images.append(generated_image)

                    # Save image to 'images' directory
                    timestamp = int(time.time())
                    image_filename = f"{IMAGES_DIR}/{model}_{timestamp}.png"
                    generated_image.save(image_filename)

                    # Add to history
                    history_images.append({
                        'image_path': image_filename,
                        'prompt': prompt,
                        'model': model,
                        'timestamp': timestamp
                    })

                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load image: {e}")
                    loading_label.configure(text="")
                    return
            else:
                loading_label.configure(text="")
                return

    loading_label.configure(text="")
    if generated_images:
        current_image_index.set(0)
        display_image(0)
        update_history_display()
        # Save history metadata
        save_history_metadata()

def display_image(index):
    if generated_images:
        image = generated_images[index]
        image_tk = CTkImage(image, size=(350, 350))

        # Display the image in the GUI
        image_label.configure(image=image_tk)
        image_label.image = image_tk

def next_image():
    if generated_images:
        current_index = current_image_index.get()
        # Loop to the first image if we are on the last one
        if current_index == len(generated_images) - 1:
            current_image_index.set(0)  # Set index to the first image
        else:
            current_image_index.set(current_index + 1)
        display_image(current_image_index.get())

def prev_image():
    if generated_images:
        current_index = current_image_index.get()
        # Loop to the last image if we are on the first one
        if current_index == 0:
            current_image_index.set(len(generated_images) - 1)  # Set index to the last image
        else:
            current_image_index.set(current_index - 1)
        display_image(current_image_index.get())


def save_image():
    if generated_images:
        current_index = current_image_index.get()
        file_path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=f"image_{current_index}",
                                                 filetypes=[("PNG files", "*.png")])
        if file_path:
            try:
                generated_images[current_index].save(file_path)
                messagebox.showinfo("Success", "Image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")
    else:
        messagebox.showwarning("Warning", "No image to save. Please generate an image first.")

def save_api_keys():
    new_bfl_api_key = bfl_api_key_entry.get()
    new_ideogram_api_key = ideogram_api_key_entry.get()
    new_stability_api_key = stability_api_key_entry.get()

    # Update the API keys in api_requests.py
    update_api_keys(new_bfl_api_key, new_ideogram_api_key, new_stability_api_key)
    # Save the API keys to the .env file
    save_api_keys_to_env(new_bfl_api_key, new_ideogram_api_key, new_stability_api_key)

    messagebox.showinfo("Success", "API keys updated successfully!")

from PIL import ImageTk

def update_history_display():
    # Clear existing widgets in scrollable_frame
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # Load the Save and Delete icons
    save_icon = Image.open("icons/diskette.png")
    delete_icon = Image.open("icons/bin.png")

    # Resize the icons if needed to fit the buttons
    save_icon = save_icon.resize((25, 25), Image.Resampling.LANCZOS)
    delete_icon = delete_icon.resize((25, 25), Image.Resampling.LANCZOS)

    # Convert the images to Tkinter-compatible format
    save_icon_tk = ImageTk.PhotoImage(save_icon)
    delete_icon_tk = ImageTk.PhotoImage(delete_icon)

    for idx, item in enumerate(history_images):
        image_path = item['image_path']
        try:
            # Create a frame to hold the image and buttons
            image_frame = ctk.CTkFrame(scrollable_frame, width=200, height=200)  # Adjust frame size
            image_frame.grid(row=idx // 5, column=idx % 5, padx=5, pady=5)  # Add padding for better spacing

            # Load the image thumbnail
            image = Image.open(image_path)
            img_tk = CTkImage(image, size=(100, 100))
            label = ctk.CTkLabel(image_frame, image=img_tk, text="")
            label.image = img_tk  # Keep a reference to avoid garbage collection
            label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

            # Add save button with icon
            save_button = ctk.CTkButton(image_frame, image=save_icon_tk, text="", fg_color="transparent", hover_color="gray" , width=30, height=20,
                                        command=lambda idx=idx: save_history_image(idx))
            save_button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")  # Use sticky to make button fill the cell

            # Add delete button with icon
            delete_button = ctk.CTkButton(image_frame, image=delete_icon_tk, text="", fg_color="transparent",  hover_color="gray", width=30, height=20,
                                          command=lambda idx=idx: delete_history_image(idx))
            delete_button.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")  # Use sticky to make button fill the cell

            # Bind left click to open image view
            label.bind("<Button-1>", lambda e, idx=idx: view_history_image(idx))

        except Exception as e:
            print(f"Failed to load image {image_path}: {e}")



def view_history_image(index):
    selected_item = history_images[index]
    image_path = selected_item['image_path']
    try:
        image = Image.open(image_path)
        image_tk = CTkImage(image, size=(400, 400))

        # Display the image in the GUI
        image_label.configure(image=image_tk)
        image_label.image = image_tk

        # Optionally, update generated_images to include this image
        generated_images.clear()
        generated_images.append(image)
        current_image_index.set(0)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load image: {e}")

def show_context_menu(event, idx):
    context_menu = tk.Menu(app, tearoff=0)
    context_menu.add_command(label="Save Image", command=lambda: save_history_image(idx))
    context_menu.add_command(label="Delete Image", command=lambda: delete_history_image(idx))
    context_menu.post(event.x_root, event.y_root)

def save_history_image(index):
    item = history_images[index]
    image_path = item['image_path']
    image = Image.open(image_path)
    file_path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=f"history_image_{index}",
                                             filetypes=[("PNG files", "*.png")])
    if file_path:
        try:
            image.save(file_path)
            messagebox.showinfo("Success", "Image saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")

def delete_history_image(index):
    confirm = messagebox.askyesno("Delete Image", "Are you sure you want to delete this image from history?")
    if confirm:
        item = history_images[index]
        image_path = item['image_path']
        if os.path.exists(image_path):
            os.remove(image_path)
        del history_images[index]
        update_history_display()
        save_history_metadata()

def save_history_metadata():
    # Save history metadata to a JSON file
    metadata = history_images
    with open(f"{IMAGES_DIR}/history.json", "w") as f:
        json.dump(metadata, f)

def load_history():
    global history_images
    # Load history metadata from JSON file
    history_file = f"{IMAGES_DIR}/history.json"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history_images = json.load(f)
        update_history_display()
    else:
        history_images = []

# Call the create_gui function when this module is run directly
if __name__ == "__main__":
    create_gui()
