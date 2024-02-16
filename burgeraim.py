import cv2 as cv
import numpy as np
from time import time, sleep
import win32api
import mss

wsize = 400

l = int((1920 / 2) - wsize)
w = int((1080 / 2) - wsize)
t = int((1920 / 2) + wsize)
d = int((1080 / 2) + wsize)

with mss.mss() as sct:
    monitor = {"left": l, "top": w, "width": t-l, "height": d-w}

    loop_time = time()
    while True:
        # get an updated image of the game
        frame = np.array(sct.grab(monitor))[...,:3]

        visname = 'BurgerWare'

        frame = frame.astype(np.uint8)

        # Convert RGB color to HSV
        rgb_color = (191, 113, 73)  # Example: Green color in RGB
        hsv_color = cv.cvtColor(np.uint8([[rgb_color]]), cv.COLOR_RGB2HSV)[0][0]

        # detect players
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        lower = np.array([hsv_color[0] - 3, hsv_color[1] - 3, hsv_color[2] - 3])
        upper = np.array([hsv_color[0] + 3, hsv_color[1] + 3, hsv_color[2] + 3])
        mask = cv.inRange(hsv, lower, upper)
        sel_color = cv.bitwise_and(frame, frame, mask=mask)

        # Convert from HSV to Gray
        sel_color = cv.cvtColor(sel_color, cv.COLOR_HSV2BGR)
        sel_color = cv.cvtColor(sel_color, cv.COLOR_BGR2GRAY)

        ret, thresh = cv.threshold(sel_color, 50, 255, cv.THRESH_BINARY)

        # Find contours
        contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

        if len(contours) != 0:
            c = max(contours, key=cv.contourArea)
            x, y, w, h = cv.boundingRect(c)
            y2 = y + round(h / 2)
            x2 = x + round(w / 2)

            # Calculate the new mouse position
            numx = x2 - wsize
            numy = y2 - wsize

            pos = win32api.GetCursorPos()
            x = int(pos[0] + numx)
            y = int(pos[1] + numy)

            # Move the mouse
            win32api.SetCursorPos((x, y))

        # visual debug
        # cv.imshow(visname, frame)
        # cv.setWindowProperty(visname, cv.WND_PROP_TOPMOST, 1)

        # press 'q' with the output window focused to exit.
        # waits 1 ms every loop to process key presses
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break

    print('Done.')
