import requests
import time


class GenAIEngine:

    def __init__(self, model="phi3", cooldown=2):
        self.model = model
        self.last_output = ""
        self.last_time = 0
        self.cooldown = cooldown

    def analyze(self, text):

        if not text:
            return None

        # Cooldown control
        if time.time() - self.last_time < self.cooldown:
            return None

        prompt = f"""
        You are an intelligent screen assistant.

        Analyze the following text and describe what is happening:

        {text}

        Keep it short and clear.
        """

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )

            result = response.json()["response"].strip()

            if result == self.last_output:
                return None

            self.last_output = result
            self.last_time = time.time()

            return result

        except Exception as e:
            print("Ollama Error:", e)
            return None