import cv2 as cv
import numpy as np
import dxcam
import mouse
import math
import win32api

resw = 1920
resh = 1080
fps = 60

region_left = int(resw / 2 - 300)
region_top = int(resh / 2 - 300)
region_right = int(resw / 2 + 300)
region_bottom = int(resh / 2 + 300)

camera = dxcam.create(output_color="BGRA")
camera.start(target_fps=60, region=(region_left, region_top, region_right, region_bottom))

while True:
    # get an image from the video
    image = camera.get_latest_frame()
    frame = np.array(image)[..., :3]

    visname = 'BurgerWare'

    frame = frame.astype(np.uint8)

    # Convert RGB color to HSV
    rgb_color = (191, 113, 73)  # Example: Green color in RGB
    hsv_color = cv.cvtColor(np.uint8([[rgb_color]]), cv.COLOR_RGB2HSV)[0][0]

    # detect players
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    lower = np.array([hsv_color[0] - 5, hsv_color[1] - 20, hsv_color[2] - 20])
    upper = np.array([hsv_color[0] + 5, hsv_color[1] + 20, hsv_color[2] + 20])
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
        if w > 1 and h > 1:
            y2 = y + round(h / 2)
            x2 = x + round(w / 2)
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv.circle(frame, (x2, y2), radius=5, color=(0, 255, 0), thickness=-1)
            cv.line(frame, (round(resw / 2), round(resh / 2)), (x2, y2), color=(255, 0, 0), thickness=2)

            # Calculate the angle and distance to the target
            angle = math.atan2(y2 - resh / 2, x2 - resw / 2)
            distance = math.sqrt((y2 - resh / 2) ** 2 + (x2 - resw / 2) ** 2)

            # Adjust mouse position based on the calculated angle and distance
            sensitivity = 5  # You can adjust this value
            new_x = int(win32api.GetSystemMetrics(0) / 2 + sensitivity * distance * math.cos(angle))
            new_y = int(win32api.GetSystemMetrics(1) / 2 + sensitivity * distance * math.sin(angle))

            # Move the mouse
            mouse.move(new_x, new_y, absolute=True, duration=0.1)

    # visual debug
    cv.imshow(visname, frame)

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')
