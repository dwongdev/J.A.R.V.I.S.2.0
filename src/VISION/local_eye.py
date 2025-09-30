import base64
import io
import os
import json
import cv2
import requests
import numpy as np
from PIL import Image, ImageDraw
from src.FUNCTION.Tools.get_env import EnvManager
import re

# The ollama library is required for this local processor.
# You can install it with: pip install ollama
try:
    import ollama
except ImportError:
    raise ImportError("The 'ollama' library is required for LocalImageProcessor. Please install it using 'pip install ollama'.")

class LocalImageProcessor:
    """
    A class to process images using a local multimodal model via Ollama.
    Mirrors the functionality of ImageProcessor for a local environment.
    """
    def __init__(self, image_path="captured_image.png", model_name="llava:7b"):
        """
        Initializes the processor.

        Args:
            image_path (str): The default path to save/read images.
            model_name (str): The name of the local model to use with Ollama (e.g., 'llava').
        """
        
        self.image_path = image_path
        self.require_width = 336
        self.require_height = 336
        if model_name:
            self.model = model_name
        else:
            self.model = EnvManager.load_variable("Image_to_text")
        
        # Check if the Ollama server is running and the model is available
        try:
            ollama.show(model_name)
        except Exception as e:
            print(f"Error connecting to Ollama or finding model '{model_name}'.")
            print("Please ensure the Ollama server is running and you have pulled the model (e.g., 'ollama run llava').")
            raise e

    # ---------- Image capture and resizing (No changes) ----------
    def resize_image(self, require_width=None, require_height=None) -> bool:
        """Resizes the image to the specified dimensions."""
        require_width = require_width or self.require_width
        require_height = require_height or self.require_height

        try:
            with Image.open(self.image_path) as img:
                # The ANTIALIAS attribute is deprecated and will be removed in Pillow 10 (2023-07-01). 
                # Use Resampling.LANCZOS instead.
                resample_filter = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
                img = img.resize((require_width, require_height), resample_filter)
                img.save(self.image_path)
                print(f"Image saved to {self.image_path}, size: {require_width}x{require_height}")
        except Exception as e:
            print(f"Error during resize: {e}")
            return False
        return True

    def capture_image_and_save(self) -> str | None:
        """Captures an image from the webcam and saves it."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return None
        try:
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(self.image_path, frame)
                print(f"Image captured and saved as {self.image_path}")
                return self.image_path
            else:
                print("Error: Could not capture image.")
                return None
        finally:
            cap.release()
            cv2.destroyAllWindows()

    # ---------- Basic detection ----------
    def detect_image(self, query: str) -> str | None:
        """Detect content using the set local model."""
        if not query:
            query = "What is this image?"
        try:
            with open(self.image_path, 'rb') as f:
                image_bytes = f.read()
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': query,
                        'images': [image_bytes]
                    }
                ]
            )
            return response['message']['content']
        except Exception as e:
            print(f"Error during local detection: {e}")
            return None

    # ---------- Object detection ----------
    def detect_objects(self, prompt="Detect all prominent items in the image.") -> list | None:
        """Detects objects using a text prompt to force JSON output."""
        # Strong prompt to guide the local model to produce structured JSON
        json_prompt = f"""{prompt}. 
        Analyze the provided image and identify the prominent objects.
        Your output must be ONLY a valid JSON list of objects. Do not include any text, explanation, or markdown.
        Each object in the list should be a dictionary with one key: "box_2d".
        The "box_2d" value must be a list of four integers: [y1, x1, y2, x2].
        These coordinates should be normalized to a 1000x1000 grid, where y1 < y2 and x1 < x2.
        Example format: [{{"box_2d": [250, 150, 750, 850]}}, {{"box_2d": [100, 300, 400, 700]}}]
        """
        try:
            image = Image.open(self.image_path)
            width, height = image.size

            with open(self.image_path, 'rb') as f:
                image_bytes = f.read()

            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': json_prompt,
                        'images': [image_bytes]
                    }
                ]
            )
            
            # Use the helper to parse the model's text response
            boxes_data = self._parse_json(response['message']['content'])
            
            if not boxes_data:
                print("Could not parse JSON from model response.")
                return None
            
            converted_boxes = []
            for box in boxes_data:
                if "box_2d" in box and len(box["box_2d"]) == 4:
                    y1, x1, y2, x2 = box["box_2d"]
                    # Convert from 1000x1000 grid to actual image dimensions
                    converted_boxes.append([
                        int(x1 / 1000 * width), int(y1 / 1000 * height),
                        int(x2 / 1000 * width), int(y2 / 1000 * height)
                    ])
            return converted_boxes
        except Exception as e:
            print(f"Error during local object detection: {e}")
            return None

    def extract_segmentation_masks(self, prompt=None, output_dir="segmentation_results"):
        """This functionality is not supported by standard local VLMs like LLaVA."""
        print("Warning: Segmentation mask generation is not supported by this local processor.")
        raise NotImplementedError("Standard local VLMs do not generate pixel-level segmentation masks.")

    # ---------- Helper (No changes) ----------
    def _parse_json(self, text_output: str) -> list:
        """
        Extracts the first JSON list from a model output string,
        even if there is extra text or markdown fences around it.
        """
        text_output = re.sub(r"```(json)?", "", text_output, flags=re.IGNORECASE).strip()

        start = text_output.find("[")
        end = text_output.rfind("]") + 1
        
        if start != -1 and end != -1:
            json_str = text_output[start:end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed on extracted text: {e}")
                return []
        return []

    # ---------- File API (Not applicable to local models) ----------
    def upload_image_file(self):
        """This functionality is not applicable for local, stateless model servers like Ollama."""
        print("Warning: The concept of a File API does not apply to this local processor.")
        raise NotImplementedError("Local models process images directly per request; there is no file upload API.")

    # ---------- Multi-image prompt ----------
    def multi_image_prompt(self, images: list[str], prompt: str) -> str | None:
        """Sends a prompt with multiple images to the local model."""
        try:
            image_bytes_list = []
            for img_path in images:
                if not os.path.exists(img_path):
                    print(f"Image path does not exist: {img_path}")
                    continue
                with open(img_path, 'rb') as f:
                    image_bytes_list.append(f.read())
            
            if not image_bytes_list:
                print("No valid images to process.")
                return None

            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': image_bytes_list
                    }
                ]
            )
            return response['message']['content']
        except Exception as e:
            print(f"Error during multi-image prompt: {e}")
            return None

    # ---------- Inline image from URL (No changes) ----------
    def get_image_from_url(self, url: str) -> Image.Image | None:
        """Downloads an image from a URL and returns a PIL Image object."""
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            img_bytes = response.content
            return Image.open(io.BytesIO(img_bytes))
        except requests.RequestException as e:
            print(f"Error fetching image from URL {url}: {e}")
            return None


def main_local():
    """Main function to demonstrate the LocalImageProcessor."""
    # Ensure a test image exists. Let's create a placeholder if not.
    test_image_path = "test_image_local.png"
    if not os.path.exists(test_image_path):
        try:
            img = Image.new('RGB', (640, 480), color = 'red')
            d = ImageDraw.Draw(img)
            d.rectangle([100, 100, 300, 300], fill='blue')
            d.text((50,50), "Test Image", fill=(255,255,0))
            img.save(test_image_path)
            print(f"Created a dummy test image: {test_image_path}")
        except Exception as e:
            print(f"Could not create a test image: {e}")
            return

    # Initialize processor with a local model name
    # Ensure you have run 'ollama pull llava' first
    try:
        processor = LocalImageProcessor(image_path=test_image_path, model_name="llava")
    except Exception:
        return # Stop if initialization fails

    # ---------- 1. Basic detection ----------
    print("\n--- 1. Basic Detection ---")
    detection = processor.detect_image("Describe this image in detail.")
    if detection:
        print("Basic detection output:")
        print(detection)

    # ---------- 2. Object detection ----------
    print("\n--- 2. Object Detection ---")
    boxes = processor.detect_objects(prompt="Detect the blue square.")
    if boxes:
        print("Detected bounding boxes:")
        for b in boxes:
            print(b)

    # ---------- 3. Multi-image prompt ----------
    print("\n--- 3. Multi-image Prompt ---")
    # For demonstration, creating a second test image
    test_image_2_path = "test_image_local_2.png"
    img2 = Image.new('RGB', (640, 480), color = 'green')
    img2.save(test_image_2_path)
    
    multi_response = processor.multi_image_prompt(
        images=[processor.image_path, test_image_2_path],
        prompt="Describe the primary color of each image. First image, then second image."
    )
    if multi_response:
        print("Multi-image prompt response:")
        print(multi_response)
        
    # ---------- 4. Fetch image from URL ----------
    print("\n--- 4. Fetch image from URL ---")
    url = "[https://via.placeholder.com/150/0000FF/FFFFFF?Text=URL+Image](https://via.placeholder.com/150/0000FF/FFFFFF?Text=URL+Image)"
    image_from_url = processor.get_image_from_url(url)
    if image_from_url:
        image_from_url.save("url_image.png")
        print("Fetched image from URL and saved as url_image.png")
    
    # ---------- 5. Unsupported features ----------
    print("\n--- 5. Testing Unsupported Features ---")
    try:
        processor.extract_segmentation_masks()
    except NotImplementedError as e:
        print(f"Correctly caught expected error: {e}")
        
    try:
        processor.upload_image_file()
    except NotImplementedError as e:
        print(f"Correctly caught expected error: {e}")


if __name__ == "__main__":
    # You can run the original main() or the new main_local()
    # main() # For the Google GenAI Processor
    main_local() # For the Local Ollama Processor