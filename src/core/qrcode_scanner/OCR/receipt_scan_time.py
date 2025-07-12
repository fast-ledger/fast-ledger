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

import sys
import re
from PIL import Image
import pytesseract

# 🔧 手動指定 tesseract.exe 路徑（請確認這個路徑正確）
try:
    # fmt: off
    pytesseract.pytesseract.tesseract_cmd =  r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    # fmt: on
except Exception as e:  # 上面這東西可能會出問題我柳個註解在這
    print(e)
    FileExistsError("可能需要把 'tesseract.exe' 放進這裡的資料夾 然後改路徑")


def extract_time_from_image(img_path):
    # Open image
    image = Image.open(img_path)
    # Run OCR (Traditional Chinese + English)
    text = pytesseract.image_to_string(image, lang="chi_tra+eng")
    # Normalize fullwidth colon to ASCII
    text = text.replace("：", ":")
    # Regex for HH:MM:SS or H:MM:SS
    pattern = re.compile(r"(\d{1,2}:\d{2}:\d{2})")
    matches = pattern.findall(text)
    return matches[0] if matches else None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"用法: {sys.argv[0]} <image_path>")
        sys.exit(1)

    img_path = sys.argv[1]
    time_str = extract_time_from_image(img_path)
    if time_str:
        print(f"時間：{time_str}")
    else:
        print("時間：未偵測到時間")
