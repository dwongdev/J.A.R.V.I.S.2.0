
import base64
import cv2
from PIL import Image
from testing.src.FUNCTION.Tools.get_env import load_variable
from google import genai

class ImageProcessor:
    def __init__(self, image_path="captured_image.png"):
        self.image_path = image_path
        self.require_width = 336
        self.require_height = 336

    def resize_image(self, require_width=None, require_height=None) -> bool:
        """Resize image to specified dimensions."""
        require_width = require_width or self.require_width
        require_height = require_height or self.require_height
        
        try:
            with Image.open(self.image_path) as img:
                width, height = img.size
                if height <= require_height and width <= require_width:
                    return True
                
                img = img.resize((require_width, require_height), Image.ANTIALIAS)
                img.save(self.image_path)
                print(f"Image saved to {self.image_path}, size: {require_width}x{require_height}")
        except Exception as e:
            print(e)
            return False
        return True 

    def capture_image_and_save(self) -> str | None:
        """Capture an image from the camera and save it."""
        # Initialize the camera
        cap = cv2.VideoCapture(0)  # 0 is the default camera

        if not cap.isOpened():
            print("Error: Could not open camera.")
            return None

        try:
            # Capture a single frame
            ret, frame = cap.read()

            if ret:
                # Save the image in PNG format
                cv2.imwrite(self.image_path, frame)
                print(f"Image captured and saved as {self.image_path}")
                return self.image_path
            else:
                print("Error: Could not capture image.")
                return None
        finally:
            # Release the camera
            cap.release()
            cv2.destroyAllWindows()

    def detect_image(self) -> str | None:
        """Detect content in the image using Google GenAI."""
        try:
            image = Image.open(self.image_path)
            genai_key = load_variable("genai-key")
            client = genai.Client(api_key=genai_key)

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=["What is this image?", image]
            )
            return response.text
        except Exception as e:
            print(f"Error: {e}")
            return None 


# Usage example:
# image_processor = ImageProcessor()
# image_processor.capture_image_and_save()
# image_processor.resize_image()
# result = image_processor.detect_image()
# print(result)
