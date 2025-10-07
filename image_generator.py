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
    Recreates your old working logic — cartoon style, photo resemblance, no img2img pipeline.
    """
    print(f"\n🎨 Starting generation for Scene {scene_index}...")

    os.makedirs("outputs", exist_ok=True)
    img_path = f"outputs/scene_{scene_index}.png"

    # 🔹 Prompt setup
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

    # 🔹 Generate image (simulate “init_image” effect by blending manually if character_image exists)
    print("🌀 Generating image...")
    result = sd_model(prompt=prompt, guidance_scale=7.5)

    final_image = result.images[0].convert("RGBA")

    # 🔹 If uploaded photo exists — blend it subtly into the result
    if character_image:
        character_image = character_image.resize(final_image.size).convert("RGBA")
        final_image = Image.blend(final_image, character_image, alpha=0.25)

    final_image = final_image.convert("RGB")
    final_image.save(img_path)

    print(f"🎉 Scene {scene_index} generated successfully! Saved at {img_path}\n")
    return img_path
