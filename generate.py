import numpy as np
import cv2
import sys
import os

COLUMNS = 53
PIXEL_SIZE = 11
PIXEL_SPACING = 8

THEME_STEPS = 5
DEFAULT_THEME = "light"

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
            self.mspf = (1 / self.fps) * 1000

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
            return True, ""

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

            return frame, self.video.mspf

        elif self.video.type == "gif":
            pass
        raise Exception

def validate_theme(theme: str):

    if not os.path.isdir("./themes/" + theme):
        return False, "theme '{}' could not be found".format(theme)

    for i in range(THEME_STEPS):

        img_path = "./themes/{}/{}.png".format(theme, i)
        if not os.path.exists(img_path):
            return False , "image '{}.png' could not be found in theme '{}'".format(i, theme)

        img = cv2.imread(img_path)
        if img.shape[0] != PIXEL_SIZE or img.shape[1] != PIXEL_SIZE:
            return False , "image '{}.png' in theme '{}' has incorrect dimensions ({}, {}), image should have dimensions ({}, {})".format(i, theme, img.shape[0], img.shape[1], PIXEL_SIZE, PIXEL_SIZE)

    return True, ""

def main():
    
    theme = DEFAULT_THEME
    video = None
    video_name = None

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
        theme = sys.argv[2]

    # Ensure that the theme is valid.
    valid, reason = validate_theme(theme)
    if not valid:
        print("{}: {}".format(sys.argv[0], reason))
        return

    # Create the video object
    video = Video(video_name)

    rows = round(COLUMNS / video.aspect_ratio)
    contribution_width = (PIXEL_SIZE * COLUMNS) + (PIXEL_SPACING * (COLUMNS - 1))
    contribution_height = (PIXEL_SIZE * rows) + (PIXEL_SPACING * (rows - 1))

    for frame, duration in video:

        frame = cv2.resize(frame, (COLUMNS, rows), interpolation=cv2.INTER_AREA)

        cv2.imshow("test", frame)
        if cv2.waitKey(30) & 0xff == ord('q'):
           break
    cv2.destroyAllWindows()
    

if __name__ == '__main__':
    main()