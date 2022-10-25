# GIF-to-Contribution

## Description

Ever wanted to have a cool stylised GIF to put into your GitHub profile README.md files? Well I did! So I created a program that takes any video and creates GIF inspired by the GitHub contribution graph.

## Dependencies

 - [NumPy](https://numpy.org/install/)
 - [Pillow](https://pypi.org/project/Pillow/)
 - [opencv-python](https://pypi.org/project/opencv-python/)
 - [alive_progress](https://github.com/rsalmei/alive-progress)

## How to Use

1. Ensure that you have all required dependencies for this project. The required dependencies are listed above.
2. Clone the repository
```
git clone https://github.com/RohanFredriksson/GIF-to-Contribution.git
```
3. Get a video that you wish to turn into a contribution graph. Usually black and white videos work best.
4. Run the python script generate.py. This will create a GIF for your chosen video in your chosen theme.
```
python3 generator.py input [-h] [-t THEME] [-o OUTPUT]
```
5. To display your GIFs in your README files, do the following
```
![SpiralDark](examples/dark.gif#gh-dark-mode-only)
![SpriralLight](examples/light.gif#gh-light-mode-only)
```
This makes sure that the GIF that is shown matches the current theme of the user viewing your README.

## Themes
Currently the only supported GitHub themes are:
 - Light
 - Dark

When Halloween rolls around this year, I might be able to add the Halloween themes as well.

## Examples

![SpiralDark](examples/dark.gif#gh-dark-mode-only)
![SpriralLight](examples/light.gif#gh-light-mode-only)
