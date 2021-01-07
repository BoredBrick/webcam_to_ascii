import numpy as np
import PySimpleGUI as sg
from PIL import Image
from numpy import asarray
from cv2 import cv2
from colour import Color
import time


def image_to_ascii(image, intensity_correction, scale, inverted):
    WIDTH_ADJUST_RATIO = 7/4
    ascii_chars = ' .,:;irsXA253hMHGS#9B&@'

    # Because ascii characters are more tall than wide, we need to adjust the image size,
    # so that the final picture retains it's shape and isn't disorted. I found
    # out that 7/4 works fairly well.
    newSize = (round(image.size[0] * scale * WIDTH_ADJUST_RATIO),
               round(image.size[1] * scale))
    image_resized = image.resize(newSize)

    # get luminosity of each pixel using average method: (R + G + B) / 3
    image = np.sum(np.asarray(image_resized), axis=2) / 3

    # normalise the luminosities for easier manipulation and flip the values, so that the
    # brightest pixel map to the space character and the darkest one to @.
    image -= image.min()
    image = (1.0 - image/image.max())
    if not inverted:
        image = abs(1-image)

    # Intensities are now raised to the power of the intensity correction
    # which alters the intensity histogram of the image and gives us some
    # some freedom to counteract very dark or light images. They are then multiplied
    # by highest index of chars and later rounded to integers, which maps every
    # intensity value of the original image to an index of the ascii character array.
    image = image**intensity_correction*(len(ascii_chars)-1)

    output = ""
    for i in range(newSize[1]):
        if (i != 0):
            output += '\n'
        for j in range(newSize[0]):
            lum = round(image[i][j])
            output += ascii_chars[lum % len(ascii_chars)]
    return output


def new_layout(scale, font_size, color):
    layout = [[sg.Titlebar("webcam_to_ascii")],
              [sg.Txt("", key="_FPS_", size=(10, 1))],

              [sg.Txt(size=(112*int(scale*10), 48*int(scale*10)),
                      font=('Courier', font_size), key='Text', text_color=color)],
              [sg.Button('Rainbow mode', key='_B_', size=(22, 1)),
               sg.Slider(range=(1, 10), default_value=10, resolution=1,
                         orientation="horizontal", key="_S2_", disable_number_display=True, enable_events=True, pad=(5, 0)),
               sg.Slider(range=(0.5, 5), default_value=3, resolution=0.1,
                         orientation="horizontal", key="_S1_",
                         disable_number_display=True),
               sg.Radio("10%", "radio", key="_R1_",
                        default=True, enable_events=True),
               sg.Radio("20%", "radio", key="_R2_", enable_events=True),
               sg.Radio("30%", "radio", key="_R3_", enable_events=True),
               sg.Radio("40%", "radio", key="_R4_", enable_events=True),
               sg.In("", key="_BCOLOR_", visible=False, enable_events=True),
               sg.ColorChooserButton("Choose color", target="_BCOLOR_", size=(16, 1)), ],

              [sg.Button("About", key="_BABOUT_", size=(22, 1), enable_events=True),
               sg.Txt('Rainbow mode speed:', key='_SSPEED_', size=(17, 1), pad=((7, 0), (0, 0))),
               sg.Txt('3', key='_RIGHT2_', size=(2, 1)),
               sg.Txt('Intensity:', key='_SINTENS_', size=(7, 1), pad=((25, 0), (0, 0))),
               sg.Txt('10', key='_RIGHT_', size=(2, 1)),
               sg.Txt('Scale percentage', key='_SCALE_', size=(15, 1), pad=((105, 0), (0, 0))),
               sg.Button("Invert", key='_BINVERT_', size=(16, 1), pad=((81, 0), (0, 0)))]]
    return layout


def new_window():
    window = sg.Window("Title", layout, location=(0, 0),
                       element_padding=(0, 0), return_keyboard_events=True,
                       keep_on_top=False, finalize=True,  no_titlebar=True)
    return window


def new_color_range(rainbow_speed):
    # scale for rainbow speed is 25 colors per level
    # the more colors the slower rainbow
    color_range1 = list(Color("red").range_to(Color("green"), 25 * rainbow_speed))
    color_range2 = list(Color("green").range_to(Color("blue"), 25 * rainbow_speed))
    color_range3 = list(Color("blue").range_to(Color("red"), 25 * rainbow_speed))
    color_range = color_range1 + color_range2 + color_range3
    return color_range


cam = cv2.VideoCapture(0)
if cam is None or not cam.isOpened():
    sg.popup_error("ERROR: Webcam not found.", no_titlebar=True)
    exit()

width = cam.get(3)
height = cam.get(4)
if width != 640 or height != 480:
    sg.popup("Detected different camera resolution than the one currently supported (640x480). The program will now"
             " try to rescale your resolution.")
    cam.set(3, 640)
    cam.set(4, 480)

rainbow_mode = False
scale = 0.1
sg.theme('DarkAmber')

color = sg.theme_text_color()
layout = new_layout(0.1, 10, color)
window = new_window()
color_index = 0
color_range = new_color_range(1)
invert = False
fps_counter = 0
start_time = time.time()

while True:
    event, values = window.Read(timeout=5)

    if event == '_BABOUT_':
        sg.popup_ok("Final project for UNIX-Programming Development course\nMade by Daniel Caban"
                    "\nFaculty of management science and informatics\nUniversity of Žilina\n",
                    no_titlebar=True, keep_on_top=True, font=('Courier', 15))

    elif event == '_B_':
        rainbow_mode = not rainbow_mode
        window['_B_'].update(
            ("Rainbow mode", "Disable rainbow mode")[rainbow_mode])
        if not rainbow_mode:
            window['Text'].update(text_color=color)

    elif event == "_BINVERT_":
        invert = not invert

    elif event == '_BCOLOR_':
        color = values[event]
        if color == 'None':
            continue
        window['Text'].update(text_color=color)
        rainbow_mode = False

    elif event in ('_R1_', '_R2_', '_R3_', '_R4_'):
        rainbow_speed = values['_S2_']
        intensity = values['_S1_']
        num = int(event[2])
        window.close()
        scale = num / 10
        font_size = 10 if num == 1 else (7-num)
        layout = new_layout(scale, font_size, color)
        window = new_window()
        window[event].update(True)
        window['_S1_'].update(intensity)
        window['_S2_'].update(rainbow_speed)
        window['_B_'].update(
            ("Rainbow mode", "Disable rainbow mode")[rainbow_mode])
        continue

    elif event == 'Escape:27' or event == None:
        break  # esc to quit

    elif event == '_S2_':
        color_range = new_color_range(int(11 - values['_S2_']))
        continue

    if rainbow_mode:
        # Values are substracted from 11, so that the slider goes from slowest to fastest
        color_index = color_index % int(((11-values['_S2_']) * 25 * 3))
        window['Text'].update(text_color=color_range[color_index])
        color_index += 1

    ret_val, img = cam.read()
    img = Image.fromarray(img)
    out_string = image_to_ascii(img, values['_S1_'], scale, invert)

    window['Text'].update(out_string)
    window.Element('_RIGHT_').Update(values['_S1_'])
    window.Element('_RIGHT2_').Update(int(values['_S2_']))

    fps_counter += 1
    if (time.time() - start_time) > 1:
        fps = int(fps_counter / (time.time() - start_time))
        window.Element('_FPS_').Update("FPS: " + str(fps))
        fps_counter = 0
        start_time = time.time()

window.close()
