# 🧠 AI-Based Live Screen Analyzer (GenAI + OCR)

## 📌 Overview

This project is a **real-time AI system** that captures screen activity, extracts textual information using OCR, and interprets it using a local Generative AI model.

The system acts as an **intelligent assistant** that understands what is happening on the user's screen.

---

## 🚀 Features

- 🖥 Real-time screen capture
- 🔍 OCR-based text extraction (EasyOCR)
- 🧠 Context-aware interpretation using local LLM (Phi-3)
- ⚡ Adaptive frame processing (efficient & optimized)
- 📊 Live system metrics (CPU, Memory, FPS)
- 🪟 Interactive UI with OpenCV

---

## 🧩 System Pipeline


Screen Capture → Preprocessing → OCR → Context Aggregation → GenAI (Phi-3) → Insight


---

## 🛠 Technologies Used

- Python
- OpenCV
- EasyOCR
- MSS (screen capture)
- NumPy
- psutil (system monitoring)
- Ollama (local LLM runtime)
- Phi-3 (local LLM model)

---

## 📂 Project Structure


screen_analyzer/
│
├ capture_engine/
│ ├ screen_capture.py
│ ├ frame_buffer.py
│ ├ monitor_manager.py
│ ├ capture_config.py
│
├ ai_modules/
│ ├ ocr_engine.py
│ ├ genai_engine.py
│
├ main.py
├ requirements.txt
└ README.md


---

## ⚙️ Setup Instructions

### 1️⃣ Install Python

Recommended version:

Python 3.10


---

### 2️⃣ Clone the Repository


git clone https://github.com/YOUR_USERNAME/screen-analyzer.git

cd screen-analyzer


---

### 3️⃣ Create Virtual Environment

**Windows:**

py -3.10 -m venv venv
venv\Scripts\activate


**Mac/Linux:**

python3.10 -m venv venv
source venv/bin/activate


---

### 4️⃣ Install Dependencies


pip install --upgrade pip setuptools wheel
pip install -r requirements.txt


---

### 5️⃣ Install Ollama

Download from:
👉 https://ollama.com

---

### 6️⃣ Pull Phi-3 Model


ollama pull phi3


---

### 7️⃣ Start LLM Server


ollama run phi3


(Keep this running)

---

### 8️⃣ Run the Project


python main.py


---

## 🧪 Example Output


OCR CONTEXT:
Login to your account Enter password

PHI-3 INSIGHT:
User is interacting with a login interface.


---

## ⚠️ Known Limitations

- Works only with visual data (no audio yet)
- OCR accuracy depends on screen clarity
- GenAI output is basic (can be improved with prompt tuning)
- UI is minimal (OpenCV-based)

---

## 🔮 Future Work

- Audio processing and speech-to-text
- Multimodal fusion (audio + screen)
- Advanced UI (Streamlit / PyQt)
- Event detection and alerts
- Improved LLM reasoning

---

## 👨‍💻 Authors

- Arnav Khandelwal  
- Nishik Ojha  

---

## 📜 License

This project is for academic purposes.