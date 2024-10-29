import os
import pyautogui
from PIL import Image, ImageDraw
import csv
import cv2
import pytesseract
import time
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np

os.environ['TESSDATA_PREFIX'] = os.path.dirname(os.path.abspath(__file__))

s_width, s_height = pyautogui.size()
region = (int(s_width * 0.296), int(s_height * 0.19), int(s_width * 0.56),  int(s_height * 0.125))
# region = (350, 250, 740, 300) 

def remove_single_quotes(input_string):
    return (input_string
            .replace("() ", "")
            .replace('  ', ' ')
            .replace('- ', '')
            .replace('-', '')
            .replace('.', '')
            .replace(', ', ',')
            .replace("’i", '')
            .replace("'i", "")
            .replace("‘i", "")
            .replace("E ", 'E')
            .replace("È", 'E')
            .replace("’ ", '')
            .replace("’", '')
            .replace("' ", "")
            .replace("'", "")
            .replace("‘ ", "")
            .replace("‘", "")
            .replace('“', '"')
            .replace('N', 'V')
            .replace('i', 'l')
            .replace('f', 'l')
            .replace('1', 'l')
            .replace('I', 'l')
            .replace('[', 'l')
            .replace(']', 'l')
            .replace('{', 'l')
            .replace('(', 'l')
            .replace('}', 'l')
            .replace(')', 'l')
            .replace('!', 'l')
            .replace('|', 'l')
            .replace('U', 'l')
            .replace('L', 'l')
            .replace('é', 'e')
            .replace('è', 'e')
            .replace('j', 'o')
            .replace('à', 'o')
            .replace('a', 'o')
            .replace('ù', 'o')
	        .replace('&', 'o')
            .replace('€', 'o')
            .replace('d', 'o')
            .replace('ò', 'o')
            .replace('0', 'o')
            .replace('rl', 'n')
            .replace('nl', 'n')
            .replace('ul', 'u')
            .replace('T e', 'Te')
            .replace('ll ', 'l ')
            .replace('o l', 'ol')
            .replace('l s', 'ls')
            .replace('l v', 'lv')
            .replace('l m', 'm')
            .replace(' } ', ' '))

def draw_dot(color):
    # Create the main window
    root = tk.Tk()
    root.geometry("6x6+800+500")  # A larger window to accommodate the shapes
    root.configure(background='white')  # Set window background color to white
    root.overrideredirect(True)

    # Create a canvas to draw; here bg='white' matches the root background
    canvas = tk.Canvas(root, width=50, height=50, bg='white', highlightthickness=0, borderwidth=0)
    canvas.pack()

    # Set the diameter for the shapes
    diameter = 5

    # Determine shape to draw based on color
    if color == 'red':
        # Draw a circle with a 5-pixel diameter
        canvas.create_oval(0, 0, 0 + diameter, 0 + diameter, fill=color, outline=color)
    elif color == 'green':
        # Draw a triangle with a height based around a 5-pixel dimension
        x1, y1 = 2.5, 0  # Top vertex
        x2, y2 = 0, 5  # Bottom left vertex
        x3, y3 = 5, 5  # Bottom right vertex
        canvas.create_polygon(x1, y1, x2, y2, x3, y3, fill=color, outline=color)
    else:
        # Draw a rectangle with a width and height of 5 pixels
        canvas.create_rectangle(0, 0, 0 + diameter, 0 + diameter, fill=color, outline=color)

    # Close the window after 1000 ms
    root.after(1000, root.destroy)

    root.mainloop()
    

def main_process():
    
    screenshot = pyautogui.screenshot(region=region)

    # Convert the screenshot to an OpenCV format
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Preprocessing for Tesseract
    gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Use Tesseract to do OCR on the processed image
    custom_config = r'--oem 3 --psm 6'  # Experiment with different configs
    extracted_text = remove_single_quotes(pytesseract.image_to_string(binary, lang='ita', config=custom_config).replace("\n", " ").rstrip())

    # test_text = pytesseract.image_to_string(screenshot).replace("\n", " ").rstrip()
    # print(f'row string: {test_text}')
    screenshot.save("screenshot.png")

    filename = 'quizzes.csv'
    # filename = '~/Documents/driving/quizzes.csv'
    with open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        
        header = next(csvreader)
        
        found = False
        for row in csvreader:
            cleaned_row = [remove_single_quotes(cell) for cell in row]
            if(extracted_text == ""):
                continue
	    
            if any(extracted_text in cell for cell in cleaned_row):
                print(f'Found in row: {row}')
                found = True
                if(row[1] == 'V'):
                    draw_dot('green')
                else:
                    draw_dot('red')
        if not found:
            print(f'String "{extracted_text}" not found in the CSV.')
            draw_dot('black')

while(1):
    try:
        main_process()
        time.sleep(1)

    except KeyboardInterrupt:
        break
