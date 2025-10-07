import os
from diffusers import StableDiffusionImg2ImgPipeline, StableDiffusionPipeline
from PIL import Image
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

# Load text-to-image model
sd_model = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
).to(device)

# Load image-to-image model for character reference
img2img_model = StableDiffusionImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
).to(device)

from PIL import Image
import os

def generate_scene_with_character(scene_desc, age, gender, character_image, output_folder="outputs"):
    """
    Generate a cartoon story scene using the uploaded character image as reference.
    Saves the final image as scene_<index>.png and returns the path.
    """
    # Create prompt emphasizing cartoon background
    base_prompt = (
        f"A magical {scene_desc}, featuring a {age}-year-old {gender} child, "
        "storybook cartoon illustration, light pastel colors, soft lines, "
        "whimsical, hand-drawn style, cheerful, background in subtle light watercolor comic style"
    )

    print(f"🎨 Generating character scene using uploaded photo as reference...")
    init_image = character_image.convert("RGB").resize((512, 512))
    ref_prompt = (
        base_prompt + ", character face should resemble the uploaded photo, "
        "in storybook cartoon form"
    )

    result = img2img_model(
        prompt=ref_prompt,
        image=init_image,
        strength=0.6,          # keeps resemblance but stylizes cartoon
        guidance_scale=8.0,
    )
    final_image = result.images[0]

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    img_path = os.path.join(output_folder, f"character_scene.png")
    final_image.save(img_path)
    print(f"✅ Character Scene saved: {img_path}")
    return img_path


def generate_scene(scene_desc, age, gender, scene_index=1, output_folder="outputs"):
    """
    Generate a cartoon story scene without any uploaded character.
    Saves the final image as scene_<index>.png and returns the path.
    """
    base_prompt = (
        f"A magical {scene_desc}, featuring a {age}-year-old {gender} child, "
        "storybook cartoon illustration, light pastel colors, soft lines, "
        "whimsical, hand-drawn style, cheerful, background in subtle watercolor comic style"
    )

    print(f"🌀 Generating scene {scene_index} without character photo...")
    result = sd_model(prompt=base_prompt, guidance_scale=7.5)
    final_image = result.images[0]

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    img_path = os.path.join(output_folder, f"scene_{scene_index}.png")
    final_image.save(img_path)
    print(f"✅ Scene {scene_index} saved: {img_path}")
    return img_path
