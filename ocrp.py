import cv2
import pandas as pd
from pytesseract import image_to_string, pytesseract
from fuzzywuzzy import fuzz, process
from PIL import Image

pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

# Load the quizzes DataFrame
csv_path = './quizzes.csv'
quizzes_df = pd.read_csv(csv_path)

def capture_and_process():
    # Open the camera
    cap = cv2.VideoCapture(0)  # Use 0 for the default camera

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    print("Press 'c' to capture the image and perform OCR or 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        cv2.imshow("Camera", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('c'):  # Capture the image
            captured_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(captured_image)

            try:
                extracted_text = image_to_string(pil_image, lang='ita').strip()
                extracted_text_clean = ' '.join(extracted_text.split())

                questions = quizzes_df['Question'].tolist()
                best_match, match_score = process.extractOne(extracted_text_clean, questions, scorer=fuzz.partial_ratio)
                print(f"Best Match: {best_match} (Score: {match_score})")
                
                matched_row = quizzes_df[quizzes_df['Question'] == best_match]
                if not matched_row.empty:
                    answer = matched_row['Answer'].iloc[0]
                    result = f"The answer for the scanned question is: {answer}"
                else:
                    result = "The scanned text did not match any question in the database."
            except Exception as e:
                result = f"Error during OCR or processing: {str(e)}"

            print(result)

        elif key == ord('q'):  # Quit the program
            break

    cap.release()
    cv2.destroyAllWindows()

capture_and_process()
