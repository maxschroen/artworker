## -- STD LIB IMPORTS --
import requests
import shutil
import os
import json
import base64
import sys
import html
import time
import threading
## -- EXT LIB IMPORTS --
from InquirerPy import prompt
## -- LOCAL IMPORTS --
import config   # constants
import utils    # utility functions

## -- Functions --
def print_title() -> None:
    """
    Prints the title of the script.

    Args:
    None

    Returns:
    None
    """
    print("  __          _                      _              ____   ")
    print(" / /__ _ _ __| |___      _____  _ __| | _____ _ __ / /\\ \\  ")
    print("/ // _` | '__| __\\ \\ /\\ / / _ \\| '__| |/ / _ \\ '__/ /  \\ \\ ")
    print("\\ \\ (_| | |  | |_ \\ V  V / (_) | |  |   <  __/ | / /   / / ")
    print(" \\_\\__,_|_|   \\__| \\_/\\_/ \\___/|_|  |_|\\_\\___|_|/_/   /_/  by maxschroen")
    print("")

def print_error_and_trigger_exit(e: Exception, message = "") -> None:
    """
    Prints an error message and triggers script exit.

    Args:
    e (Exception): Exception object.
    message (str): Optional message to print.

    Returns:
    None
    """
    # Print optional message
    if message != "":
        print(f"✗ {message}")
    # Print exception message
    print(f"✗ {e}")
    # Initiate graceful exit
    clean_up_and_exit(config.TEMP_ARTWORK_DIR_PATH)

def loading_spinner(loading_text: str, success_text: str, failure_text: str) -> None:
    """
    Display loading spinner with text.

    Args:
    text (str): Text to display with loading spinner.
    
    Returns:
    None
    """
    # Define loading spinner animation
    animation = "|/-\\"
    idx = 0
    # Get current thread
    t = threading.current_thread()
    # Show animation while attribute is set
    while getattr(t, "is_loading", True):
        print(f"  {loading_text}..." + animation[idx % len(animation)], end="\r")
        idx += 1
        time.sleep(0.1)
    # Print success or failure text based on success status attribute
    if getattr(t, "finished_successfully", True):
        print(f"{config.ANSI_FORMATS['FONT_GREEN']}✔{config.ANSI_FORMATS['END']} {success_text}")
    else:
        print(f"{config.ANSI_FORMATS['FONT_RED']}✗{config.ANSI_FORMATS['END']} {failure_text}")
    
def spawn_loading_spinner_thread(loading_text: str, success_text: str, failure_text: str) -> threading.Thread:
    """
    Spawns a new thread for the loading spinner.

    Args:
    loading_text (str): Text to display with loading spinner.
    success_text (str): Text to display upon successful completion.
    failure_text (str): Text to display upon failure.

    Returns:
    thread (threading.Thread): Thread object for loading spinner.
    """
    thread = None
    try:
        # Spawn thread with target function and arguments
        thread = threading.Thread(target=loading_spinner, args=(loading_text, success_text, failure_text))
        # Set thread as daemon to allow for KeyboardInterrupt to stop thread
        thread.daemon = True                                                                                                
        # Set thread loading status to True to start animation  
        thread.is_loading = True                                                                                    
        # Set thread success status initial value
        thread.finished_successfully = False                                                                    
        # Start thread   
        thread.start()                                                                                                           
    except KeyboardInterrupt:
        pass
    return thread

def terminate_loading_spinner_thread(thread: threading.Thread, terminate_success: bool ) -> None:
    """
    Terminates the loading spinner thread and sets success status.

    Args:
    thread (threading.Thread): Thread object for loading spinner.
    terminate_success (bool): True if successful, False if failed.

    Returns:
    None
    """
    try:
        # Set thread loading status attribute to stop animation
        thread.is_loading = False
        # Set thread success status for conditional print of failure text                            
        thread.finished_successfully = {terminate_success}
        # Join thread back to main thread / end thread     
        thread.join()                                           
    except KeyboardInterrupt: 
        pass

def get_user_search() -> str:
    """
    Prompts user for a search term and returns the input.

    Returns:
    user_search (str): User input search term.
    """
    # Set up InquirerPy prompt question
    questions = [
        {
            "type": "input",
            "message": "Search for an artist and/or album:",
            "name": "user_search",
            "mandatory": True,
            "amark": "✔"
        }
    ]
    # Access user input from prompt
    user_search = prompt(questions)["user_search"]
    return user_search

