# from transformers import T5Tokenizer, T5ForConditionalGeneration
# import torch

# class LocalT5:
#     def __init__(self):
#         # Load the tokenizer and model from Hugging Face Hub.
#         # This will download the model to your local machine.
#         self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")
#         self.model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small")

#         # Check if a GPU is available and move the model to it.
#         if torch.cuda.is_available():
#             self.device = torch.device("cuda")
#         else:
#             self.device = torch.device("cpu")
            
#         self.model.to(self.device)

#     def predict(self, prompt):
#         """Generates a response to a given prompt."""
#         try:
#             # Tokenize the input text.
#             inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
#             # Generate the output text.
#             outputs = self.model.generate(**inputs, max_length=150)
            
#             # Decode the output tokens and return the result.
#             response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
#             return response
            
#         except Exception as e:
#             return f"An error occurred during generation: {e}"

# # Example of how you would use this class in your commands.py:
# #
# # from models.LocalT5 import LocalT5
# # local_llm = LocalT5()
# #
# # def handle_command(command):
# #     if "summarize" in command:
# #         article = "..."
# #         summary = local_llm.predict(f"Summarize the following text: {article}")
# #         return summary
# #     # ... other commands


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