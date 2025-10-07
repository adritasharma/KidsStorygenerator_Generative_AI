from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import os

device = "cuda" if torch.cuda.is_available() else "cpu"

print("🚀 Loading Stable Diffusion model...")
sd_model = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
).to(device)
print("✅ Model loaded successfully.\n")

def generate_scene_image(scene_desc, age, gender, character_image=None, scene_index=1):
    """
    Generates one cartoon-style story scene image.
    Returns the saved image path.
    """
    print(f"\n🎨 Starting generation for Scene {scene_index}...")

    os.makedirs("outputs", exist_ok=True)
    img_path = f"outputs/scene_{scene_index}.png"

    if character_image:
        prompt = (
            f"{scene_desc}, include a {age}-year-old {gender} child resembling uploaded photo, "
            "cartoon style, storybook illustration, light pastel colors, "
            "character interacting naturally with scene, full body, natural pose"
        )
    else:
        prompt = (
            f"{scene_desc}, {age}-year-old {gender} child, cartoon style, storybook illustration, light pastel colors"
        )
    print("✅ Prompt ready.")

    print("🌀 Starting Stable Diffusion generation...")
    final_image = sd_model(
        prompt=prompt,
        guidance_scale=7.5
    ).images[0]
    print("✅ Image generation complete.")

    print("🖼️ Converting and saving image...")
    final_image = final_image.convert("RGB")
    final_image.save(img_path)
    print(f"✅ Image saved at: {img_path}")

    print(f"🎉 Scene {scene_index} generation completed successfully!\n")

    return img_path
