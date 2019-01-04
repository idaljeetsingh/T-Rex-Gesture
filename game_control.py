"""
    Title: T-Rex Gesture
    File Name: game_control.py
    Author: Daljeet Singh Chhabra
    Language: Python
    Date Created: 04-01-2019
    Date Modified: 04-01-2019
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

status = 0
driver = None


def control(k):
    global status
    global driver

    if status is 0 and k is 5:
        status = 1
        print("Launching Game!!!")
        driver = webdriver.Chrome()
        driver.get('chrome://dino')
    if status is 1:
        if k is 0:                                      # To stop the game
            print("Stopping the game!!")
            driver.stop_client()
            driver.quit()
        if k is 1:                                      # To make the DINO jump
            print("JUMP")
            body = driver.find_element_by_id("t")
            body.send_keys(Keys.SPACE)
        if k is 2:                                      # To make the DINO crouch
            print("Crouch")
            body = driver.find_element_by_id("t")
            body.send_keys(Keys.ARROW_DOWN)
        if k is 3:                                      # To reload the game
            print("Reloading")
            driver.get('chrome://dino')
