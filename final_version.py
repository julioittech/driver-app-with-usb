import time
time.sleep(10)

import cv2
import numpy as np
import sqlite3
from picamera2 import Picamera2, Preview
from pytesseract import image_to_string, pytesseract
from fuzzywuzzy import fuzz, process
from PIL import Image
import queue
import RPi.GPIO as GPIO


pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

frame_queue = queue.Queue()
result_queue = queue.Queue()
GPIO.cleanup()
GPIO.setwarnings(False)  # Ignore warnings
GPIO.setmode(GPIO.BCM)

VIBRATION_PIN = 23
GPIO.setup(VIBRATION_PIN, GPIO.OUT)

conn = sqlite3.connect('/home/pi/Project/quizzes.db')
cursor = conn.cursor()
cursor.execute("SELECT Question, Answer FROM quizzes")
quizzes_data = cursor.fetchall()
conn.close()
questions = [row[0] for row in quizzes_data]
previous_question = ''

def vibrate(count):
    for _ in range(count):
        print("Started vibration")
        GPIO.output(VIBRATION_PIN, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(VIBRATION_PIN, GPIO.LOW)
        time.sleep(0.2)

def preprocess_image(frame):
    """Enhance image quality for better OCR results."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    denoised = cv2.fastNlMeansDenoising(enhanced)
    
    binary = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )
    
    kernel = np.ones((1,1), np.uint8)
    dilated = cv2.dilate(binary, kernel, iterations=1)
    
    return dilated

def find_text_regions(image):
    """Find regions containing text using contour detection."""
    contours, _ = cv2.findContours(
        image, 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    min_area = 100
    text_regions = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            x, y, w, h = cv2.boundingRect(contour)
            text_regions.append((x, y, w, h))
    
    return text_regions

def extract_text_from_regions(image, regions):
    extracted_texts = []
    
    for x, y, w, h in regions:
        padding = 10
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(image.shape[1], x + w + padding)
        y2 = min(image.shape[0], y + h + padding)
        
        region = image[y1:y2, x1:x2]
        
        pil_region = Image.fromarray(region)
        text = image_to_string(pil_region, lang='ita').strip()
        if text:
            extracted_texts.append(text)
    
    return ' '.join(extracted_texts)

def ocr_processing_thread(frame):
    global previous_question
    try:
        processed_image = preprocess_image(frame)
        text_regions = find_text_regions(processed_image)
        extracted_text = extract_text_from_regions(processed_image, text_regions)
        print(extracted_text)
        if extracted_text:
            extracted_text_clean = ' '.join(extracted_text.split())
                    
            best_match, match_score = process.extractOne(
                extracted_text_clean,
                questions,
                scorer=fuzz.partial_ratio
            )
                    
            if match_score > 80 and match_score < 100:  # Match threshold
                answer = next((row[1] for row in quizzes_data if row[0] == best_match), None)
                result = f"Question: {best_match}\nAnswer: {answer}\nMatch Score: {match_score}"
                if best_match == previous_question:
                    print('Already rings')
                    return
                previous_question = best_match
                if answer == 'V':
                    vibrate(2)
                else:
                    vibrate(1)
            else:
                result = f"No match found. Best match score: {match_score}"
                        
            print(result)
                    
    except Exception as e:
        print(f"Error during processing: {str(e)}")

def capture_and_process():
    picam2 = Picamera2()

    picam2.configure(picam2.create_preview_configuration(main={'size': (3840, 2160)}))
    picam2.set_controls({'AfMode':2,'AfTrigger':0,'AeEnable': 1})
   
   
    # picam2.start_preview(Preview.QTGL)s
    
    # threading.Thread(target=ocr_processing_thread, daemon=True).start()
    picam2.start()
    
    try:
        while True:
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            cv2.imshow("Camera Feed", frame)
            
            ocr_processing_thread(frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    finally:
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    vibrate(3)
    capture_and_process()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    

