import os
import tkinter as tk
import pyautogui
import numpy as np
import cv2
import pytesseract
import time

os.environ['TESSDATA_PREFIX'] = os.path.dirname(os.path.abspath(__file__))
# Define the area for capturing clicks
click_area_x1, click_area_y1 = 100, 100  # Top-left corner
click_area_x2, click_area_y2 = 200, 200  # Bottom-right corner
region = (click_area_x1, click_area_y1, click_area_x2 - click_area_x1, click_area_y2 - click_area_y1)

def remove_single_quotes(text):
    return text.replace("'", "")  # Example implementation

def main_process():
    # Taking a screenshot in the specified region
    screenshot = pyautogui.screenshot()

    # Convert the screenshot to OpenCV format
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Preprocessing for Tesseract
    gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Use Tesseract to do OCR on the processed image
    custom_config = r'--oem 3 --psm 6'  # Experiment with different configs
    extracted_text = remove_single_quotes(pytesseract.image_to_string(binary, lang='ita', config=custom_config).replace("\n", " ").rstrip())
    
    print("Extracted Text:", extracted_text)  # Print the extracted text

# Function to handle mouse clicks on the Tkinter window
def on_click(event):
    x, y = event.x, event.y

    # Check if click is within the defined area
    if click_area_x1 <= x <= click_area_x2 and click_area_y1 <= y <= click_area_y2:
        print("Click detected in specified area! Terminating the script.")
        root.quit()  # Terminate the Tkinter main loop

root = tk.Tk()
root.title("Click to Terminate Script")
root.geometry("400x400")  # Window size

# Label for visual feedback
label = tk.Label(root, text="Click within the area (100, 100) to (200, 200) to exit.")
label.pack(pady=20)

# Bind the click event to the window
root.bind("<Button-1>", on_click)

# Start the main loop
try:
    while True:
        main_process()
        root.update()  # Update Tkinter window
        time.sleep(1)

except KeyboardInterrupt:
    pass
finally:
    root.quit()  # Ensure Tkinter is closed properly