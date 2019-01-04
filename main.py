"""
    Title: T-Rex Gesture
    File Name: main.py
    Author: Daljeet Singh Chhabra
    Language: Python
    Date Created: 04-01-2019
    Date Modified: 04-01-2019
"""

import game_control
import cv2
import numpy as np
import math
from urllib.request import urlopen


url = 'http://192.168.43.72:8080/shot.jpg'              # enter URL of your device from IP WebCam


def main():
    # cap = cv2.VideoCapture(0)                         # For Web Cam

    global url
    while True:
        try:
            image_response = urlopen(url)
            imgNp = np.array(bytearray(image_response.read()), dtype=np.uint8)
            frame = cv2.imdecode(imgNp, -1)

            # check, frame = cap.read()                 # use these lines in case of WebCam only
            # frame = cv2.flip(frame, 1)
            kernel = np.ones((3, 3), np.uint8)

            # Defining Region Of Interest towards right side

            roi = frame[100:300, 100:300]
            cv2.rectangle(frame, (100, 100), (300, 300), (0, 255, 0), 0)

            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            # Defining range of skin color in HSV
            lower_skin = np.array([0, 10, 60], dtype=np.uint8)
            upper_skin = np.array([20, 150, 255], dtype=np.uint8)

            # extract skin color image
            mask = cv2.inRange(hsv, lower_skin, upper_skin)

            # extrapolate the hand to fill dark spots within
            mask = cv2.dilate(mask, kernel, iterations=4)

            # blur the image
            mask = cv2.GaussianBlur(mask, (5, 5), 100)

            # find contours
            _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # find contour of max area(hand)
            cnt = max(contours, key=lambda x: cv2.contourArea(x))

            # approx the contour a little
            epsilon = 0.0005 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            # make convex hull around hand
            hull = cv2.convexHull(cnt)

            # define area of hull and area of hand
            areahull = cv2.contourArea(hull)
            areacnt = cv2.contourArea(cnt)

            # find the percentage of area not covered by hand in convex hull
            arearatio = ((areahull - areacnt) / areacnt) * 100

            # find the defects in convex hull with respect to hand
            hull = cv2.convexHull(approx, returnPoints=False)
            defects = cv2.convexityDefects(approx, hull)

            # nod = no. of defects
            nod = 0

            # code for finding no. of defects due to fingers
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(approx[s][0])
                end = tuple(approx[e][0])
                far = tuple(approx[f][0])
                # pt = (100, 180)

                # finding length of all sides of triangle
                a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                s = (a + b + c) / 2
                ar = math.sqrt(s * (s - a) * (s - b) * (s - c))

                # distance between point and convex hull
                d = (2 * ar) / a

                # applying cosine rule here to find the angle
                angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

                # ignore angles > 90 and ignore points very close to convex hull(they generally come due to noise)
                if angle <= 90 and d > 30:
                    nod += 1
                    cv2.circle(roi, far, 3, [255, 0, 0], -1)

                # draw lines around hand
                cv2.line(roi, start, end, [0, 255, 0], 2)

            nod += 1                                          # Total fingers = Total defects + 1

            # print corresponding gestures which are in their ranges
            screen_font = cv2.FONT_HERSHEY_DUPLEX
            if nod is 1:
                if areacnt < 2000:                              # Empty ROI
                    game_control.control(0)
                    game_control.status = 0
                    cv2.putText(frame, 'Put hand in the box', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                else:
                    if arearatio < 12:
                        cv2.putText(frame, 'N.A', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)

                    elif arearatio < 17.5:                      # Thumbs Up Gesture
                        if game_control.status is 1:
                            game_control.control(1)
                            cv2.putText(frame, 'JUMP', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                        else:
                            cv2.putText(frame, 'Start Game first...', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)

                    else:                                       # 1 Finger Detected
                        if game_control.status is 1:
                            game_control.control(1)
                            cv2.putText(frame, 'JUMP', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                        else:
                            cv2.putText(frame, 'Start Game first...', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            elif nod is 2:                                        # 2 Fingers Detected
                if game_control.status is 1:
                    game_control.control(2)
                    cv2.putText(frame, 'Crouch', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                else:
                    cv2.putText(frame, 'Start Game first...', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            elif nod is 3:
                if arearatio < 27:                              # 3 Fingers Detected
                    if game_control.status is 1:
                        game_control.control(3)
                        cv2.putText(frame, 'RELOAD', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    else:
                        cv2.putText(frame, 'Start Game first...', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            # For additional functionality...
            # 4 Fingers Detected here...
            elif nod is 4:
                if game_control.status is 1:
                    game_control.control(4)
                    cv2.putText(frame, ' ', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                else:
                    cv2.putText(frame, 'Start Game first...', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            elif nod is 5:
                if game_control.status is 1:
                    cv2.putText(frame, 'Already Running...', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                else:
                    game_control.control(5)
                    cv2.putText(frame, 'Starting Game', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            elif nod == 6:
                cv2.putText(frame, 'reposition', (0, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            else:
                cv2.putText(frame, 'reposition', (10, 50), screen_font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            # show the windows
            cv2.imshow('mask', mask)
            cv2.imshow('frame', frame)

            key = cv2.waitKey(1)
            if key is 27:       # ESC stops the applet
                game_control.control(0)
                break
        except:
            pass
    cv2.destroyAllWindows()
    # cap.release()


if __name__ == '__main__':
    main()
