from picamera2 import Picamera2
import cv2
import sqlite3
from pytesseract import image_to_string, pytesseract
from fuzzywuzzy import fuzz, process
from PIL import Image
import threading
import queue
import os
import time
import RPi.GPIO as GPIO

pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
db_path = './quizzes.db'
VIBRATION_PIN = 20  
frame_queue = queue.Queue()
result_queue = queue.Queue()
last_matched_text = None  
GPIO.setmode(GPIO.BCM)
GPIO.setup(VIBRATION_PIN, GPIO.OUT)

def vibrate_pattern(pattern):
    """
    Pattern: 'single' for match found, 'double' for no match
    """
    try:
        if pattern == 'single':
            GPIO.output(VIBRATION_PIN, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(VIBRATION_PIN, GPIO.LOW)
        elif pattern == 'double':
            for _ in range(2):
                GPIO.output(VIBRATION_PIN, GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(VIBRATION_PIN, GPIO.LOW)
                time.sleep(0.2)
    except Exception as e:
        print(f"Vibration error: {e}")
    finally:
        GPIO.output(VIBRATION_PIN, GPIO.LOW)

def fetch_questions_and_answers():
    """Fetch all questions and answers from the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT Question, Answer FROM quizzes")
    data = cursor.fetchall()
    conn.close()
    return data

def ocr_processing_thread():
    """Thread to process OCR and match text."""
    global last_matched_text
    quizzes_data = fetch_questions_and_answers()
    questions = [row[0] for row in quizzes_data]
    
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            try:
                captured_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(captured_image)
                extracted_text = image_to_string(pil_image, lang='ita').strip()
                extracted_text_clean = ' '.join(extracted_text.split())
                
                if extracted_text_clean:  
                    best_match, match_score = process.extractOne(
                        extracted_text_clean, questions, scorer=fuzz.partial_ratio
                    )
                    if match_score > 80:  
                        answer = next((row[1] for row in quizzes_data if row[0] == best_match), None)
                        result = f"Question: {best_match}\nAnswer: {answer} (Score: {match_score})"
                        
                        # Only vibrate if this is not the same as the last matched text
                        if best_match != last_matched_text:
                            vibrate_pattern('single')
                            last_matched_text = best_match
                    else:
                        result = "The scanned text did not match any question in the database."
                        vibrate_pattern('double')
                        last_matched_text = None
                    result_queue.put(result)
            except Exception as e:
                result_queue.put(f"Error during OCR or processing: {str(e)}")
                last_matched_text = None

def capture_and_process():
    # Initialize PiCamera2
    picam2 = Picamera2()
    config = picam2.create_preview_configuration()
    picam2.configure(config)
    picam2.start()
    time.sleep(2) 
    
    print("Processing frames in real-time. Press 'q' to quit.")
    threading.Thread(target=ocr_processing_thread, daemon=True).start()
    
    frame_counter = 0
    frame_skip = 5 
    
    try:
        while True:
            frame = picam2.capture_array()
            
            if frame_counter % frame_skip == 0:
                if frame_queue.qsize() < 2:  
                    frame_queue.put(frame)
                    
            if not result_queue.empty():
                print(result_queue.get())
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            frame_counter += 1
            
    except Exception as e:
        print(f"Error in capture process: {e}")
        
    finally:
        GPIO.cleanup()  
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        capture_and_process()
    except KeyboardInterrupt:
        GPIO.cleanup()  # 
