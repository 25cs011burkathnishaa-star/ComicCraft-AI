import os
import re
from PIL import Image, ImageDraw
import torch
from diffusers import StableDiffusionPipeline

MODEL_ID = "runwayml/stable-diffusion-v1-5"
_pipe = None

def get_image_pipe():
    global _pipe
    if _pipe is None:
        try:
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            _pipe = StableDiffusionPipeline.from_pretrained(
                MODEL_ID, 
                torch_dtype=dtype,
                low_cpu_mem_usage=True
            )
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _pipe = _pipe.to(device)
        except Exception as e:
            print(f"Warning: Could not load Stable Diffusion model ({e}). Fallback dummy image generator active.")
            _pipe = "fallback"
    return _pipe

def sanitize_filename(text: str) -> str:
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '_', text)[:50] + ".png"

def generate_image(prompt: str, filename: str = None) -> str:
    if not filename:
        filename = sanitize_filename(prompt)
    
    path = os.path.join("static", "panels", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    pipe = get_image_pipe()
    
    if pipe == "fallback" or pipe is None:
        img = Image.new('RGB', (512, 512), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((20, 250), "Comic Panel Illustration\n(AI Model Placeholder)", fill=(255, 255, 255))
        img.save(path)
        return path

    try:
        image = pipe(prompt, num_inference_steps=25).images[0]
        image.save(path)
        return path
    except Exception as e:
        print(f"Image generation error: {e}. Using fallback image.")
        img = Image.new('RGB', (512, 512), color=(100, 50, 50))
        d = ImageDraw.Draw(img)
        d.text((20, 250), f"Error generating image:\n{str(e)[:30]}", fill=(255, 255, 255))
        img.save(path)
        return path