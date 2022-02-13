import json
import base64
import random
from io import BytesIO
from sys import maxsize as sys_maxsize

from PIL import Image, ImageDraw, ImageFilter
import streamlit as st


@st.cache(show_spinner=False)
def get_palettesColors():
    with open(r"data\\colors.json", 'r') as f:
        data = json.load(f)
    return data

COLORS_DATA = get_palettesColors()
PALETTES_NAMES = list(COLORS_DATA.keys())

if "palettes_list" not in st.session_state:
    st.session_state["palettes_list"] = list(COLORS_DATA.values())

if "palette" not in st.session_state:
    st.session_state["palette"] = None

if "seed" not in st.session_state: 
    st.session_state["seed"] = None

if "image" not in st.session_state:
    st.session_state["image"] = None

if "args" not in st.session_state:
    st.session_state["args"] = (st.session_state.seed, st.session_state.palette)


def change_args(*args):
    seed, palette = args
    if (palette == False) or (isinstance(palette, str)):
        idx = PALETTES_NAMES.index(radio)
        palette = st.session_state.palettes_list[idx]
    new_args = seed, palette
    st.session_state.palette = palette
    st.session_state.args = new_args

def random_palette(seed):
    if seed == None:
        seed = random.randint(-sys_maxsize, sys_maxsize)
    random.seed(seed)
    palette = random.choice(st.session_state.palettes_list)
    return palette

def random_color(palette):
    color = random.choice(list(palette.values()))
    return color

# Side bar
st.sidebar.subheader("Resolution")
width_box = st.sidebar.number_input("width", min_value=10, max_value=6000, value=1920, step=1)
height_box = st.sidebar.number_input("height", min_value=10, max_value=5000, value=1080, step=1)

# Slider for grid dimensions.
grid_expander = st.sidebar.expander("Grid dimensions", expanded=False)
with grid_expander:
    grid_h = st.slider("rows", min_value=1, max_value=6, value=2, step=1)
    grid_w = st.slider("columns", min_value=1, max_value=6, value=3, step=1)

# Slider for blur strengh
st.sidebar.header("")
slider_blur = st.sidebar.slider("Blur strength", min_value=0, max_value=1000, value=300, step=1)

def generate_img(*args):
    seed, palette = args[0]
    if seed == None:
        seed = random.randint(-sys_maxsize, sys_maxsize)
        st.session_state.seed = seed
    if palette == None:
        palette = random_palette(seed)
    random.seed(seed)
    st.session_state.palette = palette
    # Init image.
    img = Image.new('RGB', (int(width_box), int(height_box)))  # Create the canvas.
    draw = ImageDraw.Draw(img)
    colstep = int(width_box // grid_w)
    rowstep = int(height_box // grid_h)
    for r in range(grid_h):
        for c in range(grid_w):
            x0 = colstep * c
            y0 = rowstep * r
            x1 = colstep * (c + 1)
            y1 = rowstep * (r + 1)
            draw.rectangle([x0, y0 ,x1 ,y1], fill=random_color(palette=palette))
    # Save settings.
    change_args(st.session_state.seed, palette)
    # Save blurred image.
    st.session_state.image = img.filter(ImageFilter.GaussianBlur(radius=int(slider_blur)))

# Header
st.title("Wallpaper generator")
col1, col2 = st.columns(2)
with col1:
    st.button("Generate", on_click=change_args, args=(None, None,))

@st.cache(show_spinner=False)
def get_palettesMiniatures():
    palette_miniatures = []
    for palette in st.session_state.palettes_list:
        # Make a miniature pic for each color color palette 200x20px.
        pal_img = Image.new('RGB', (200, 20))
        pal_draw = ImageDraw.Draw(pal_img)
        pie = 200 // len(palette.values())
        for step, color in enumerate(palette.values()):
            x0 = pie * step
            x1 = pie * (step + 1)
            pal_draw.rectangle([x0, 0, x1, 20], fill=color)
        palette_miniatures.append(pal_img)
    return palette_miniatures

# Color palette Picker.
color_expander = st.sidebar.expander("Colors Palettes", expanded=False)
with color_expander:
    # Column for radio buttons and column for palettes pictures.
    radio_col, miniature_col = st.columns(2)
    palette_miniatures = get_palettesMiniatures()
    with st.form(key='my_form'):
        with radio_col:
            radio = st.radio("Pick a palette", PALETTES_NAMES, index=0)
        with miniature_col:
            st.header("")
            for miniature in palette_miniatures:
                st.image(miniature)
        submit_button = st.form_submit_button(label='Apply', on_click=change_args, args=(st.session_state.seed, radio,))

@st.cache(show_spinner=False)
def get_image_download_link(img, filename):
    # Tranlate image to bytes str dot download.
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href =  f'<a href="data:file/txt;base64,{img_str}" style="padding: 8px;border: 0.1px solid gray;font-weight: 100;color: #FAFAFA;text-decoration: none;border-radius: 7%;" download="{filename}">Download</a>'
    return href

# layout.
image_container = st.container()
spinner_container = st.empty()

# Spinner to load image.
with col2:  # On side of Generate Button.
    with spinner_container:
        spinner = st.spinner("Generating wallpaper...")
    with spinner:
        generate_img(st.session_state.args)
        PIL_image = st.session_state.image	
        with image_container:
            st.image(PIL_image, channels="RGB", output_format="png")

# Download link under image.
with image_container:
    name = f"wpp_{st.session_state.seed}.png"
    st.markdown(get_image_download_link(PIL_image, name), unsafe_allow_html=True)