def get_use_default_store() -> bool:
    """
    Prompts user to use the default store country or select a different one.

    Returns:
    use_default_store (bool): True if user wants to use the default store country, False if user wants to select a different store country.
    """
    # Set up InquirerPy prompt question
    questions = [
        {
            "type": "confirm",
            "message": "Use default store country (US)?",
            "name": "use_default_store",
            "default": True,
            "mandatory": True,
            "amark": "✔"
        }
    ]
    # Access user input from prompt
    use_default_store = prompt(questions)["use_default_store"]
    return use_default_store

def get_store_country_code() -> str:
    """
    Prompts user for a country selection and will return the corrseponding 2-letter country code.

    Returns:
    country_code (str): ISO 3166-1 alpha-2 country code.
    """
    # Set up InquirerPy prompt question
    questions = [
        {
            "type": "fuzzy",
            "message": "Select a store country: ",
            "name": "country",
            "choices": config.ISO_3166_1_ALPHA_2_CC.keys(),
            "mandatory": True,
            "amark": "✔"
        }
    ]
    # Access user input from prompt
    country = prompt(questions)["country"]
    # Get country code from dictionary
    country_code = config.ISO_3166_1_ALPHA_2_CC[country]
    return country_code

def get_albums_from_itunes(search_string: str, country_code: str, spinner_thread: threading.Thread) -> list:
    """
    Fetches albums from the iTunes API based on the search string and country code.

    Args:
    search_string (str): Formatted search string for the iTunes API.
    country_code (str): ISO 3166-1 alpha-2 country code.
    spinner_thread (threading.Thread): Thread object for loading spinner.

    Returns:
    albums (list): Dictionary of albums fetched from the iTunes API.
    """
    # Initialize albums dictionary
    albums = []
    # Set request url
    url = f"{config.SEARCH_API_BASE_URL}?term={search_string}&entity=album&country={country_code}&limit={config.ALBUM_RESULT_LIMIT}" # iTunes API URL
    try:
        # Send GET request to iTunes API
        response = requests.get(url)
        # Handle response status code
        if response.status_code == 200:
            # Terminate loading spinner thread with success message
            terminate_loading_spinner_thread(spinner_thread, True)
            # Parse JSON response
            albums = response.json()
            # Filter out non-album results and reduce to required properties
            albums = [
                {
                    "artist": album['artistName'],
                    "artist_id": album['artistId'],
                    "id": album['collectionId'],
                    "name": album['collectionName'],
                    "artwork_url": album['artworkUrl100'].replace("100x100bb", "1500x1500bb"),
                    "track_count": album['trackCount'],
                    "copyright": album['copyright'],
                    "release_date": album['releaseDate'],
                } for album in response.json()['results'] if album['wrapperType'] == 'collection' and album['collectionType'] == 'Album'
            ]
        else:
            # Terminate loading spinner thread with failure message
            terminate_loading_spinner_thread(spinner_thread, False)
    except Exception as e:
        # Terminate loading spinner thread with exception message
        terminate_loading_spinner_thread(spinner_thread, False)
        # Print error message and trigger exit
        print_error_and_trigger_exit(e)
    return albums

def create_dir(dir_path: str) -> None:
    """
    Creates a directory if it does not exist.

    Args:
    dir_path (str): Path to the directory.

    Returns:
    None
    """
    # Attempt to create directory if not exists
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    except Exception as e:
        # Print error message and trigger exit
        print_error_and_trigger_exit(e, "Failed to create directory")

def clean_up_and_exit(clean_up_path: str) -> None:
    """
    Exits the script with a message.

    Args:
    None

    Returns:
    None
    """
    print("\n  Cleaning up temporary files and directories...      ", end="", flush=True)
    # Attempt to remove temporary directory and files if exist
    try:
        if os.path.exists(clean_up_path):
            for f in os.listdir(clean_up_path):
                os.remove(os.path.join(clean_up_path, f))
            os.rmdir(clean_up_path)
    except Exception as e:
        # Print error message
        print(f"✗ {e}")
        # Exit script
        sys.exit()
    print(f"{config.ANSI_FORMATS['FONT_GREEN']}[DONE]{config.ANSI_FORMATS['END']}")
    print("  Exiting script...")
    sys.exit()

