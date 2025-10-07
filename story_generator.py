import json, requests

def generate_story_from_llama3(name, age, moral, scenes, length):
    """Generate story JSON using local Llama3 API."""
    system_prompt = (
        f"Create a {length} children's story for a {age}-year-old child named {name}. "
        f"The story should teach about {moral or 'kindness'} and have {scenes} clear scenes. "
        f"Output JSON with keys: 'scenes': [{{'title':..., 'text':..., 'background':...}}]."
    )
    print("Llama3 prompt:", system_prompt)

    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": system_prompt, "stream": False},
            timeout=300
        )
        text = resp.json().get("response", "")
    except requests.exceptions.RequestException as e:
        print("Llama3 API request failed:", e)
        text = ""

    # Parse story structure
    try:
        story_json = json.loads(text[text.find("{"):text.rfind("}") + 1])
        return story_json.get("scenes", [])
    except Exception:
        # fallback simple split
        scenes_list = []
        scenes_split = text.split("Scene")
        for i, chunk in enumerate(scenes_split[1:], start=1):
            scenes_list.append({
                "title": f"Scene {i}",
                "text": chunk.strip(),
                "background": f"Scene {i} illustration"
            })
        return scenes_list
