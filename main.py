import os, io, base64, json, requests
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from diffusers import StableDiffusionPipeline
import torch
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

from transformers import CLIPTextModel

# --------------------- Config ---------------------
os.makedirs("outputs", exist_ok=True)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load Stable Diffusion (small checkpoint)
print("Loading Stable Diffusion model...")
sd_model = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    dtype=torch.float16 if device == "cuda" else torch.float32
).to(device)

# --------------------- Dash Setup ---------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.MINTY],
    suppress_callback_exceptions=True
)
app.title = "Kids Story Creator"

def display_image(path):
    """Helper to display generated image"""
    if not os.path.exists(path):
        return ""
    encoded = base64.b64encode(open(path, "rb").read()).decode()
    return f"data:image/png;base64,{encoded}"

# --------------------- Layout ---------------------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("🧒 Kids Story Creator", 
                        style={'textAlign': 'center', 'color': '#FF6F61', 'fontFamily': 'Comic Sans MS'}),
                width=12)
    ], className="mb-4"),

    dbc.Row([
        # ---------- Input Panel ----------
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Story Inputs", className="bg-warning text-dark fw-bold"),
                dbc.CardBody([
                    dbc.Input(id="kid_name", placeholder="Enter child's name", type="text", className="mb-2"),
                    dbc.Label("Select Age:", className="fw-bold"),
                    dcc.Slider(3, 12, 1, value=6, marks={i: str(i) for i in range(3, 13)}, id="age_slider", className="mb-3"),

                    dbc.Label("Story Moral or Theme:", className="fw-bold"),
                    dbc.Textarea(id="story_moral", placeholder="e.g. Honesty, Friendship, Courage", className="mb-3"),

                    dbc.Label("Upload Child's Photo:", className="fw-bold"),
                    dcc.Upload(
                        id="upload_photo",
                        children=html.Div(["📸 Drag and Drop or Click to Upload"]),
                        multiple=False,
                        style={
                            'width': '100%', 'height': '60px', 'lineHeight': '60px',
                            'borderWidth': '2px', 'borderStyle': 'dashed', 'borderRadius': '10px',
                            'textAlign': 'center', 'backgroundColor': '#FFF8DC', 'color': '#555'
                        }
                    ),
                    html.Br(),

                    dbc.Label("Number of Scenes:", className="fw-bold"),
                    dcc.Slider(1, 5, 1, value=1, marks={i: str(i) for i in range(1, 6)}, id="scene_slider", className="mb-4"),

                    dbc.Label("Story Length:", className="fw-bold"),
                    dbc.RadioItems(
                        options=[
                            {"label": "Short", "value": "short"},
                            {"label": "Medium", "value": "medium"},
                            {"label": "Long", "value": "long"}
                        ],
                        value="medium",
                        id="story_length",
                        inline=True,
                        className="mb-3"
                    ),

                    dbc.Button("✨ Generate Story", id="generate_btn", color="primary", className="w-100 mb-2 fw-bold"),
                    dbc.Button("📕 Export as PDF", id="pdf_btn", color="success", className="w-100 fw-bold")
                ])
            ])
        ], width=4),

        # ---------- Output Panel ----------
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Generated Storybook", className="bg-info text-white fw-bold"),
                dbc.CardBody([
                    html.Div(id="story_output", 
                             style={'whiteSpace': 'pre-wrap', 'fontFamily': 'Comic Sans MS', 'fontSize': '16px'}),
                    html.Hr(),
                    html.Div(id="images_output"),
                    html.Div(id="pdf_status", style={'color': 'green', 'marginTop': '10px'})
                ])
            ])
        ], width=8)
    ])
], fluid=True, style={'backgroundColor': '#FFFAE5', 'paddingBottom': '30px'})


# --------------------- Story Generation ---------------------
def generate_story_from_llama3(name, age, moral, scenes, length):
    """Use local Ollama Llama3 model to generate story"""
    system_prompt = (
        f"Create a {length} children's story for a {age}-year-old child named {name}. "
        f"The story should teach about {moral or 'kindness'} and have {scenes} clear scenes. "
        f"Output JSON with keys: 'scenes': [{{'title':..., 'text':..., 'background':...}}]."
    )

    print(f"Generating story... prompt: {system_prompt}")
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": system_prompt, "stream": False},
            timeout=300
        )
        text = resp.json().get("response", "")
    except requests.exceptions.RequestException as e:
        print("Ollama Llama3 API request failed", e)
    
    # try parsing story structure
    try:
        story_json = json.loads(text[text.find("{"):text.rfind("}")+1])
        return story_json.get("scenes", [])
    except Exception:
        print(f"parsing story structure failed: {text}")
        # fallback: naive split if LLM returned plain text
        scenes_split = text.split("Scene")
        scenes_list = []
        for i, chunk in enumerate(scenes_split[1:], start=1):
            scenes_list.append({"title": f"Scene {i}", "text": chunk.strip(), "background": f"Scene {i} illustration"})
        return scenes_list


# --------------------- Callbacks ---------------------
@app.callback(
    [Output("story_output", "children"),
     Output("images_output", "children")],
    Input("generate_btn", "n_clicks"),
    [State("kid_name", "value"),
     State("age_slider", "value"),
     State("story_moral", "value"),
     State("scene_slider", "value"),
     State("story_length", "value"),
     State("upload_photo", "contents")]
)
def generate_story(n_clicks, name, age, moral, scenes, length, photo):
    if not n_clicks:
        raise PreventUpdate

    if not name:
        return "Please enter a name!", []

    story_scenes = generate_story_from_llama3(name, age, moral, scenes, length)

    print(story_scenes)

    if not story_scenes:
        return "Story generation failed. Try again.", []

    story_text = ""
    image_divs = []

    for i, sc in enumerate(story_scenes):
        title = sc.get("title", f"Scene {i+1}")
        text = sc.get("text", "")
        bg_prompt = sc.get("background", f"cartoon scene for a children's story about {moral}")
        
        story_text += f"\n🧩 {title}\n{text}\n"

        # --- Image Generation ---
        img_path = f"outputs/scene_{i+1}.png"
        if not os.path.exists(img_path):
            image = sd_model(
                prompt=f"{bg_prompt}, colorful, cartoon, storybook illustration for kids",
                guidance_scale=7.0
            ).images[0]
            image.save(img_path)

        img_src = display_image(img_path)
        image_divs.append(html.Img(src=img_src, style={
            'width': '80%', 'borderRadius': '10px', 'marginBottom': '10px'
        }))

    return story_text, image_divs


# --------------------- PDF Export ---------------------
@app.callback(
    Output("pdf_status", "children"),
    Input("pdf_btn", "n_clicks"),
    [State("story_output", "children"),
     State("scene_slider", "value")]
)
def export_pdf(n_clicks, story_text, scene_count):
    if not n_clicks:
        raise PreventUpdate

    pdf_path = "outputs/storybook.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Write story text
    y = height - 50
    c.setFont("Helvetica", 12)
    for line in story_text.split("\n"):
        c.drawString(40, y, line[:120])
        y -= 16
        if y < 100:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 12)

    # Add images per scene
    for i in range(scene_count):
        img_path = f"outputs/scene_{i+1}.png"
        if os.path.exists(img_path):
            c.showPage()
            img = ImageReader(img_path)
            c.drawImage(img, 50, 150, width=500, preserveAspectRatio=True, mask='auto')
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, 100, f"Scene {i+1}")

    c.save()
    return "✅ Storybook exported to outputs/storybook.pdf!"

# --------------------- Run ---------------------
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