def validate_or_exit(container: list, message: str) -> None:
    """
    Validates a container and triggers exit if empty.

    Args:
    container (list): List to validate.
    message (str): Message to print if container is empty.

    Returns:
    None
    """
    # Check container content length
    if len(container) == 0:
        print(message)
        # Initiate graceful exit
        clean_up_and_exit(config.TEMP_ARTWORK_DIR_PATH)

def get_selected_album(albums: list) -> dict:
    """
    Prompts user to select an album from a list of albums.

    Args:
    albums (list): List of album dictionaries fetched from the iTunes API.

    Returns:
    album (dict): Dictionary of the selected album.
    """
    # Set up InquirerPy prompt question
    questions = [
        {
            "type": "list",
            "message": "Select an album:",
            "name": "selected_album",
            "choices": [f"{album['name']} - {album['artist']} ({album['release_date'].split('-')[0]})" for album in albums],
            "mandatory": True,
            "amark": "✔"
        }
    ]
    # Access user input from prompt
    selected_album = prompt(questions)["selected_album"]
    # Get selected album index
    selected_album_idx = [f"{album['name']} - {album['artist']} ({album['release_date'].split('-')[0]})" for album in albums].index(selected_album)
    # Get selected album from albums list
    album = albums[selected_album_idx]
    return album

def get_album_tracks_from_itunes(album_id: str, country_code: str, spinner_thread: threading.Thread) -> list:
    """
    Fetches tracks from the iTunes API based on album ID and country code.

    Args:
    album_id (str): Album ID.
    country_code (str): ISO 3166-1 alpha-2 country code.
    spinner_thread (threading.Thread): Thread object for loading spinner.

    Returns:
    tracks (list): Dictionary of tracks fetched from the iTunes API.
    """
    # Initialize tracks dictionary
    tracks = []
    # Set request URL
    url = f"{config.LOOKUP_API_BASE_URL}?id={album_id}&entity=song&country={country_code}"
    try:
        # Send GET request to iTunes API
        response = requests.get(url)
        # Handle response status code
        if response.status_code == 200:
            # Terminate loading spinner thread with success message
            terminate_loading_spinner_thread(spinner_thread, True)
            # Parse JSON response
            tracks = response.json()
            # Filter out non-track results and reduce to required properties
            tracks = [
                {
                    "id": track['trackId'],
                    "name": track['trackName'],
                    "number": track['trackNumber'],
                    "time_millis": track['trackTimeMillis'],
                    "time_parts": utils.millis_to_minutes_and_seconds(track['trackTimeMillis'])
                } for track in response.json()['results'] if track['wrapperType'] == 'track'
            ]
        else:
            # Terminate loading spinner thread with failure message
            terminate_loading_spinner_thread(spinner_thread, False)
    except Exception as e:
        # Terminate loading spinner thread with exception message
        terminate_loading_spinner_thread(spinner_thread, False)
        # Print error message and trigger exit
        print_error_and_trigger_exit(e)
    return tracks

def download_album_artwork(artwork_url: str, file_path: str, spinner_thread: threading.Thread) -> None:
    """
    Fetches album artwork from a URL and saves it to a temporary file.

    Args:
    artwork_url (str): URL of the album artwork.
    spinner_thread (threading.Thread): Thread object for loading spinner.

    Returns:
    None
    """
    try:
        # Send GET request to artwork URL
        response = requests.get(artwork_url, stream=True)
        # Handle response status code
        if response.status_code == 200:
            # Terminate loading spinner thread with success message
            terminate_loading_spinner_thread(spinner_thread, True)
            try:
                # Save artwork to file
                with open(file_path, "wb") as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)
            except Exception as e:
                # Print error message and trigger exit
                print_error_and_trigger_exit(e, "Error saving artwork to file")
        else:
            # Terminate loading spinner thread with failure message
            terminate_loading_spinner_thread(spinner_thread, False)
    except Exception as e:
        # Terminate loading spinner thread with exception message
        terminate_loading_spinner_thread(spinner_thread, False)
        # Print error message and trigger exit
        print_error_and_trigger_exit(e)

