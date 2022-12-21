import cv2 as cv
import numpy as np
import os
from time import time
from time import sleep
import dxcam
import win32gui, win32api, win32con
import math
import ctypes
import mouse

toplist, winlist = [], []
def enum_cb(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
win32gui.EnumWindows(enum_cb, toplist)

krunker = [(hwnd, title) for hwnd, title in winlist if 'krunker' in title.lower()]
# just grab the hwnd for first window matching krunker
krunker = krunker[0]
hwnd = krunker[0]

win32gui.SetForegroundWindow(hwnd)
bbox = win32gui.GetWindowRect(hwnd)

wsize = 400

bbox_list = list(bbox)
bbox_list[0] = int((1920 / 2) - wsize)
bbox_list[1] = int((1080 / 2) - wsize)
bbox_list[2] = int((1920 / 2) + wsize)
bbox_list[3] = int((1080 / 2) + wsize)

bbox = tuple(bbox_list)

camera = dxcam.create(output_color="BGRA")
camera.start(target_fps=144, region=bbox)

loop_time = time()
while(True):

    # get an updated image of the game
    frame = np.array(camera.get_latest_frame())[...,:3]

    visname = 'BurgerWare'

    frame = frame.astype(np.uint8)

    #detect players
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    lower = np.array([7, 150, 190])
    upper = np.array([11, 200, 220])
    mask = cv.inRange(hsv, lower, upper)
    sel_color = cv.bitwise_and(frame, frame, mask=mask)

    # Convert from HSV to Gray
    sel_color = cv.cvtColor(sel_color, cv.COLOR_HSV2BGR)
    sel_color = cv.cvtColor(sel_color, cv.COLOR_BGR2GRAY)

    ret, thresh = cv.threshold(sel_color, 50, 255, cv.THRESH_BINARY)

    # Find contours
    contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    if len(contours) != 0:
        c = max(contours, key = cv.contourArea)
        x, y, w, h = cv.boundingRect(c)
        if w > 1 and h > 1:
            y2 = y + round(h/2)
            x2 = x + round(w/2)
            cv.rectangle(frame, (x, y), (x+w, y+h), (0,0,255), 2)
            cv.circle(frame, (x2,y2), radius=5, color=(0, 255, 0), thickness=-1)
            if y != wsize and x != wsize:
                numx = x2 - wsize
                numy = y2 - wsize
                

                pos = win32api.GetCursorPos()
                x = int(pos[0] + numx)
                y = int(pos[1] + numy)
                # win32api.SetCursorPos((x,y))
                # mouse.click()

    #visual debug
    # cv.imshow(visname, frame)
    # cv.setWindowProperty(visname, cv.WND_PROP_TOPMOST, 1)

    # debug the loop rate
    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')
