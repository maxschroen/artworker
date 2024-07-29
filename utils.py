## -- STD LIB IMPORTS --
import re
import unicodedata
## -- EXT LIB IMPORTS --
from PIL import Image, ImageFont
import numpy as np
from sklearn.cluster import KMeans
## -- LOCAL IMPORTS --
from config import LUMINANCE_WEIGHTS

## -- FUNCTIONS --
def format_search_string(user_search: str) -> str:
    """
    Formats user search string for use in iTunes API calls. 
    Will convert to lowercase, strip whitespace, and replace spaces with '+'.

    Args:
    user_search (str): User input search string.

    Returns:
    search_string (str): Formatted search string.
    """
    search_string = user_search.lower().strip().replace(" ","+")
    return search_string

def slug(raw: str) -> str:
    """
    Converts input raw string to a slug, leaving only alphanumerics and hyphens.
    Slugs are typically used for URLs or file names and contain only safe / unreserved characters.

    Args:
    raw (str): Input string to convert to slug.

    Returns:
    slug (str): Slugified string.
    """
    raw_normalized = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("ascii")   # Normalize unicode characters
    raw_normalized_compacted = raw_normalized.lower().strip().replace(" ","-")                      # Lowercase, strip whitespace, and replace spaces with '-'
    raw_normalized_compacted_validated  = re.sub(r"[^a-zA-Z0-9-]", "", raw_normalized_compacted)    # Validate allowed characters (alphanumeric and hyphen) by removing all other characters
    slug = re.sub(r"-{2,}", "-", raw_normalized_compacted_validated)                                # Deduplicate hyphenation
    return slug

def millis_to_minutes_and_seconds(millis: int) -> list[int,int]:
    """
    Converts integer milliseconds to a list of minute and second time parts.

    Args:
    millis (int): Time in milliseconds.

    Returns:
    time_parts (list[int,int]): List containing minute and second time parts.
    """
    total_seconds = millis / 1000
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    time_parts = [minutes, seconds]
    return time_parts

def pad(num: int, size: int) -> str:
    """
    Pads a number with leading zeros to a specified size.

    Args:
    num (int): Number to pad.
    size (int): Size of padded number.

    Returns:
    padded_num (str): Padded number.
    """
    padded_num = f"{num:0{size}}"
    return padded_num

def extract_colors_kmeans(image_path: str, num_colors: int, resize = False) -> list:
    """
    Extracts a color palette from an image using KMeans clustering.

    Args:
    image_path (str): Path to the image file.
    num_colors (int): Number of colors to extract.
    resize (bool): Resize the image to 256x256 pixels.

    Returns:
    colors (list | np.ndarray): List of RGB color values.
    """
    image = Image.open(image_path)                                                                  # Open the image file, resize if necessary
    if resize:
        image = image.resize((256, 256))
    image_array = np.array(image)                                                                   # Reshape the image array to a 2D array of pixels
    pixels = image_array.reshape(-1, 3)                       
    kmeans = KMeans(n_clusters=num_colors)                                                          # Fit the KMeans model to the pixel data
    kmeans.fit(pixels)              
    colors = kmeans.cluster_centers_                                                                # Get the RGB color values of the cluster centers                   
    colors = colors.astype(np.uint8)                                                                # Convert the colors to uint8 data type
    palette = colors.tolist()                                                                       # Convert the colors to a list                 
    return palette

def compute_luminance(color: list) -> float:
    """
    Computes the luminance of an RGB color using the weighted sum of the color channels.

    Args:
    color (list): RGB color list.

    Returns:
    luminance (float): Luminance value.
    """
    luminance = sum(LUMINANCE_WEIGHTS[i] * color[i] for i in range(len(color))) / 255
    return luminance                                                                                  


def rgb_to_hex(rgb: list | np.ndarray) -> str:
    """
    Converts an RGB color list to a hex color string.

    Args:
    rgb (list | np.ndarray): RGB color list.

    Returns:
    hex_color (str): Hex color string.
    """
    hex_color = '#%02x%02x%02x' % tuple(rgb)
    return hex_color

def get_font_size(element: str) -> int:
    """
    Extracts font size from an XML element.

    Args:
    element (str): XML element.

    Returns:
    font_size (int): Font size.
    """
    font_size = int(re.search(r"font-size=\"([0-9]+)\"", element).group(1))
    return font_size

def get_font_weight(element):
    """
    Extracts font weight from an XML element.

    Args:
    element (str): XML element.

    Returns: 
    font_weight (int): Font weight.
    """
    font_weight = int(re.search(r"font-weight=\"([0-9]+)\"", element).group(1))
    return font_weight

def check_overflow(text, element, calc_values):
    """
    Evaluates whether text overflows the document width and returns the element or a replacement element.

    Args:
    text (str): Text to evaluate.
    element (str): XML element.
    calc_values (dict): Boundary values for calculation.
    overflow_replacement (str): Replacement element.

    Returns:
    element (str): Element or replacement element.
    """
    font_size = get_font_size(element)
    font_weight = get_font_weight(element)
    font_name = calc_values['font_weight_mapping'][str(font_weight)]
    kerning_factor = calc_values['weight_kerning_factors'][str(font_weight)]
    font = ImageFont.truetype(font_name, font_size)
    text_length_px = font.getlength(text)  * kerning_factor
    overflows = bool((calc_values['dims']['doc_width'] - 2 * calc_values['dims']['x_padding']) - (round(text_length_px, None)) < 0)
    return overflows

# def check_collision(element1, text1, element2, text2):
#   font_size = get_font_size(element)
#   font_weight = get_font_weight(element)
#   font = ImageFont.truetype("Inter-Bold.otf", FONT_SIZE)
#   x = font.getlength(text1) * KERNING_FACTOR_700
#   y = font.getlength(text2) * KERNING_FACTOR_700
#   collides =  bool((calc_values['dims']['doc_width'] - 2 * calc_values['dims']['x_padding']) - (round((x + y), None)) < 0)
#   return collides