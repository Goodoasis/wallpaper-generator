import base64
from io import BytesIO
from sys import maxsize as sys_maxsize
import random

from PIL import Image, ImageDraw, ImageFilter
import streamlit as st


back_garden = {
    'light-cyan': "#cffcff",
    'magic-mint': "#aaefdf",
    'light-green': "#9ee37d",
    'kelly-green': "#63c132",
    'india-green': "#358600ff"
    }

kill_bill = {
    'black': "#000000",
    'oxford-blue': "#14213d",
    'orange-web': "#fca311",
    'platinum': "#e5e5e5",
    'white': "#ffffff"
    }

colors_summer = {
    'amethyst': '#9b5de5',
    'magenta-crayola': '#f15bb5',
    'minion-yellow': '#fee440',
    'capri': '#00bbf9',
    'sea-green-crayola': '#00f5d4'
    }

colors_coffee = {
    'almond': '#ede0d4',
    'desert-sand': '#e6ccb2',
    'tan': '#ddb892',
    'cafe-au-lait': '#b08968',
    'coffee': '#7f5539',
    'brown-sugar': '#9c6644'
    }

colors_sky = {
    'flickr-pink': '#f72585',
    'byzantine': '#b5179e',
    'purple': '#7209b7',
    'purple-2': '#560bad',
    'trypan-blue': '#480ca8',
    'trypan-blue-2': '#3a0ca3',
    'persian-blue': '#3f37c9',
    'ultramarine-blue': '#4361ee',
    'dodger-blue': '#4895ef',
    'vivid-sky-blue': '#4cc9f0'
    }

cupcake = {
    'cotton-candy': "#fdc5f5",
    'mauve': "#f7aef8",
    'lavender-floral': "#b388eb",
    'cornflower-blue': "#8093f1",
    'sky-blue-crayola': "#72ddf7"
    }

default_colors = {
    "0": '#7cb8e6',
    "1": '#a587e8',
    "3": '#e687ba',
    "4": '#c0f59d',
    "5": '#f5ef9d',
    "6": '#f5a09d',
    "7": '#b49df5',
    "8": '#f8f7fa'
    }

PALETTES_NAMES = ["Back garden", "Kill_Bill", "Summer", "Coffee", "Sky", "Cup Cake", "Pastelle"]

if "palettes_list" not in st.session_state:
    st.session_state["palettes_list"] = [back_garden, kill_bill, colors_summer, colors_coffee, colors_sky, cupcake, default_colors]

if "palette_index" not in st.session_state:
    st.session_state["palette_index"] = None

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
    if palette == False:
        idx = PALETTES_NAMES.index(radio)
        palette = st.session_state.palettes_list[idx]
    elif isinstance(palette, str):
        idx = PALETTES_NAMES.index(radio)
        palette = st.session_state.palettes_list[idx]
    elif palette is not None:
        st.session_state.palette_index = st.session_state.palettes_list.index(palette)
    args = seed, palette
    st.session_state.palette = palette
    st.session_state.args = args

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
width_box = st.sidebar.number_input("width", min_value=10, max_value=6000, value=1920, step=1, on_change=None)
height_box = st.sidebar.number_input("height", min_value=10, max_value=5000, value=1080, step=1, on_change=None)

# Slider for grid dimensions.
grid_expander = st.sidebar.expander("Grid dimensions", expanded=False)
with grid_expander:
    grid_h = st.slider("rows", min_value=1, key='grid_h', max_value=6, value=2, step=1, on_change=None)
    grid_w = st.slider("columns", min_value=1, key='grid_w', max_value=6, value=3, step=1, on_change=None)

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
    st.session_state.palette_index = st.session_state.palettes_list.index(palette)
    # Init image.
    img = Image.new('RGB', (width_box, height_box))  # Create the canvas.
    draw = ImageDraw.Draw(img)
    col, row = grid_w, grid_h
    colstep = int(width_box // col)
    rowstep = int(height_box // row)
    for r in range(row):
        for c in range(col):
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
    st.button("Generate", key=None, help=None, on_click=change_args, args=(None, None,))

# Color palette Picker.
color_expander = st.sidebar.expander("Colors Palettes", expanded=False)
with color_expander:
    palette_miniatures = []
    for palette in st.session_state.palettes_list:
        # Make a miniature pic for palette color 200x20px!.
        pal_img = Image.new('RGB', (200, 20))
        pal_draw = ImageDraw.Draw(pal_img)
        pie = 200 // len(palette.values())
        for step, color in enumerate(palette.values()):
            x0 = pie * step
            x1 = pie * (step + 1)
            pal_draw.rectangle([x0, 0, x1, 20], fill=color)
        palette_miniatures.append(pal_img)

    # Column for radio buttons and column for palettes pictures.
    radio_col, miniature_col = st.columns(2)
    with st.form(key='my_form'):
        with radio_col:
            radio = st.radio("Pick a palette", PALETTES_NAMES, index=0, on_change=None)
        with miniature_col:
            st.header("")
            for i in palette_miniatures:
                st.image(i)
        submit_button = st.form_submit_button(label='Apply', on_click=change_args, args=(st.session_state.seed, radio,))

def get_image_download_link(img, filename, text):
    # Tranlate image to byt str dot download.
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href =  f'<a href="data:file/txt;base64,{img_str}" style="padding:7px; border: 0.1px solid gray; font-weight: 100; color: silver; text-decoration: none; border-radius: 7%;" download="{filename}">Download</a>'
    return href

# layout.
image_container = st.container()
spinner_container = st.empty()

# Spinner to load image.
with col2: # On side of Generate Button.
    with spinner_container:
        spinner = st.spinner("Generating wallpaper...")
    with spinner:
        generate_img(st.session_state.args)
        PIL_image = st.session_state.image	
        with image_container:
            st.image(PIL_image, channels="RGBA", output_format="png")

# Download link under image.
with image_container:
    st.markdown(get_image_download_link(PIL_image, "coblur.png", f"Download {width_box}x{height_box} version"), unsafe_allow_html=True)