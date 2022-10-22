import numpy as np
import cv2
import sys
import os

COLUMNS = 53
PIXEL_SIZE = 11
PIXEL_SPACING = 8

THEME_STEPS = 5
DEFAULT_THEME = "light"

def validate_video(video: str):

    if not os.path.exists(video):
        return False, "video '{}' could not be found".format(video)

    return True, ""

def validate_theme(theme: str):

    if not os.path.isdir("./themes/" + theme):
        return False, "theme '{}' could not be found".format(theme)

    for i in THEME_STEPS:

        img_path = "./themes/{}/{}.png".format(theme, i)
        if not os.path.exists(img_path):
            return False , "image '{}.png' could not be found in theme '{}'".format(i, theme)

        img = cv2.imread(img_path)
        if img.shape[0] != PIXEL_SIZE or img.shape[1] != PIXEL_SIZE:
            return False , "image '{}.png' has incorrect dimensions ({}, {}), image should have dimensions ({}, {})".format(img.shape[0], img.shape[1], PIXEL_SIZE, PIXEL_SIZE)

    return True, ""

def main():
    
    theme = DEFAULT_THEME
    video = None

    # Video argument is required.
    if len(sys.argv) < 2:
        print("{}: missing file arguments".format(sys.argv[0]))
        return

    # Store the video argument
    video = sys.argv[1]

    # Ensure that the video is valid.
    valid, reason = validate_video(video)
    if not valid:
        print("{}: {}".format(sys.argv[0], reason))
        return

    # See if the user inputted a theme.
    if len(sys.argv) > 2:
        theme = sys.argv[2]

    # Ensure that the theme is valid.
    valid, reason = validate_theme(theme)
    if not valid:
        print("{}: {}".format(sys.argv[0], reason))
        return

    width = (PIXEL_SIZE * COLUMNS) + (PIXEL_SPACING * (COLUMNS - 1))
    

if __name__ == '__main__':
    main()