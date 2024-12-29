import cv2
import numpy as np
import sqlite3
from picamera2 import Picamera2
from pytesseract import image_to_string, image_to_boxes, pytesseract
from fuzzywuzzy import process, fuzz
import RPi.GPIO as GPIO
import os
import time

# --- Configuration ---
pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
VIBRATION_PIN = 20
TEMP_THRESHOLD = 75  # Temperature threshold in Celsius
MOTION_THRESHOLD = 1000  # Default sensitivity for motion detection
STABILITY_DELAY = 2  # Wait time in seconds after motion stops

# Landmark Cache
landmark_cache = {'domanda_y': None, 'risposta_y': None}
landmark_detection_counter = 0

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(VIBRATION_PIN, GPIO.OUT)


# --- Load Database into Memory ---
def load_quiz_data():
    """Load questions and answers into memory for faster access."""
    conn = sqlite3.connect('/home/pi/Project/quizzes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Question, Answer FROM quizzes")
    quizzes_data = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in quizzes_data}


quizzes = load_quiz_data()


# --- Vibration Feedback ---
def vibrate(count):
    """Trigger vibration feedback based on count."""
    for _ in range(count):
        GPIO.output(VIBRATION_PIN, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(VIBRATION_PIN, GPIO.LOW)
        time.sleep(0.2)


# --- Temperature Monitoring ---
def monitor_temperature():
    """Check Raspberry Pi temperature."""
    temp = os.popen("vcgencmd measure_temp").readline()
    temp_value = float(temp.replace("temp=", "").replace("'C\n", ""))
    print(f"Temperature: {temp_value}°C")
    return temp_value


def adaptive_motion_threshold():
    """Adjust motion threshold based on CPU temperature."""
    temp = monitor_temperature()
    if temp > TEMP_THRESHOLD:
        print("High temperature detected! Lowering motion sensitivity.")
        return 500  # Lower sensitivity during high CPU load
    return MOTION_THRESHOLD


# --- Motion Detection ---
def detect_motion(frame1, frame2, threshold):
    """Detect significant motion between two frames."""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    
    diff = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    motion_score = np.sum(thresh) / 255  # Count white pixels
    
    print(f"Motion Score: {motion_score}, Threshold: {threshold}")
    return motion_score > threshold


# --- Dynamic ROI Detection ---
def find_dynamic_roi(frame):
    """Dynamically locate ROI based on 'Domanda' and 'Risposta'."""
    global landmark_cache, landmark_detection_counter
    
    if landmark_detection_counter % 5 == 0 or not landmark_cache['domanda_y'] or not landmark_cache['risposta_y']:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        boxes = image_to_boxes(gray, config='-l ita')
        
        domanda_y = None
        risposta_y = None
        
        height, width, _ = frame.shape
        
        for b in boxes.splitlines():
            b = b.split()
            word = b[0]
            x1, y1, x2, y2 = map(int, (b[1], b[2], b[3], b[4]))
            
            if 'Domanda' in word:
                domanda_y = height - y1
            if 'Risposta' in word:
                risposta_y = height - y2
        
        if domanda_y and risposta_y:
            landmark_cache['domanda_y'] = domanda_y
            landmark_cache['risposta_y'] = risposta_y
            print(f"Landmarks Updated: Domanda={domanda_y}, Risposta={risposta_y}")
    
    landmark_detection_counter += 1
    
    if landmark_cache['domanda_y'] and landmark_cache['risposta_y']:
        return frame[landmark_cache['risposta_y']:landmark_cache['domanda_y'], 100:width-100]
    else:
        print("Fallback ROI used")
        return frame[120:220, 200:1100]


# --- ROI Validation ---
def validate_roi(roi):
    """Quick check to ensure the ROI contains meaningful text."""
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    non_empty_pixels = cv2.countNonZero(thresh)
    total_pixels = roi.shape[0] * roi.shape[1]
    density = non_empty_pixels / total_pixels
    
    print(f"ROI Text Density: {density}")
    return density > 0.05


# --- Image Preprocessing ---
def preprocess_image(frame):
    """Enhance image quality for better OCR results."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, 50, 150)
    resized = cv2.resize(edges, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    cv2.imshow("Preprocessed Image", resized)
    cv2.waitKey(1)
    return resized


# --- OCR Text Extraction ---
def extract_text(image):
    """Extract text using OCR with optimized configuration."""
    config = '--oem 3 --psm 6 -l ita'
    text = image_to_string(image, config=config).strip()
    print(f"OCR Extracted Text: {text}")
    return text


# --- Optimized Text Matching ---
def match_question(extracted_text):
    """Match OCR text with database questions."""
    extracted_text = ' '.join(extracted_text.split())
    matches = process.extract(extracted_text, quizzes.keys(), limit=5, scorer=fuzz.token_sort_ratio)
    
    valid_matches = [(q, s) for q, s in matches if s > 80]
    if valid_matches:
        return max(valid_matches, key=lambda x: x[1])
    return None, 0


# --- Main Loop ---
def main():
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={'size': (1920, 1080)}))
    picam2.start()
    prev_frame = picam2.capture_array()
    
    try:
        while True:
            frame = picam2.capture_array()
            if not detect_motion(prev_frame, frame, adaptive_motion_threshold()):
                roi = find_dynamic_roi(frame)
                if validate_roi(roi):
                    text = extract_text(preprocess_image(roi))
                    match, score = match_question(text)
                    if match:
                        vibrate(2 if 'V' in match else 1)
            prev_frame = frame
    finally:
        picam2.stop()
        GPIO.cleanup()
        cv2.destroyAllWindows()


# --- Entry Point ---
if __name__ == "__main__":
    vibrate(3)
    main()
