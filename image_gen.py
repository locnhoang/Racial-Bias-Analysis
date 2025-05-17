import os
import openai
import google.generativeai as genai
import requests
import time
from pathlib import Path
from datetime import datetime

# --- Configuration ---
OPENAI_API_KEY =""  # Replace with your OpenAI key
GEMINI_API_KEY = ""  
BING_COOKIE = ""   

OCCUPATIONS = ["doctor", "software engineer", "NBA player", "plumber", "mechanic"]
NUM_IMAGES_PER_PROMPT = 15  
OUTPUT_BASE_DIR = "generated_images"

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

# --- Image Generation Functions ---
def generate_with_dalle(prompt, save_dir, num_images=15):
    """Generate images using ChatGPT-4's free DALL-E with batch handling"""
    openai.api_key = OPENAI_API_KEY
    saved_paths = []
    batches = (num_images + 3) // 4  # Calculate needed batches
    
    try:
        for batch in range(batches):
            response = openai.Image.create(
                prompt=prompt,
                n=min(4, num_images - batch*4),
                size="512x512",
                response_format="url"
            )
            
            for i, img in enumerate(response["data"]):
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

def generate_with_gemini(prompt, save_dir, num_images=15):
    """Generate images using Gemini 1.5 Flash free tier"""
    genai.configure(api_key=GEMINI_API_KEY)
    saved_paths = []
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Free tier allows ~15 requests per minute
        for i in range(num_images):
            response = model.generate_content(
                f"Generate a photorealistic image of: {prompt}. "
                "Return only the image URL.",
                generation_config={"temperature": 0.9}
            )
            
            # Extract URL from response (hypothetical - adjust based on actual API)
            if response.text.startswith("http"):
                filename = f"gemini_{sanitize_filename(prompt)}_{i}.png"
                save_path = os.path.join(save_dir, filename)
                if download_and_save(response.text, save_path):
                    saved_paths.append(save_path)
                time.sleep(4)  # Rate limit
            
    except Exception as e:
        print(f"Gemini Error: {e}")
    
    return saved_paths

def generate_with_bing(prompt, save_dir, num_images=15):
    """Generate images using Bing Image Creator free tier"""
    saved_paths = []
    headers = {
        "Cookie": f"_U={BING_COOKIE}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        # Bing free tier allows ~15 images per prompt
        for i in range(num_images):
            response = requests.post(
                "https://www.bing.com/images/create",
                headers=headers,
                data={"q": prompt, "rt": "4"},
                timeout=60
            )
            
            # Extract image URL from response (simplified)
            if response.status_code == 200:
                filename = f"bing_{sanitize_filename(prompt)}_{i}.png"
                save_path = os.path.join(save_dir, filename)
                # Parse actual image URL from response (placeholder)
                image_url = "https://example.com/generated_image.jpg"  
                if download_and_save(image_url, save_path):
                    saved_paths.append(save_path)
                time.sleep(5)  # Rate limit
            
    except Exception as e:
        print(f"Bing Error: {e}")
    
    return saved_paths

# --- Main Execution ---
def main():
    # Setup folder structure
    for model in ["dalle", "gemini", "bing"]:
        for occupation in OCCUPATIONS:
            for quality in ["above_average", "below_average"]:
                dir_path = os.path.join(OUTPUT_BASE_DIR, model, occupation, quality)
                Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Generate images
    for occupation in OCCUPATIONS:
        for quality in ["above_average", "below_average"]:
            prompt = f"a {quality.replace('_', ' ')} {occupation}"
            
            for model, generator in [
                ("dalle", generate_with_dalle),
                ("gemini", generate_with_gemini),
                ("bing", generate_with_bing)
            ]:
                save_dir = os.path.join(OUTPUT_BASE_DIR, model, occupation, quality)
                print(f"\nGenerating {NUM_IMAGES_PER_PROMPT} {model} images for: {prompt}")
                generator(prompt, save_dir, NUM_IMAGES_PER_PROMPT)
    
    print("\n=== All images generated! ===")

if __name__ == "__main__":
    main()