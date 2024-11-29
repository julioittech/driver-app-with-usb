import cv2
import numpy as np
import sqlite3
from pytesseract import image_to_string, pytesseract
from fuzzywuzzy import fuzz, process
from PIL import Image
import threading
import queue
import os

pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
db_path = './quizzes.db'
LED_PIN = 20
GPIO_CHIP = 'gpiochip4'
frame_queue = queue.Queue()
result_queue = queue.Queue()

def toggle_gpio(pin, state):
    """Use os.system to toggle GPIO pin state."""
    os.system(f"gpioset {GPIO_CHIP} {pin}={state}")

def fetch_questions_and_answers():
    """Fetch all questions and answers from the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT Question, Answer FROM quizzes")
    data = cursor.fetchall()
    conn.close()
    return data

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

def ocr_processing_thread():
    quizzes_data = fetch_questions_and_answers()
    questions = [row[0] for row in quizzes_data]
    
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            try:
                processed_image = preprocess_image(frame)
                
                text_regions = find_text_regions(processed_image)
                
                extracted_text = extract_text_from_regions(processed_image, text_regions)
                
                if extracted_text:
                    extracted_text_clean = ' '.join(extracted_text.split())
                    
                    best_match, match_score = process.extractOne(
                        extracted_text_clean,
                        questions,
                        scorer=fuzz.partial_ratio
                    )
                    
                    if match_score > 80:  # Match threshold
                        answer = next((row[1] for row in quizzes_data if row[0] == best_match), None)
                        result = f"Question: {best_match}\nAnswer: {answer}\nMatch Score: {match_score}"
                        toggle_gpio(LED_PIN, 1)
                    else:
                        result = f"No match found. Best match score: {match_score}"
                        toggle_gpio(LED_PIN, 0)
                        
                    result_queue.put(result)
                    
            except Exception as e:
                result_queue.put(f"Error during processing: {str(e)}")
                toggle_gpio(LED_PIN, 0)

def capture_and_process():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    
    print("Processing frames in real-time. Press 'q' to quit.")
    
    threading.Thread(target=ocr_processing_thread, daemon=True).start()
    
    frame_counter = 0
    frame_skip = 5 
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break
            
            cv2.imshow("Camera Feed", frame)
            
            if frame_counter % frame_skip == 0:
                toggle_gpio(LED_PIN, 0)
                if frame_queue.qsize() < 2:
                    frame_queue.put(frame)
            
            if not result_queue.empty():
                print("\n" + result_queue.get() + "\n")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            frame_counter += 1
            
    finally:
        toggle_gpio(LED_PIN, 0)
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_and_process()
