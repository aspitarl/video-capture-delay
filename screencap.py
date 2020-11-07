import numpy as np
from PIL import ImageGrab
import win32gui
import cv2
import time

#https://pysource.com/2019/11/01/capture-screen-from-a-window-python-plays-tetris-p-1/

# Detect the window with Tetris game
windows_list = []
toplist = []
def enum_win(hwnd, result):
    win_text = win32gui.GetWindowText(hwnd)
    windows_list.append((hwnd, win_text))
win32gui.EnumWindows(enum_win, toplist)


# Game handle
game_hwnd = 0
for (hwnd, win_text) in windows_list:
    if "Camera" in win_text:
        game_hwnd = hwnd

position = win32gui.GetWindowRect(game_hwnd)

start_time = time.time()

DELAY_SECONDS = 2

frames = []
times = []


#https://stackoverflow.com/questions/32237862/find-the-closest-date-to-a-given-date
def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))


def nearest_ind(items, pivot):
    time_diff = np.abs([date - pivot for date in items])
    return time_diff.argmin(0)

while True:
    
    # Take screenshot
    screenshot = ImageGrab.grab(position)
    screenshot = np.array(screenshot)
    # print(screenshot.shape)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    screenshot_time = time.time()

    frames.append(screenshot)
    times.append(screenshot_time)

    target_time = screenshot_time - DELAY_SECONDS

    target_time_idx = nearest_ind(times, target_time )

    # print(target_time_idx)

    display_screnshot = frames[target_time_idx]

    frames = frames[target_time_idx:]
    times = times[target_time_idx:]

    cv2.imshow("frame", display_screnshot)


    if cv2.waitKey(1) == 27: 
        break  # esc to quit

cv2.destroyAllWindows()