import cv2
import numpy as np
import sqlite3
from picamera2 import Picamera2, Preview
from pytesseract import image_to_string, pytesseract
from fuzzywuzzy import fuzz, process
from PIL import Image
import queue
import RPi.GPIO as GPIO
import time

# Tesseract Configuration
pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

# GPIO Setup
VIBRATION_PIN = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(VIBRATION_PIN, GPIO.OUT)

# Load Database
conn = sqlite3.connect('./quizzes.db')
cursor = conn.cursor()
cursor.execute("SELECT Question, Answer FROM quizzes")
quizzes_data = cursor.fetchall()
conn.close()
questions = [row[0] for row in quizzes_data]
previous_question = ''


# --- Vibration Feedback ---
def vibrate(count):
    """Trigger vibration feedback based on count."""
    for _ in range(count):
        GPIO.output(VIBRATION_PIN, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(VIBRATION_PIN, GPIO.LOW)
        time.sleep(0.2)


# --- Image Preprocessing ---
def preprocess_image(frame):
    """Enhance image quality for better OCR results."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Reduce noise with GaussianBlur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply CLAHE for local contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blurred)
    
    # Adaptive thresholding for binarization
    binary = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    return binary


# --- Text Region Detection ---
def find_text_regions(image):
    """Find regions containing text using contour detection."""
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = 500  # Increase to filter out noise
    text_regions = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            x, y, w, h = cv2.boundingRect(contour)
            text_regions.append((x, y, w, h))
    
    return text_regions


# --- Extract Text from Regions ---
def extract_text_from_regions(image, regions):
    """Extract text from detected regions using Tesseract."""
    extracted_texts = []
    
    for x, y, w, h in regions:
        padding = 15
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(image.shape[1], x + w + padding)
        y2 = min(image.shape[0], y + h + padding)
        
        region = image[y1:y2, x1:x2]
        pil_region = Image.fromarray(region)
        text = image_to_string(
            pil_region, lang='ita', config='--psm 6 --oem 3'
        ).strip()
        if text:
            extracted_texts.append(text)
    
    return ' '.join(extracted_texts)


# --- OCR Processing ---
def ocr_processing_thread(frame):
    """Process frame for OCR and match text with database."""
    global previous_question
    try:
        processed_image = preprocess_image(frame)
        text_regions = find_text_regions(processed_image)
        extracted_text = extract_text_from_regions(processed_image, text_regions)
        print(f"Extracted Text: {extracted_text}")
        
        if extracted_text:
            extracted_text_clean = ' '.join(extracted_text.split())
            
            # Perform fuzzy matching
            best_match, match_score = process.extractOne(
                extracted_text_clean, questions, scorer=fuzz.token_sort_ratio
            )
            
            if match_score > 85:  # Adjusted threshold for better accuracy
                answer = next((row[1] for row in quizzes_data if row[0] == best_match), None)
                if best_match == previous_question:
                    print("Duplicate question detected. Skipping vibration.")
                    return
                
                # Update previous question and trigger vibration
                previous_question = best_match
                vibrate(2 if answer == 'V' else 1)
                
                print(f"Question: {best_match}\nAnswer: {answer}\nMatch Score: {match_score}")
            else:
                print(f"No valid match found. Best match score: {match_score}")
    
    except Exception as e:
        print(f"Error during processing: {str(e)}")


# --- Capture and Process ---
def capture_and_process():
    """Capture frames and process them for OCR."""
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={'size': (1920, 1080)}))
    picam2.start()
    
    try:
        while True:
            frame = picam2.capture_array()
            frame = cv2.resize(frame, (1280, 720))  # Downscale for faster processing
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            cv2.imshow("Camera Feed", frame)
            ocr_processing_thread(frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
        GPIO.cleanup()


# --- Main Execution ---
if __name__ == "__main__":
    vibrate(3)  # Startup vibration
    capture_and_process()
