import os
import openai
import requests
import time

# --- Configuration ---
OPENAI_API_KEY = ""  # Replace with your OpenAI key

# --- Helper Functions ---
def sanitize_filename(text):
    """Convert prompt text to a safe filename."""
    return "".join(c if c.isalnum() else "_" for c in text)[:50]

def download_and_save(url, save_path):
    """Download image from URL and save to disk."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"✓ Saved: {save_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to save {url}: {str(e)}")
        return False

# --- DALL-E Generation Function ---
def generate_with_dalle(prompt, save_dir, num_images=1):
    """
    Generate images using DALL-E API with batch handling.
    
    Parameters:
      prompt (str): The prompt for the image generation.
      save_dir (str): The directory where the images will be saved.
      num_images (int): Total images to generate.
      
    Returns:
      list: File paths to the saved images.
    """
    openai.api_key = OPENAI_API_KEY
    saved_paths = []
    batches = (num_images + 3) // 4  # DALL-E allows 4 images per batch
    
    try:
        for batch in range(batches):
            n_images = min(4, num_images - batch * 4)
            print(f"Calling DALL-E API for batch {batch + 1} (n={n_images})")
            response = openai.Image.create(
                prompt=prompt,
                n=n_images,
                size="512x512",
                response_format="url"
            )
            
            for i, img in enumerate(response["data"]):
                # Debug print to check the extracted URL.
                print("Extracted URL from DALL-E:", img["url"])
                filename = f"dalle_{sanitize_filename(prompt)}_{batch*4+i}.png"
                save_path = os.path.join(save_dir, filename)
                if download_and_save(img["url"], save_path):
                    saved_paths.append(save_path)
            
            if batch < batches - 1:
                print("Waiting 20 seconds for DALL-E rate limit...")
                time.sleep(20)
                
    except Exception as e:
        print(f"DALL-E Error: {e}")
    
    return saved_paths

# --- Testing the DALL-E Function ---
if __name__ == "__main__":
    test_prompt = "a picture of an avergae family"  # Change the prompt as needed
    test_save_dir = "test_dalle_images"
    os.makedirs(test_save_dir, exist_ok=True)
    
    print("Testing DALL-E image generation:")
    generated_paths = generate_with_dalle(test_prompt, test_save_dir, num_images=1)
    print("Generated file paths:", generated_paths)
