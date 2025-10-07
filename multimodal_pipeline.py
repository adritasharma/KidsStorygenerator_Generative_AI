from story_generator import generate_story_from_llama3
from image_generator import generate_scene_image
from utils import display_image
from PIL import Image
import io, base64

def create_story_and_images(name, age, gender, moral, scenes_count, length, photo_contents=None):
    story_scenes = generate_story_from_llama3(name, age, moral, scenes_count, length)
    story_text = ""
    image_divs = []

    # Prepare character image
    if photo_contents:
        header, encoded = photo_contents.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        character_image = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        character_image = character_image.resize((256, 256))
    else:
        character_image = None

    for i, sc in enumerate(story_scenes):
        title = sc.get("title", f"Scene {i+1}")
        text = sc.get("text", "")
        scene_desc = sc.get("background", "cartoon storybook scene, light pastel colors, soft, calm")

        story_text += f"\n🧩 {title}\n{text}\n"
        img_path = generate_scene_image(scene_desc, age, gender, character_image, i+1)
        img_src = display_image(img_path)
        image_divs.append({"src": img_src, "title": title})

    return story_text, image_divs
