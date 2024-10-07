# api_requests.py

import os
import requests
import time
import io
from tkinter import messagebox
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set your API keys from environment variables or .env file
BFL_API_KEY = os.getenv("BFL_API_KEY")
IDEOGRAM_API_KEY = os.getenv("IDEOGRAM_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# Function to send a prompt request to the BFL API
def generate_image_request_bfl(prompt, model, width=1024, height=768):
    try:
        response = requests.post(
            f'https://api.bfl.ml/v1/{model}',
            headers={
                'accept': 'application/json',
                'x-key': BFL_API_KEY,
                'Content-Type': 'application/json',
            },
            json={
                'prompt': prompt,
                'width': width,
                'height': height,
            },
        )
        response.raise_for_status()
        response_json = response.json()
        return response_json.get("id")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to create generation request: {e}")
        return None

# Function to poll the result of a BFL request
def get_image_result_bfl(request_id):
    try:
        while True:
            time.sleep(0.5)
            result = requests.get(
                'https://api.bfl.ml/v1/get_result',
                headers={
                    'accept': 'application/json',
                    'x-key': BFL_API_KEY,
                },
                params={
                    'id': request_id,
                },
            )
            result.raise_for_status()
            result_json = result.json()
            if result_json["status"] == "Ready":
                return result_json['result']['sample']
            elif result_json["status"] == "Failed":
                messagebox.showerror("Error", "Image generation failed")
                return None
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to retrieve image result: {e}")
        return None

# Function to send a prompt request to the Ideogram API
def generate_image_request_ideogram(prompt, model, num_images):
    try:
        url = "https://api.ideogram.ai/generate"
        payload = {
            "image_request": {
                "prompt": prompt,
                "model": model,
                "num_images": num_images,
                "magic_prompt_option": "AUTO"
            }
        }
        headers = {
            "Api-Key": IDEOGRAM_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        return response_json.get("data", [])
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to create generation request: {e}")
        return None

# Function to send a prompt request to the Stability AI API
def generate_image_request_stability(prompt, model='ultra', negative_prompt=None, aspect_ratio='1:1', output_format='png'):
    try:
        # Check if the API key is set
        if not STABILITY_API_KEY:
            messagebox.showerror("Error", "Stability API key is not set. Please enter it in the Settings tab.")
            return None

        # Set the endpoint URL based on the model
        if model == 'ultra':
            url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
        elif model == 'core':
            url = "https://api.stability.ai/v2beta/stable-image/generate/core"
        elif model == 'sd3':
            url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        else:
            messagebox.showerror("Error", f"Invalid Stability model selected: {model}")
            return None

        # Prepare headers
        headers = {
            "authorization": f"Bearer {STABILITY_API_KEY}",
            "accept": "image/*",
            # Content-Type is automatically set when using 'files' and 'data' in requests
        }

        # Prepare data
        data = {
            "prompt": prompt,
            "output_format": output_format,
            "aspect_ratio": aspect_ratio,
        }
        if negative_prompt:
            data['negative_prompt'] = negative_prompt

        # For multipart/form-data, we need to include a dummy file field
        response = requests.post(url, headers=headers, files={"none": ''}, data=data)

        if response.status_code == 200:
            return response.content  # Return the image bytes
        else:
            error_message = f"Error: {response.status_code}, {response.text}"
            messagebox.showerror("Error", error_message)
            return None

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to send request: {e}")
        return None

# Function to update API keys
def update_api_keys(bfl_key, ideogram_key, stability_key):
    global BFL_API_KEY, IDEOGRAM_API_KEY, STABILITY_API_KEY
    BFL_API_KEY = bfl_key
    IDEOGRAM_API_KEY = ideogram_key
    STABILITY_API_KEY = stability_key
