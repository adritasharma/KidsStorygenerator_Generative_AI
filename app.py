import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from multimodal_pipeline import create_story_and_images
from utils import export_story_to_pdf
import os

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
app.title = "Kids Story Creator"

# --------------------- Layout ---------------------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("🧒 Kids Story Creator",
                        style={'textAlign': 'center', 'color': '#FF6F61', 'fontFamily': 'Comic Sans MS', 'marginTop': '20px'}),
                width=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Story Inputs", className="bg-warning text-dark fw-bold"),
                dbc.CardBody([
                    dbc.Input(id="kid_name", placeholder="Enter child's name", type="text", className="mb-2"),

                    dbc.Label("Select Age:", className="fw-bold"),
                    dcc.Slider(2, 12, 1, value=6, marks={i: str(i) for i in range(2, 13)}, id="age_slider",
                               className="mb-3"),

                    dbc.Label("Select Gender:", className="fw-bold"),
                    dbc.RadioItems(
                        options=[{"label": "Girl", "value": "girl"},
                                 {"label": "Boy", "value": "boy"}],
                        value="girl",
                        id="gender_select",
                        inline=True,
                        className="mb-3"
                    ),

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
                    dcc.Slider(1, 5, 1, value=1, marks={i: str(i) for i in range(1, 6)}, id="scene_slider",
                               className="mb-4"),

                    dbc.Label("Story Length:", className="fw-bold"),
                    dbc.RadioItems(
                        options=[{"label": "Short", "value": "short"},
                                 {"label": "Medium", "value": "medium"},
                                 {"label": "Long", "value": "long"}],
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

        dbc.Col([
            dbc.Card([
                html.Div(id="pdf_status", style={'color': 'green', 'marginTop': '10px'}),
                dbc.CardHeader("Generated Storybook", className="bg-info text-white fw-bold"),
                dbc.CardBody([
                    html.Div(id="story_output",
                             style={'whiteSpace': 'pre-wrap', 'fontFamily': 'Comic Sans MS', 'fontSize': '16px'}),
                    html.Hr(),
                    html.Div(id="images_output", style={'textAlign': 'center'}),
                ])
            ])
        ], width=8)
    ])
], fluid=True, style={'backgroundColor': '#FFFAE5', 'paddingBottom': '30px'})


# --------------------- Callbacks ---------------------
@app.callback(
    [Output("story_output", "children"),
     Output("images_output", "children")],
    Input("generate_btn", "n_clicks"),
    [State("kid_name", "value"),
     State("age_slider", "value"),
     State("gender_select", "value"),
     State("story_moral", "value"),
     State("scene_slider", "value"),
     State("story_length", "value"),
     State("upload_photo", "contents")]
)
def generate_story_callback(n_clicks, name, age, gender, moral, scenes, length, photo):
    if not n_clicks: raise PreventUpdate
    if not name: return "Please enter a name!", []
    print(f"Generating story for {name}, age: {age}")
    story_text, image_data = create_story_and_images(name, age, gender, moral, scenes, length, photo)
    image_divs = [
        html.Img(src=i["src"], style={'width': '80%', 'borderRadius': '10px', 'marginBottom': '10px'})
        for i in image_data
    ]
    return story_text, image_divs


@app.callback(
    Output("pdf_status", "children"),
    Input("pdf_btn", "n_clicks"),
    [State("story_output", "children"),
     State("scene_slider", "value")]
)
def export_pdf_callback(n_clicks, story_text, scene_count):
    if not n_clicks: raise PreventUpdate
    return export_story_to_pdf(story_text, scene_count)