def convert_image_to_base64(image_path: str) -> str:
    """
    Converts an image file to a base64 encoded string.

    Args:
    image_path (str): Path to image file.

    Returns:
    encoded_image (str): Base64 encoded image string.
    """
    try:
        # Open image file and encode to base64
        with open(image_path, "rb") as f:
            encoded_image = base64.b64encode(f.read())
    except Exception as e:
        # Print error message and trigger exit
        print_error_and_trigger_exit(e, "Error encoding image to base64")
    return encoded_image

def get_template_path_from_options(options: dict) -> str:
    """
    Prompts user to select a template option and returns the corresponding file path.

    Args:
    options (dict): Dictionary of template options.

    Returns:
    template_path (str): File path of the selected template.
    """
    # Set up InquirerPy prompt question
    questions = [
        {
            "type": "list",
            "message": "Select a template option: ",
            "name": "template_selection",
            "choices": options.keys(),
            "mandatory": True,
            "amark": "✔"
        }
    ]
    # Access user input from prompt
    template_selection = prompt(questions)["template_selection"]
    # Get template path from dictionary
    template_path = options[template_selection]
    return template_path

def read_template_from_path(template_path: str) -> dict:
    """
    Reads a template JSON file from a file path.

    Args:
    template_path (str): Path to the template JSON file.

    Returns:
    template (dict): Template dictionary.
    """
    try:
        # Read template file
        template = json.load(open(template_path, "r"))
    except Exception as e:
        # Print error message and trigger exit
        print_error_and_trigger_exit(e, "Error reading template file")
    return template

def populate_template(template: dict, album: dict, tracks: list) -> str:
    """
    Populates a template with album and track data.

    Args:
    template (dict): Template dictionary.
    album (dict): Album dictionary.
    tracks (list): List of track dictionaries.

    Returns:
    svg_file_content (str): SVG file content.
    """
    try:
        # Populate template with album and track data using placeholders
        svg_file_content = "\n".join([
            template['svg_placeholders']['file_wrapper_open'],
            template['svg_placeholders']['background'],
            template['svg_placeholders']['album_artwork'].format(artwork_b64 = album["artwork_b64"]),
            template['svg_placeholders']['album_title'].format(album_title = html.escape(album["name"].upper())),
            template['svg_placeholders']['album_artist'].format(album_artist = html.escape(album["artist"].upper())),
            template['svg_placeholders']['album_copyright'].format(album_copyright = html.escape(album["copyright"].upper())),
            template['svg_placeholders']['header_separator'],
            "\n".join([template['svg_placeholders']['tracklist_item'].format(tracklist_item_x = template['tracklist_item_coordinates'][idx]['x'], tracklist_item_y = template['tracklist_item_coordinates'][idx]['y'], tracklist_item_text_anchor = template['tracklist_item_coordinates'][idx]['text_anchor'], track_title = html.escape(track['name'])) for idx, track in enumerate(tracks) if idx < template['limits']['tracklist_item_max']]),
            template['svg_placeholders']['album_release_label'],
            template['svg_placeholders']['album_release_year'].format(album_release_year = album["release_date"].split('-')[0]),
            template['svg_placeholders']['album_length_label'],
            template['svg_placeholders']['album_length'].format(album_length = f"{album['length_time_parts'][0]}:{album['length_time_parts'][1]}"),
            "\n".join([ template['svg_placeholders']['color_blob_item'].format(color_blob_item_x = template['color_blob_item_coordinates'][idx]['x'], color_blob_item_y = template['color_blob_item_coordinates'][idx]['y'], color_hex = color) for idx, color in enumerate(album['colors']) if idx < template['limits']['color_blob_item_max']]),
            template['svg_placeholders']['file_wrapper_close']
        ])
    except Exception as e:
        # Print error message and trigger exit
        print_error_and_trigger_exit(e, "Error populating template")
    return svg_file_content

def write_to_svg_file(file_path: str, content: str) -> None:
    """
    Writes content to an SVG file.

    Args:
    file_path (str): Path to the SVG file.
    content (str): SVG file content.

    Returns:
    None
    """
    try:
        # Write content to file
        with open(file_path, "w") as f:
            f.write(content)
    except Exception as e:
        # Print error message and trigger exit
        print_error_and_trigger_exit(e, "Error writing to file")

