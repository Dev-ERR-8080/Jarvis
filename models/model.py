import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

class GeminiModel:
    def __init__(self):
        # Configure the API key securely from environment variables
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_text(self, prompt_text):
        """
        Sends a prompt to the Gemini model and returns the generated text.
        """
        try:
            # Generate content from the model
            response = self.model.generate_content(prompt_text)
            
            # Return the text from the response
            return response.text
            
        except Exception as e:
            return f"An error occurred while generating content: {e}"

# Example of how to use this class:
if __name__ == '__main__':
    gemini_ai = GeminiModel()
    test_prompt = "Write a short, engaging story about a robot who discovers an old record player."
    response = gemini_ai.generate_text(test_prompt)
    print(response)