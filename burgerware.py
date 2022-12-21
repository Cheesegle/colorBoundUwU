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

vidcap = cv2.VideoCapture('big_buck_bunny_720p_5mb.mp4')
success,image = vidcap.read()

while success:
    # get an image from the video
    frame = np.array(image)[...,:3]

    visname = 'BurgerWare'

    frame = frame.astype(np.uint8)

    #detect players
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    lower = np.array([9, 130, 180])
    upper = np.array([12, 150, 190])
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
    cv.imshow(visname, frame)
    cv.setWindowProperty(visname, cv.WND_PROP_TOPMOST, 1)

    # debug the loop rate
    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')