def main() -> None:
    """Envelopes main script execution."""
    # ------------------------------------- #
    # Print script title
    print_title() 
    # ------------------------------------- #
    # Get user search input
    user_search = get_user_search()
    # Format search string for iTunes API                                                 
    search_string = utils.format_search_string(user_search)                         
    # ------------------------------------- #
    # Set default storefront country code
    country_code = config.ISO_3166_1_ALPHA_2_CC["United States of America"]
    # Get user preference for default store country         
    use_default_store = get_use_default_store()                                     
    if not use_default_store:
        # Get user selected storefront country code
        country_code = get_store_country_code()                                     
    # ------------------------------------- #
    # Spawn loading spinner thread
    thread_album_loading = spawn_loading_spinner_thread("Fetching albums from iTunes store", "Successfully fetched albums from iTunes store", "Failed to fetch albums from iTunes store")
    # Get albums from iTunes API
    albums = get_albums_from_itunes(search_string, country_code, thread_album_loading)
    # Validate fetched albums
    validate_or_exit(albums, "No albums found matching search criteria. Try a different search term or store country.")
    # ------------------------------------- #
    # Get user selected album
    album = get_selected_album(albums)                                              
    # ------------------------------------- #
    # Spawn loading spinner thread
    thread_tracks_loading = spawn_loading_spinner_thread("Fetching tracks from iTunes store", "Successfully fetched tracks from iTunes store", "Failed to fetch tracks from iTunes store")
    # Get tracks for selected album from iTunes API
    tracks = get_album_tracks_from_itunes(album['id'], country_code, thread_tracks_loading)
    # Validate fetched tracks
    validate_or_exit(tracks, "No tracks found for selected album.\n  Likely the album tracks are not available for the selected store country. Please retry with a differrent selection.")
    # Calculate album length time parts
    album['length_time_parts'] = [ utils.pad(time_component, 2) for time_component in utils.millis_to_minutes_and_seconds(sum([track['time_millis'] for track in tracks]))]
    # ------------------------------------- #
    # Spawn loading spinner thread
    thread_artwork_loading = spawn_loading_spinner_thread("Fetching album artwork", "Successfully fetched album artwork", "Failed to fetch album artwork")
    # Create temporary artwork directory
    create_dir(config.TEMP_ARTWORK_DIR_PATH)     
    # Get album artwork from iTunes API                                          
    artwork_file_path = os.path.join(config.TEMP_ARTWORK_DIR_PATH, config.TEMP_ARTWORK_FILE_NAME)
    # Get album artwork from iTunes CDN resource 
    download_album_artwork(album['artwork_url'], artwork_file_path, thread_artwork_loading)
    # Convert album artwork to base64
    encoded_artwork = convert_image_to_base64(artwork_file_path)                                        
    album['artwork_b64'] = "data:image/png;base64," + str(encoded_artwork, encoding='utf-8')
    # Extract colors from album artwork
    album['colors'] = [utils.rgb_to_hex(color.rgb) for color in utils.extract_colors_from_image(artwork_file_path)] 
    # ------------------------------------- #
    # Get user selected template path
    template_path = get_template_path_from_options(config.TEMPLATE_OPTIONS)   
    # Load template JSON      
    template = read_template_from_path(template_path)
    # Populate template with album and track data
    svg_file_content = populate_template(template, album, tracks)
    # Generate file name slug                 
    out_file_name = utils.slug(f"{album['artist']} - {album['name']}")
    # Create output directory
    create_dir(config.OUTPUT_FOLDER)
    # Compose output file path
    out_file_path = os.path.join(config.OUTPUT_FOLDER, f"{out_file_name}.svg")
    # Write SVG content to file
    write_to_svg_file(out_file_path, svg_file_content)                             
    # ------------------------------------- #
    # Print success message
    print(f"{config.ANSI_FORMATS['FONT_GREEN']}✔{config.ANSI_FORMATS['END']} Successfully generated SVG file {config.ANSI_FORMATS['FONT_LIGHT_GREEN']}{out_file_path}{config.ANSI_FORMATS['END']}")
    # Initiate graceful exit            
    clean_up_and_exit(config.TEMP_ARTWORK_DIR_PATH)
    # ------------------------------------- #

if (__name__ == "__main__"):
    try:
        # Execute main script
        main()
    except KeyboardInterrupt as e:                                                  
        # Initiate graceful exit
        clean_up_and_exit(config.TEMP_ARTWORK_DIR_PATH)