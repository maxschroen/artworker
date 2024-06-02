## -- STD LIB IMPORTS --
import re
import unicodedata
## -- EXT LIB IMPORTS --
from PIL import Image
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