import cv2
import numpy as np
import pyautogui
import time

def capture_screen():
    # Capture the entire screen
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def remove_header(image):
    lower_bound = np.array([181, 51, 20])  # Specify lower bound
    upper_bound = np.array([255, 150, 60])  # Specify upper bound
    # Create a mask for the specific color range
    mask = cv2.inRange(image, lower_bound, upper_bound)

    # Scan the image from top to bottom to find the first non-zero pixel in the mask
    height, width = mask.shape
    for y in range(height):
        for x in range(int(width * 0.1)):  # Check only the first 10% of the width
            if mask[y, x] > 0:  # Found a pixel within the color range
                print(f"Found color at (x: {x}, y: {y})")
                # Crop the image from this point downwards
                found_color = image[y, x]  # This is in BGR format

                print(f"Color found (RGB): {found_color}")

                cropped_image = image[y:, :]  # Remove the top part
                return cropped_image, (x, y)
    
    print("Color not found in the specified area.")
    return image, None  # Return the original image if the color isn't found

def remove_left(image):    
    lower_bound = np.array([200, 200, 200])  # Specify lower bound
    upper_bound = np.array([255, 255, 255])  # Specify upper bound

    mask = cv2.inRange(image, lower_bound, upper_bound)

    # Scan the image from top to bottom to find the first non-zero pixel in the mask
    height, width = mask.shape
    for x in range(width):
        for y in range(int(height * 0.01)):  # Check only the first 1% of the height
            if mask[y, x] > 0:  # Found a pixel within the color range
                print(f"Found color at (x: {x}, y: {y})")
                # Crop the image from this point downwards
                found_color = image[y, x]  # This is in BGR format

                print(f"Color found (RGB): {found_color}")

                cropped_image = image[ :, x:]  # Remove the top part
                return cropped_image, (x, y)
    return image  # Return the original image if not wide enough

def main():
    # Delay to allow for setup
    print("Please switch to the window you want to capture...")
    time.sleep(2)

    # Capture the screen
    image = capture_screen()

    # Find the color and crop the image
    header_remove, header_location = remove_header(image)
    cv2.imwrite('cropped_image.png', header_remove)

    print("location", header_location)

    sidebar_remove, sidebar_location = remove_left(header_remove)
    print("position", sidebar_location)
    cv2.imwrite('sidebar_remove.png', sidebar_remove)  # Save cropped image

if __name__ == "__main__":
    while(1):
        main()