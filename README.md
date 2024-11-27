
# OCR on Raspberry Pi

This project captures an image from a camera connected to a Raspberry Pi, extracts text using OCR, and matches it against a set of quiz questions stored in a CSV file. The best match is identified, and its corresponding answer is displayed.

## Prerequisites

### Hardware
- Raspberry Pi with an internet connection
- USB or Pi-compatible camera
- Sufficient power supply

### Software
- Raspberry Pi OS (with Python 3 pre-installed)
- Tesseract OCR installed on the Raspberry Pi

---

## Installation

### 1. Install Dependencies
Update your Raspberry Pi and install the required packages:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install tesseract-ocr libtesseract-dev python3-pip python3-opencv -y
```

Install Python libraries:
```bash
pip3 install opencv-python pytesseract fuzzywuzzy pandas pillow
```

### 2. Install Tesseract Language Data (Italian)
Ensure Tesseract has the Italian language data:
```bash
sudo apt install tesseract-ocr-ita
```


## Setup

1. Place your quiz data in a CSV file named `quizzes.csv` in the same directory as the script. The CSV must have the following format:
   - **Column 1**: `Question` (string)
   - **Column 2**: `Answer` (string)

   Example:
   ```csv
   Question,Answer
   What is the capital of Italy?,Rome
   ```

2. Place the script file (`main.py`) in the same directory.

---

## Running the Script

Run the script to start the camera feed:
```bash
python3 main.py
```

### Controls:
- **Press `c`**: Capture an image and perform OCR.
- **Press `q`**: Quit the application.

---

## Troubleshooting

### Common Issues
1. **Camera not detected**:
   - Ensure the camera is properly connected.
   - Check if the camera is enabled:
     ```bash
     sudo raspi-config
     ```
     Go to *Interface Options > Camera* and enable it.

2. **Low OCR Accuracy**:
   - Ensure good lighting conditions.
   - Check if the camera focus is clear.
   - Validate the `ita` language pack is installed.

3. **Tesseract not found**:
   - Verify the installation path using:
     ```bash
     which tesseract
     ```
     Update the `pytesseract.pytesseract_cmd` path in the script if necessary.

---


### Input (Image Text):
*"Qual è la capitale d'Italia?"*


## Credits
This project uses:
- [OpenCV](https://opencv.org/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [FuzzyWuzzy](https://github.com/seatgeek/fuzzywuzzy)

