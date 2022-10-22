import numpy as np
import sys
import cv2
import os

DEFAULT_THEME = "light"
GRID_SPACING = 8
COLUMNS = 53

def validate_video(video: str):

    if not os.path.exists(video):
        return False, "video '" + video + " could not be found"

    return True, None

def validate_theme(theme: str):

    if not os.path.isdir("./themes/" + theme):
        return False, "theme '" + theme + "' could not be found"

    return True, None

def main():
    
    theme = DEFAULT_THEME
    video = None

    # Video argument is required.
    if len(sys.argv) < 2:
        print(sys.argv[0] + ": missing file arguments")
        return

    # Store the video argument
    video = sys.argv[1]

    # Ensure that the video is valid.
    valid, reason = validate_video(video)
    if not valid:
        print(sys.argv[0] + ": " + reason)
        return

    # See if the user inputted a theme.
    if len(sys.argv) > 2:
        theme = sys.argv[2]

    # Ensure that the theme is valid.
    valid, reason = validate_theme(theme)
    if not valid:
        print(sys.argv[0] + ": " + reason)
        return

    

if __name__ == '__main__':
    main()