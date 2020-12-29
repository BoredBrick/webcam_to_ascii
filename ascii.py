import numpy as np
import PySimpleGUI as sg
from PIL import Image
from numpy import asarray
from cv2 import cv2
from colour import Color

def image_to_ascii(image, intensity_correction, scale):
    WIDTH_ADJUST_RATIO = 7/4
    ascii_chars = ' .,:;irsXA253hMHGS#9B&@'
    image = image.convert("LA")
    newSize = (round(image.size[0] * scale * WIDTH_ADJUST_RATIO),
               round(image.size[1] * scale))
    image_resized = image.resize(newSize)
    image = np.sum(np.asarray(image_resized), axis=2)
    image -= image.min()
    image = (1.0 - image/image.max())**intensity_correction*(len(ascii_chars)-1)

    output = ""
    for i in range(newSize[1]):
        if (i != 0):
            output += '\n'
        for j in range(newSize[0]):
            lum = round(image[i][j])
            output += ascii_chars[lum % len(ascii_chars)]
    return output

def new_layout(scale, font_size):
    layout = [[sg.Txt(size=(112*int(scale*10), 48*int(scale*10)),
                      font=('Courier', font_size), key='Text')],
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
               sg.Radio("40%", "radio", key="_R4_", enable_events=True), ],

              [sg.Button("About", key="_BABOUT_", size=(22, 1), enable_events=True),
               sg.Txt('Rainbow mode speed:', key='_SSPEED_', size=(17, 1), pad=((7, 0), (0, 0))),
               sg.Txt('3', key='_RIGHT2_', size=(2, 1)),
               sg.Txt('Intensity:', key='_SINTENS_', size=(7, 1), pad=((25, 0), (0, 0))),
               sg.Txt('10', key='_RIGHT_', size=(2, 1)),
               sg.Txt('Scale percentage', key='_SCALE_', size=(15, 1), pad=((105, 0), (0, 0)))]]
    return layout

def new_window():
    window = sg.Window("Title", layout, location=(0, 0),
                       element_padding=(0, 0), return_keyboard_events=True,
                       keep_on_top=True, finalize=True, grab_anywhere=True, no_titlebar=True)
    return window

def new_color_range(rainbow_speed):
    color_range1 = list(Color("red").range_to(Color("green"), 25 * rainbow_speed))
    color_range2 = list(Color("green").range_to(Color("blue"), 25 * rainbow_speed))
    color_range3 = list(Color("blue").range_to(Color("red"), 25 * rainbow_speed))
    color_range = color_range1 + color_range2 + color_range3
    return color_range

cam = cv2.VideoCapture(0)
rainbow_mode = False
scale = 0.1
sg.theme('DarkAmber')

layout = new_layout(0.1, 10)
window = new_window()
color_index = 0
color_range = new_color_range(1)

while True:
    event, values = window.Read(timeout=0)
    if event == '_BABOUT_':
        sg.popup_ok("Final project for UNIX-Programming Development course\nMade by Daniel Caban"
                    "\nFaculty of management science and informatics\nUniversity of Žilina\n"
                    "Press ESC to end application, Right-click to control sliders",
                    no_titlebar=True, keep_on_top=True, font=('Courier', 15))

    elif event == '_B_':
        rainbow_mode = not rainbow_mode
        window['_B_'].update(
            ("Rainbow mode", "Disable rainbow mode")[rainbow_mode])
        if not rainbow_mode:
            window['Text'].update(text_color=sg.theme_text_color())

    elif event in ('_R1_', '_R2_', '_R3_',  '_R4_'):
        rainbow_speed = values['_S2_']
        intensity = values['_S1_']
        num = int(event[2])
        window.close()
        scale = num / 10
        font_size = 10 if num == 1 else (7-num)
        layout = new_layout(scale, font_size)
        window = new_window()
        window[event].update(True)
        window['_S1_'].update(intensity)
        window['_S2_'].update(rainbow_speed)
        window['_B_'].update(
            ("Rainbow mode", "Disable rainbow mode")[rainbow_mode])
        continue

    elif event == 'Escape:27':
        break  # esc to quit

    elif event == '_S2_':
        color_range = new_color_range(int(11 - values['_S2_']))
        continue

    if rainbow_mode:
        color_index = color_index % int(((11-values['_S2_']) * 25 * 3))
        window['Text'].update(text_color=color_range[color_index])
        color_index += 1

    ret_val, img = cam.read()
    img = Image.fromarray(img)
    out_string = image_to_ascii(img, values['_S1_'], scale)

    window['Text'].update(out_string)
    window.Element('_RIGHT_').Update(values['_S1_'])
    window.Element('_RIGHT2_').Update(int(values['_S2_']))

window.close()
