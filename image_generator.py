from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import os

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading Stable Diffusion model...")
sd_model = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if device=="cuda" else torch.float32
).to(device)

def generate_scene_image(scene_desc, age, gender, character_image=None, scene_index=1):
    """Generate a story scene image."""
    img_path = f"outputs/scene_{scene_index}.png"
    if os.path.exists(img_path):
        return img_path

    if character_image:
        prompt = (
            f"{scene_desc}, include a {age}-year-old {gender} child resembling uploaded photo, "
            "cartoon style, storybook illustration, light pastel colors, "
            "character interacting naturally with scene, full body, natural pose"
        )
        final_image = sd_model(
            prompt=prompt,
            init_image=character_image,
            strength=0.6,
            guidance_scale=7.5
        ).images[0]
    else:
        prompt = (
            f"{scene_desc}, {age}-year-old {gender} child, cartoon style, "
            "storybook illustration, light pastel colors"
        )
        final_image = sd_model(
            prompt=prompt,
            guidance_scale=7.5
        ).images[0]

    final_image.save(img_path)
    return img_path
