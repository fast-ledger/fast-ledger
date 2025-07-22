#!/usr/bin/env python3
"""
extract_time_vscode.py

This script reads an image file, applies OCR via Tesseract, and extracts the first occurrence
of a time in HH:MM:SS format, printing it as "時間：HH:MM:SS".

Usage:
    python extract_time_vscode.py /path/to/image.jpg

Requirements:
    - Python 3.6+
    - Tesseract OCR installed and accessible in PATH
        On Windows: download from https://github.com/tesseract-ocr/tesseract
        On macOS: brew install tesseract-lang
        On Linux: sudo apt-get install tesseract-ocr tesseract-ocr-chi-tra
    - Python packages: pillow, pytesseract
        Install via: pip install pillow pytesseract
"""

import re
from pathlib import Path
from PIL import Image
import pytesseract


try:
    # fmt: off
    pytesseract.pytesseract.tesseract_cmd = (Path(__file__).parent / "../../../../bin/Tesseract-OCR/tesseract.exe").resolve()
    # fmt: on
except Exception as e:  # 上面這東西可能會出問題我柳個註解在這
    print(e)
    FileExistsError("可能需要把 'tesseract.exe' 放進這裡的資料夾 然後改路徑")


def extract_time_from_image(image):
    text = pytesseract.image_to_string(image)
    # Normalize fullwidth colon to ASCII
    text = text.replace("：", ":")
    # Regex for HH:MM:SS or H:MM:SS
    pattern = re.compile(r"(\d{1,2}:\d{2}:\d{2})")
    matches = pattern.findall(text)
    return matches[0] if matches else None


if __name__ == "__main__":
    import cv2
    
    test_path = Path(__file__) / "../images"
    for img_path in test_path.iterdir():
        if not img_path.is_file(): continue
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        print(extract_time_from_image(image))