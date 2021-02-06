from selenium import webdriver
import time
import pandas as pd
import numpy as np

browser = webdriver.Chrome('C:/Users/armar/Desktop/chromedriver.exe')

def google_search(obj_search):
    #Private function created to search in google for "obj_search"
    browser.get('https://google.com')
    search_bar = browser.find_element_by_xpath('//*[@id="tsf"]/div[2]/div[1]/div[1]/div/div[2]/input')
    search_bar.send_keys(str(obj_search)) #converts obj_search to string
    search_key = browser.find_element_by_xpath('//*[@id="tsf"]/div[2]/div[1]/div[3]/center/input[1]')
    search_key.submit()
    cords = browser.find_elements_by_class_name('Z0LcW XcVN5d')
    return cords

searcher = google_search('pilares latitude longitude rio de janeiro')