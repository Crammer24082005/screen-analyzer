import easyocr
import cv2
from datetime import datetime


class OCREngine:

    def __init__(self, languages=['en'], output_file="ocr_output.txt"):
        self.reader = easyocr.Reader(languages, gpu=False, verbose=False)
        self.output_file = output_file

    def extract_text(self, frame):

        # Resize frame for faster OCR
        small = cv2.resize(frame, (800, 450))

        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

        results = self.reader.readtext(gray)

        texts = []

        for bbox, text, confidence in results:
            if confidence > 0.5:
                texts.append(text)

        return texts

    def save_text(self, texts):

        if not texts:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")

        with open(self.output_file, "a", encoding="utf-8") as f:
            for text in texts:
                f.write(f"[{timestamp}] {text}\n")