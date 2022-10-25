from alive_progress import alive_bar
import multiprocessing
from PIL import Image
import numpy as np
import argparse
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
        self.cache = []

        for i in range(THEME_STEPS):

            # For each contribution box store both its image and grayscale value.
            img = cv2.imread("./themes/{}/{}.png".format(name, i))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            self.images.append(img)
            self.values.append(min(i * 64, 255))

        # Map each value 0-255 with an image.
        for i in range(256):

            # Find the closest grayscale box value for this value.
            closest_distance = float('inf')
            closest_img = None
            for j in range(len(self.values)):

                distance = abs(i - self.values[j])
                if distance < closest_distance:
                    closest_distance = distance
                    closest_img = self.images[j]

            self.cache.append(closest_img)

    def get_closest_image(self, value: int):
        value = max(min(value, 255), 0)
        return self.cache[value]
        
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
            self.num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Get the fps of the video
            major_ver, minor_ver, subminor_ver = (cv2.__version__).split('.')
            if int(major_ver) < 3:
                self.fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
            else:
                self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.mspf = 1000 / self.fps

            cap.release()

        elif name.endswith(".gif"):            
            
            gif = Image.open(name)

            # Get gif info
            self.type = "gif"
            self.width, self.height = gif.size
            self.aspect_ratio = self.width / self.height
            self.num_frames = 0

            # Count number of frames
            while True:
                try:
                    gif.seek(self.num_frames)
                    self.num_frames += 1
                except:
                    break

            gif = None

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

            img = Image.open(name)
            if img == None:
                return False, "video '{}' could not be opened".format(name)

            if 'duration' not in img.info:
                return False, "video '{}' not of .gif format".format(name)

            img = None
            return True, ""

        return False, "video '{}' is not of a supported format (.mp4, .gif)".format(name)

class VideoIterator:

    def __init__(self, video: Video):

        self.video = video

        if video.type == "mp4":
            self.capture = cv2.VideoCapture(video.name)
        elif video.type == "gif":
            self.gif = Image.open(video.name)
            self.current_frame = 0
            self.gif.seek(0)

    def __next__(self):
        
        # Get the next available frame
        if self.video.type == "mp4":

            flag, frame = self.capture.read()
            if not flag:
                self.capture.release()
                raise StopIteration

            return frame, self.video.mspf

        elif self.video.type == "gif":
            
            try:
                self.gif.seek(self.current_frame)
                self.current_frame += 1
                return np.array(self.gif), self.gif.info['duration']
            except EOFError:
                raise StopIteration

        raise Exception

def generate_contribution_frame(args):
    
    frame = args[0]
    theme = args[1]
    rows = args[2]
    contribution_width = args[3]
    contribution_height = args[4]

    # Take the frame, downsize it to the correct size.
    frame = cv2.resize(frame, (COLUMNS, rows), interpolation=cv2.INTER_AREA)

    # Convert the frame to grayscale if it is not grayscale.
    gray = frame
    if len(frame.shape) == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Create the new frame to store the contribution gif frame.
    contribution_frame = Image.new(mode="RGBA", size=(contribution_width, contribution_height))
    for i in range(rows):
        for j in range(COLUMNS):

            # For each pixel in the grayscale, match it to a git contribution box.
            pixel = theme.get_closest_image(gray[i][j])

            # Find the bounding box to paste the contribution box into.
            top = i * (PIXEL_SIZE + PIXEL_SPACING)
            bottom = top + PIXEL_SIZE
            left = j * (PIXEL_SIZE + PIXEL_SPACING)
            right = left + PIXEL_SIZE

            # Paste the contribution box
            contribution_frame.paste(pixel, box=(left, top, right, bottom))
    
    return contribution_frame

def main():

    # Generate the argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="A video file. Currently supported formats are .mp4 and .gif.")
    parser.add_argument("-t", "--theme", help="The name of a theme located in the themes directory.", default=DEFAULT_THEME)
    parser.add_argument("-o", "--output", help="The name of the file where the gif should be saved.", default=DEFAULT_OUTPUT)

    # Parse the arguments
    args = parser.parse_args()

    # Set variables
    theme = None
    video = None
    video_name = args.input
    theme_name = args.theme
    output = args.output

    # Ensure that the video is valid.
    valid, reason = Video.validate(video_name)
    if not valid:
        print("{}: {}".format(sys.argv[0], reason))
        return
        
    # Ensure that the theme is valid.
    valid, reason = Theme.validate(theme_name)
    if not valid:
        print("{}: {}".format(sys.argv[0], reason))
        return

    # Theme name and video are valid, create the objects
    theme = Theme(theme_name)
    video = Video(video_name)

    # Figure out how many rows are required for the image.
    rows = round(COLUMNS / video.aspect_ratio)
    contribution_width = (PIXEL_SIZE * COLUMNS) + (PIXEL_SPACING * (COLUMNS - 1))
    contribution_height = (PIXEL_SIZE * rows) + (PIXEL_SPACING * (rows - 1))

    # Create the pool.
    pool = multiprocessing.Pool()

    # Create lists to store arguments and duration data.
    durations = []
    args = []

    # Loop through every frame and duration in the video
    for frame, duration in video:
        args.append((frame, theme, rows, contribution_width, contribution_height))
        durations.append(duration)

    contribution_frames = []
    print("\nRendering frames...")
    with alive_bar(video.num_frames) as bar:
        for result in pool.imap(generate_contribution_frame, args):
            contribution_frames.append(result)
            bar()

    # Save all frames as a gif.
    print("\nSaving frames to '{}'...".format(output))
    with alive_bar(0) as bar:
        contribution_frames[0].save(output, format="GIF", save_all=True, append_images=contribution_frames[1:], duration=durations, loop=0, transparency=0)
        bar()
    
    print("\nDone!")

if __name__ == '__main__':
    main()