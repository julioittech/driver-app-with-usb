### Documentation for Running the OCR-Database Integration System

#### **Overview**
This system utilizes optical character recognition (OCR) to capture text from images via a camera feed, compares the extracted text against a quiz database stored in an SQLite database, and then triggers a GPIO LED response based on whether a match is found in the database.

#### **Components and Technologies Used**
1. **OpenCV**: Used for capturing video frames from a camera.
2. **Tesseract OCR**: Used for optical character recognition to extract text from images.
3. **FuzzyWuzzy**: Used for fuzzy text matching between OCR results and quiz data.
4. **SQLite**: Stores quiz data (questions and answers).
5. **GPIO**: Manages an LED indicator based on the OCR results (whether a match is found).
6. **PIL (Python Imaging Library)**: Used for image handling and processing.

#### **System Requirements**
To successfully run this system, the following software and libraries must be installed:

1. **Python 3.x**: The system is developed in Python 3.
2. **OpenCV**: For capturing and processing video frames.
3. **Tesseract OCR**: For text recognition from images.
4. **Pillow**: For handling image operations.
5. **FuzzyWuzzy**: For fuzzy text matching.
6. **SQLite**: For storing and querying quiz data.
7. **Raspberry Pi or Equivalent**: GPIO control for LED.
8. **GPIO utility (gpioset)**: To toggle the GPIO pins.

#### **Installation Steps**
1. **Install Python Libraries**:
   Use `pip` to install the necessary libraries.
   ```bash
   pip install opencv-python pillow fuzzywuzzy pytesseract python-Levenshtein
   ```

2. **Install Tesseract OCR**:
   You will need to install Tesseract OCR, which is the engine for optical character recognition.
   - **On Ubuntu**:
     ```bash
     sudo apt install tesseract-ocr
     ```
   - **On Raspberry Pi**:
     ```bash
     sudo apt-get install tesseract-ocr
     ```

3. **SQLite Database**:
   This system assumes you have an SQLite database (`quizzes.db`) containing quiz data. The database should have a table (`quizzes`) with the following fields:
   - `id` (integer, primary key)
   - `Question` (text)
   - `Answer` (text)

   Ensure the table is populated with the quiz data before running the system.

4. **GPIO Setup**:
   If using a Raspberry Pi or equivalent hardware, ensure you have the GPIO setup ready. Install the GPIO libraries and ensure the `gpioset` utility is available to toggle the LED connected to the designated pin.


#### **Running the System**
1. **Camera Setup**:
   Ensure your camera is properly connected and accessible. The system uses the default camera (index `0`). If you have multiple cameras or want to use a specific one, you can modify the camera index in the code.

2. **Prepare the SQLite Database**:
   Before running the script, ensure that the `quizzes.db` database is populated with questions and answers from your quiz CSV or other data source. The system queries the database for these questions and answers when processing OCR results.

3. **GPIO Pin Setup**:
   The system is designed to toggle an LED connected to GPIO pin 20. Ensure your LED is connected to the appropriate pin on your Raspberry Pi or other GPIO-compatible hardware.

4. **Run the Script**:
   Run the Python script that captures frames, processes them using OCR, and checks them against the SQLite database:
   ```bash
   python withdb.py
   ```

   - The system will start processing frames from the camera feed.
   - It will extract text from every `N`-th frame (based on the `frame_skip` setting).
   - If a match is found in the database, the LED will be turned on. If no match is found, the LED will remain off.
   - The OCR text matching uses fuzzy matching, so it works even with minor errors in the extracted text.

5. **View OCR Results**:
   The OCR results will be printed to the console, showing the matched question, the corresponding answer, and the match score (if a match is found). For example:
   ```


6. **Quit the System**:
   Press the 'q' key to stop the frame capture and OCR process.

#### **How the System Works**
1. **OCR Text Extraction**:
   The system captures video frames from the camera in real-time. It processes each frame, converting it to an image format suitable for Tesseract OCR, and extracts the text from the image.

2. **Text Matching**:
   The extracted text is cleaned and matched against the quiz questions stored in the SQLite database using fuzzy text matching with the FuzzyWuzzy library. If a match score greater than 80 is found, it considers the text to be a valid match.

3. **GPIO Response**:
   Based on the match:
   - If a match is found, the LED connected to the GPIO pin will turn on.
   - If no match is found, the LED will be turned off.
   
   The status of the LED provides immediate feedback on whether the OCR result matched any of the stored questions.

4. **Threading**:
   The system uses a separate thread (`ocr_processing_thread`) to handle OCR processing. This allows for continuous video capture while OCR is processed asynchronously.

5. **Error Handling**:
   If there is an error in processing the OCR or matching the text, an error message will be printed to the console, and the LED will be turned off.

#### **Troubleshooting**
1. **OCR Not Detecting Text**:
   - Ensure the camera has good lighting and is focused on the text. OCR accuracy depends heavily on image quality.
   - You may need to adjust the `lang='ita'` parameter in `image_to_string()` to match the language of the text you are trying to extract.
   
2. **No Match in the Database**:
   - Check the quiz data in your SQLite database to ensure that it contains relevant questions and answers.
   - Ensure that the text is extracted clearly; OCR results might be affected by the quality of the image or the font used in the text.

3. **GPIO Not Working**:
   - Verify the wiring and configuration of your GPIO pins. Ensure that the pin number (`LED_PIN`) is correct and that your system has access to GPIO control.
   - If you are not using a Raspberry Pi, you may need to adjust the GPIO control code or use a different library depending on your hardware.

#### **Customization and Expansion**
- **Customize OCR Language**: The current system is set to recognize Italian text (`lang='ita'`). You can modify this to support different languages by changing the language parameter in the `image_to_string()` function.
- **Change GPIO Pin**: If you want to control a different GPIO pin, simply modify the `LED_PIN` variable to the desired pin number.
- **Frame Processing Rate**: The `frame_skip` variable controls how often the system processes frames. Adjust this value to control the speed of OCR processing.
  
#### **Conclusion**
This system leverages OCR to process real-time camera feeds, matches extracted text with quiz questions stored in an SQLite database, and provides feedback via GPIO control. By following the steps outlined in this documentation, you can set up, run, and customize the system for various use cases, such as automated quizzes or interactive learning platforms.


#### **Note**
Disabling the Bluetooth and Wifi if not used will help in consuming less power and also keep it from getting hot. Recommended to use the heat sink and fan. Attatch external 3.3V power source to the Piezeo vibrarotor for smooth working. 
