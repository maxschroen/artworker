## -- STD LIB IMPORTS --
import re
import unicodedata
## -- EXT LIB IMPORTS --
import Pylette as pylette # https://github.com/qTipTip/Pylette

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

# @TODO: At some point replace this with self-built solution
def extract_colors_from_image(image_path: str) -> pylette.Palette:
    """
    Extracts a color palette from an image file.

    Args:
    image_path (str): Path to image file.

    Returns:
    palette (pylette.Palette): Extracted color palette.
    """
    palette = pylette.extract_colors(image=image_path, palette_size=5, resize=True, mode='MC', sort_mode='luminance')
    return palette

def rgb_to_hex(rgb: tuple[int,int,int]) -> str:
    """
    Converts an RGB color tuple to a hex color string.

    Args:
    rgb (tuple[int,int,int]): RGB color tuple.

    Returns:
    hex_color (str): Hex color string.
    """
    hex_color = '#%02x%02x%02x' % rgb
    return hex_color