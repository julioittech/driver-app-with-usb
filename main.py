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

b_xposition = 0
b_yposition = 0
exit_flag = False

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
            .replace('K', 'k')
            .replace('i', 'l')
            .replace('î', 'l')
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
            .replace('5 t', '5t')
            .replace('T e', 'Te')
            .replace('D e', 'De')
            .replace('o l', 'ol')
            .replace('l s', 'ls')
            .replace('l v', 'lv')
            .replace('l m', 'm')
            .replace('ll', 'l')
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

def on_click(event):
    global exit_flag
    # print("button clicked!! Perfect!!!")
    exit_flag = True
    
def terminate_button():
    global b_xposition, b_yposition, exit_flag
    # print("ternaiate button", b_xposition, b_yposition)

    if b_xposition == 0 or b_yposition == 0:
        return
    root = tk.Tk()
    root.geometry(f"20x20+1+{b_yposition + 1}")  # A larger window to accommodate the shapes
    root.configure(background='#2865C9')  # Set window background color 
    root.overrideredirect(True)


    root.wm_attributes('-type', 'splash')
    root.attributes('-alpha', 1.0)
    root.attributes('-topmost', True)  

    root.bind("<Button-1>", on_click)

    # Close the window after 1000 ms
    root.after(2000, root.destroy)

    root.mainloop()
    if(exit_flag):
        exit()

def capture_screen():
    # Capture the entire screen
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def remove_top(image):
    return image, None  

def preprocess_left(image):    
    lower_bound = np.array([181, 51, 20])  # Specify lower bound
    upper_bound = np.array([255, 150, 60])  # Specify upper bound

    mask = cv2.inRange(image, lower_bound, upper_bound)

    # Scan the image from top to bottom to find the first non-zero pixel in the mask
    height, width = mask.shape
    for x in range(width):
        flag = False
        for y in range(int(height*0.5)):  
            if mask[y, x] > 0:  # Found a pixel within the color range
                flag = True
                break
        if not flag:
            cropped_image = image[:, x+3:]  # Remove the top part
            left_image = image[:, :x]
            return cropped_image, left_image
    
    return image, None  # Return the original image if the color isn't found

def cal_bposition(image):    
    global b_xposition, b_yposition
    b_xposition = 0
    b_yposition = 0
    lower_bound = np.array([40, 26, 177])  # Specify lower bound
    upper_bound = np.array([80, 66, 255])  # Specify upper bound

    mask = cv2.inRange(image, lower_bound, upper_bound)

    # Scan the image from top to bottom to find the first non-zero pixel in the mask
    height, width = mask.shape
    for y in range(int(height*0.7), height):
        red_flag = False
        for x in range(width):  
            if mask[y, x] > 0:  # Found a pixel within the color range
                b_xposition = x
                b_yposition = y
                return

def remove_left(image):    
    lower_bound = np.array([40, 26, 177])  # Specify lower bound
    upper_bound = np.array([80, 66, 255])  # Specify upper bound

    mask = cv2.inRange(image, lower_bound, upper_bound)

    # Scan the image from top to bottom to find the first non-zero pixel in the mask
    height, width = mask.shape
    white_flag = False
    for x in range(width):
        red_flag = False
        for y in range(height):  
            if mask[y, x] > 0:  # Found a pixel within the color range
                white_flag = True
                red_flag = True
                break
        if not red_flag and white_flag:
            cropped_image = image[:, x+3:]  # Remove the top part
            return cropped_image, x
    
    return image, None  # Return the original image if the color isn't found

