import cv2
import numpy as np
import pyautogui
import time
import pytesseract

def capture_screen():
    # Capture the entire screen
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def remove_top(image):
    return image, None  

def remove_left(image):    
    return image, None  

def remove_right(image):    
    lower_bound = np.array([0, 0, 0])  # Specify lower bound
    upper_bound = np.array([200, 200, 200])  # Specify upper bound

    mask = cv2.inRange(image, lower_bound, upper_bound)

    # Scan the image from top to bottom to find the first non-zero pixel in the mask
    height, width = mask.shape
    print("remove_right:", height, width, mask.shape[0], mask.shape[1])
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
    
    print("Color not found in the specified area.")
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
    
    print("Color not found in the specified area.")
    return image, None  # Return the original image if the color isn't found

def find_text_location(image, search_string):
    # Apply OCR to the image
    results = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    # Loop through the results
    for i in range(len(results['text'])):
        if results['text'][i].strip() == search_string:
            # Get the bounding box coordinates
            x = results['left'][i]
            y = results['top'][i]
            w = results['width'][i]
            h = results['height'][i]

            print(f"Found '{search_string}' at (x: {x}, y: {y}), width: {w}, height: {h}")
            
            if search_string == "Domanda":
                cropped_image = image[y+h:, x:]  # Remove the top part
                return cropped_image, (x, y)
            else:
                cropped_image = image[:y, :x+w]  # Remove the top part
                return cropped_image, (x, y)


    return image, None

def main():
    # Delay to allow for setup
    print("Please switch to the window you want to capture...")
    time.sleep(2)

    # Capture the screen
    image = capture_screen()

    # Find the color and crop the image
    domanda_remove, domanda_location = find_text_location(image, "Domanda")
    cv2.imwrite('domanda_image.png', domanda_remove)
    print("domanda_location", domanda_location)
    if domanda_location != None:
        risposta_remove, risposta_location = find_text_location(domanda_remove, "Risposta")
        cv2.imwrite('risposta_remove.png', risposta_remove)
        print("risposta_location", risposta_location)

        if risposta_location != None:
            top_remove, top_location = remove_top(risposta_remove)
            cv2.imwrite('top_remove.png', top_remove)
            print("top_location", top_location)

            bottom_remove, bottom_location = remove_bottom(top_remove)
            cv2.imwrite('bottom_remove.png', bottom_remove)
            print("bottom_location", bottom_location)

            right_remove, right_location = remove_right(bottom_remove)
            cv2.imwrite('right_remove.png', right_remove)
            print("right_location", right_location)

            left_remove, left_location = remove_left(right_remove)
            cv2.imwrite('left_remove.png', left_remove)
            print("left_location", left_location)

if __name__ == "__main__":
    main()