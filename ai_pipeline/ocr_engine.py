import easyocr
import cv2
import numpy as np
from datetime import datetime


class OCREngine:

    def __init__(
        self,
        languages=['en'],
        output_file="ocr_output.txt",
        history_size=3,
        confidence_threshold=0.5
    ):
        self.reader = easyocr.Reader(languages, gpu=False, verbose=False)
        self.output_file = output_file

        self.conf_threshold = confidence_threshold
        self.history_size = history_size

        self.text_history = []
        self.last_output = ""

    def preprocess(self, frame):

        frame = cv2.resize(frame, (960, 540))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        gray = cv2.equalizeHist(gray)

        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        return thresh

    def extract_text(self, frame):

        processed = self.preprocess(frame)

        results = self.reader.readtext(processed)

        texts = []

        for bbox, text, confidence in results:

            text = text.strip()

            if confidence > self.conf_threshold and len(text) > 2:
                texts.append(text)

        if not texts:
            return None

        combined_text = self._combine_text(texts)

        if combined_text == self.last_output:
            return None

        self.last_output = combined_text

        self.text_history.append(combined_text)

        if len(self.text_history) > self.history_size:
            self.text_history.pop(0)

        return self.get_context()

    def _combine_text(self, texts):

        unique_texts = list(dict.fromkeys(texts))

        return " ".join(unique_texts)

    def get_context(self):

        return " ".join(self.text_history)

    def save_text(self, text):

        if not text:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")

        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {text}\n")