def remove_right(image):    
    lower_bound = np.array([0, 0, 0])  # Specify lower bound
    upper_bound = np.array([200, 200, 200])  # Specify upper bound

    mask = cv2.inRange(image, lower_bound, upper_bound)

    # Scan the image from top to bottom to find the first non-zero pixel in the mask
    height, width = mask.shape

    for x in range(width -1, 0, -1):
        flag = False
        for y in range(height):  
            if (0 <= y < mask.shape[0]) and (0 <= x < mask.shape[1]):
                if mask[y, x] > 0:  # Found a pixel within the color range
                    flag = True
                    break
        if not flag:
            cropped_image = image[:, :x]  # Remove the top part
            return cropped_image, x

    return image, None  # Return the original image if the color isn't found

def remove_bottom(image):
    lower_bound = np.array([0, 0, 0])  # Specify lower bound
    upper_bound = np.array([200, 200, 200])  # Specify upper bound
    # Create a mask for the specific color range
    mask = cv2.inRange(image, lower_bound, upper_bound)

    # Scan the image from top to bottom to find the first non-zero pixel in the mask
    height, width = mask.shape
    
    for y in range(height-1, 0, -1):
        flag = False
        for x in range(width):  
            if (0 <= y < mask.shape[0]) and (0 <= x < mask.shape[1]):
                if mask[y, x] > 0:  # Found a pixel within the color range
                    flag = True
                    break
        if not flag:
            cropped_image = image[:y, :]  # Remove the top part
            return cropped_image, y
    
    return image, None  # Return the original image if the color isn't found

def preprocess_roi(roi):
    # Convert to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Apply adaptive thresholding
    thresholded = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    return thresholded

def find_text_location(image, search_string):
    height, width, _ = image.shape

    roi = image[0:int(height * 0.3), :]

    processed_roi = preprocess_roi(roi)

    # roi = cv2.adaptiveThreshold(roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    custom_config = r'--oem 3 --psm 6 -l ita+eng'
    # Apply OCR to the image
    results = pytesseract.image_to_data(processed_roi, output_type=pytesseract.Output.DICT, config=custom_config)
    # Loop through the results
    for i in range(len(results['text'])):
        if results['text'][i].strip() == search_string:
            # Get the bounding box coordinates
            x = results['left'][i]
            y = results['top'][i]
            w = results['width'][i]
            h = results['height'][i]

            # print(f"Found '{search_string}' at (x: {x}, y: {y}), width: {w}, height: {h}")
            if(search_string == "Domanda"): 
                cropped_image = image[y+h:, x:]  # Remove the top part
                return cropped_image, (x, y)
            else:
                cropped_image = image[:y, :x+w]  # Remove the top part
                return cropped_image, (x, y)
                
    return image, None
    
def main_process():
    text_find = False
    extracted_text = ""
    image = capture_screen()
    image, left_image = preprocess_left(image)

    if left_image is not None and left_image.size > 0:
        cal_bposition(left_image)
    # cv2.imwrite('left.png', image)
    image, domanda_location = find_text_location(image, "Domanda")
    # cv2.imwrite('1.png', image)
    if domanda_location != None:
        image, risposta_location = find_text_location(image, "Risposta")
        text_find = True
        # cv2.imwrite('2.png', image)

        if risposta_location != None:
            image, top_location = remove_top(image)
            # cv2.imwrite('3.png', image)

            image, bottom_location = remove_bottom(image)
            # cv2.imwrite('4.png', image)

            image, right_location = remove_right(image)
            # cv2.imwrite('5.png', image)

            image, left_location = remove_left(image)
            # cv2.imwrite('6.png', image)

    if text_find:
        # Use Tesseract to do OCR on the processed image
        custom_config = r'--oem 3 --psm 6'  # Experiment with different configs
        extracted_text = remove_single_quotes(pytesseract.image_to_string(image, lang='ita', config=custom_config).replace("\n", " ").rstrip())

        # test_text = pytesseract.image_to_string(image).replace("\n", " ").rstrip()
        # print(f'row string: {test_text}')

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
                break
        if not found:
            print(f'String "{extracted_text}" not found in the CSV.')
            draw_dot('black')

while(1):
    try:
        main_process()
        terminate_button()

    except KeyboardInterrupt:
        break
