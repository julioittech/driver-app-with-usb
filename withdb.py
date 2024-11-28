import cv2
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

def ocr_processing_thread():
    """Thread to process OCR and match text."""
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

                    if match_score > 80:  # Match threshold
                        answer = next((row[1] for row in quizzes_data if row[0] == best_match), None)
                        result = f"Question: {best_match}\nAnswer: {answer} (Score: {match_score})"
                        
                        toggle_gpio(LED_PIN, 1)
                    else:
                        result = "The scanned text did not match any question in the database."
                        toggle_gpio(LED_PIN, 0)  # Turn off LED if no match

                    result_queue.put(result)
            except Exception as e:
                result_queue.put(f"Error during OCR or processing: {str(e)}")
                toggle_gpio(LED_PIN, 0)  # Ensure LED is off in case of error

def capture_and_process():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

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

            #cv2.imshow("Camera", frame)

            if frame_counter % frame_skip == 0:
                toggle_gpio(LED_PIN, 0)
                if frame_queue.qsize() < 2:  
                    frame_queue.put(frame)

            if not result_queue.empty():
                print(result_queue.get())

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            frame_counter += 1

    finally:
        toggle_gpio(LED_PIN, 0)
        cap.release()
        cv2.destroyAllWindows()

capture_and_process()