from PIL import Image
import argparse
import numpy as np
import imageio
import cv2
import sys
import os

COLUMNS = 53
PIXEL_SIZE = 11
PIXEL_SPACING = 8

THEME_STEPS = 5
DEFAULT_THEME = "light"
DEFAULT_OUTPUT = "contribution.gif"

class Theme:

    def __init__(self, name: str):
        
        self.name = name
        self.images = []
        self.values = []
        self.cache = {}

        for i in range(THEME_STEPS):

            img = cv2.imread("./themes/{}/{}.png".format(name, i))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            self.images.append(img)
            self.values.append(min(i * 64, 255))

    def get_closest_image(self, value: int):

        if value in self.cache:
            return self.cache[value]

        closest_distance = float('inf')
        closest_value = None
        closest_img = None
        for i in range(len(self.values)):

            distance = abs(value - self.values[i])
            if distance < closest_distance:
                closest_distance = distance
                closest_value = self.values[i]
                closest_img = self.images[i]
        
        self.cache[closest_value] = closest_img
        return closest_img

        
    def validate(name: str):

        if not os.path.isdir("./themes/{}".format(name)):
            return False, "theme '{}' could not be found".format(name)

        for i in range(THEME_STEPS):

            img_path = "./themes/{}/{}.png".format(name, i)
            if not os.path.exists(img_path):
                return False , "image '{}.png' could not be found in theme '{}'".format(i, name)

            img = cv2.imread(img_path)
            if img.shape[0] != PIXEL_SIZE or img.shape[1] != PIXEL_SIZE:
                return False , "image '{}.png' in theme '{}' has incorrect dimensions ({}, {}), image should have dimensions ({}, {})".format(i, name, img.shape[0], img.shape[1], PIXEL_SIZE, PIXEL_SIZE)

        return True, ""

class Video:

    def __init__(self, name: str):
        
        self.name = name

        if name.endswith(".mp4"):
            
            cap = cv2.VideoCapture(name)
            _, frame = cap.read()

            # Get video info
            self.type = "mp4"
            self.width = frame.shape[1]
            self.height = frame.shape[0]
            self.aspect_ratio = self.width / self.height

            # Get the fps of the video
            major_ver, minor_ver, subminor_ver = (cv2.__version__).split('.')
            if int(major_ver) < 3:
                self.fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
            else:
                self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.spf = 1000 / self.fps

            cap.release()

        elif name.endswith(".gif"):            
            
            # Get gif info
            self.type = "gif"

        else:
            raise Exception

    def __iter__(self):
        return VideoIterator(self)

    def validate(name: str):

        if not os.path.exists(name):
            return False, "video '{}' could not be found".format(name)

        if name.endswith(".mp4"):

            cap = cv2.VideoCapture(name)
            if not cap.isOpened():
                return False, "video '{}' could not be opened".format(name)
            cap.release()

            return True, ""

        elif name.endswith(".gif"):
            return False, ".gif format is not supported yet"

        return False, "video '{}' is not of a supported format (.mp4, .gif)".format(name)

class VideoIterator:

    def __init__(self, video: Video):

        self.video = video

        if video.type == "mp4":
            self.capture = cv2.VideoCapture(video.name)
        elif video.type == "gif":
            pass

    def __next__(self):
        
        # Get the next available frame
        if self.video.type == "mp4":

            flag, frame = self.capture.read()
            if not flag:
                self.capture.release()
                raise StopIteration

            return frame, self.video.spf

        elif self.video.type == "gif":
            pass
        raise Exception

def main():

    theme = None
    video = None

    theme_name = DEFAULT_THEME
    video_name = None

    output = DEFAULT_OUTPUT

    # Video argument is required.
    if len(sys.argv) < 2:
        print("{}: missing file arguments".format(sys.argv[0]))
        return

    # Store the video argument
    video_name = sys.argv[1]

    # Ensure that the video is valid.
    valid, reason = Video.validate(video_name)
    if not valid:
        print("{}: {}".format(sys.argv[0], reason))
        return

    # See if the user inputted a theme.
    if len(sys.argv) > 2:
        theme_name = sys.argv[2]

    # Ensure that the theme is valid.
    valid, reason = Theme.validate(theme_name)
    if not valid:
        print("{}: {}".format(sys.argv[0], reason))
        return

    theme = Theme(theme_name)
    video = Video(video_name)

    rows = round(COLUMNS / video.aspect_ratio)
    contribution_width = (PIXEL_SIZE * COLUMNS) + (PIXEL_SPACING * (COLUMNS - 1))
    contribution_height = (PIXEL_SIZE * rows) + (PIXEL_SPACING * (rows - 1))

    frames = []
    durations = []

    a = 0
    for frame, duration in video:

        print(a)

        frame = cv2.resize(frame, (COLUMNS, rows), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        contribution_frame = Image.new(mode="RGBA", size=(contribution_width, contribution_height))
        for i in range(rows):
            for j in range(COLUMNS):

                pixel = theme.get_closest_image(gray[i][j])

                top = i * (PIXEL_SIZE + PIXEL_SPACING)
                bottom = top + PIXEL_SIZE
                left = j * (PIXEL_SIZE + PIXEL_SPACING)
                right = left + PIXEL_SIZE

                contribution_frame.paste(pixel, box=(left, top, right, bottom))

        frames.append(contribution_frame)
        durations.append(duration)
        a += 1

    frames[0].save(output, save_all=True, append_images=frames[1:], duration=durations, loop=0, transparency=0)

if __name__ == '__main__':
    main()