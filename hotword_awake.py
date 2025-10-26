# import pvporcupine
# import pyaudio
# import struct
# import os
# import subprocess
# import sys
# from dotenv import load_dotenv
# load_dotenv()


# # Get your free Picovoice AccessKey from https://console.picovoice.ai/
# PICOVOICE_ACCESS_KEY = os.getenv("PVPORCUPINE_ACCESS_KEY")  

# def hotword_awake():
#     try:
#         # Get the path to the virtual environment's Python interpreter
#         venv_python_path = sys.executable
        
#         # Initialize Porcupine with the hotword 'Jarvis'
#         porcupine = pvporcupine.create(
#             access_key=PICOVOICE_ACCESS_KEY,
#             keywords=['jarvis']
#         )
        
#         # Setup PyAudio for microphone input
#         pa = pyaudio.PyAudio()
#         audio_stream = pa.open(
#             rate=porcupine.sample_rate,
#             channels=1,
#             format=pyaudio.paInt16,
#             input=True,
#             frames_per_buffer=porcupine.frame_length
#         )
        
#         print("Listening for hotword 'Jarvis'...")
        
#         while True:
#             # Read audio data from the microphone
#             pcm = audio_stream.read(porcupine.frame_length)
#             pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
#             # Process audio for hotword detection
#             keyword_index = porcupine.process(pcm)
            
#             if keyword_index >= 0:
#                 print("Hotword detected! Launching assistant...")
#                 # Use the explicit path to the venv's python interpreter
#                 subprocess.run([venv_python_path, "jarvis_assistant.py"], check=True)
#                 print("Assistant session ended. Listening again...")

#     except pvporcupine.PorcupineInvalidArgumentError as e:
#         print(f"Error: Invalid argument provided to Porcupine. Check your access key or hotword.")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     finally:
#         # Clean up resources
#         if porcupine is not None:
#             porcupine.delete()
#         if audio_stream is not None:
#             audio_stream.close()
#         if pa is not None:
#             pa.terminate()

# if __name__ == "__main__":
#     hotword_awake()


import threading
from time import sleep
import pvporcupine
import pyaudio
import struct
import os
import subprocess
import sys
from dotenv import load_dotenv
from utils.voice_output import say

load_dotenv()

def play_welcome_prompt():
    say("Hello sir, how can I help you")
    
# Get your free Picovoice AccessKey from https://console.picovoice.ai/
PICOVOICE_ACCESS_KEY = os.getenv("PVPORCUPINE_ACCESS_KEY")  

def hotword_awake():
    try:
        # Get the path to the virtual environment's Python interpreter
        venv_python_path = sys.executable
        
        # Initialize Porcupine with the hotword 'Jarvis'
        porcupine = pvporcupine.create(
            access_key=PICOVOICE_ACCESS_KEY,
            keywords=['jarvis']
        )
        
        # Setup PyAudio for microphone input
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        
        print("Listening for hotword 'Jarvis'...")
        
        while True:
            # Read audio data from the microphone
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
            # Process audio for hotword detection
            keyword_index = porcupine.process(pcm)
            
            if keyword_index >= 0:
                print("Hotword detected! Launching assistant...")          
                threading.Thread(target=play_welcome_prompt, daemon=True).start()
                # Close the audio stream to prevent feedback loop
                audio_stream.close()
                pa.terminate()
                porcupine.delete()
                
                # Use the explicit path to the venv's python interpreter
                subprocess.run([venv_python_path, "jarvis_assistant.py"], check=True)
                print("Assistant session ended. Restarting listener...")
                
                # Re-initialize resources
                porcupine = pvporcupine.create(
                    access_key=PICOVOICE_ACCESS_KEY,
                    keywords=['jarvis']
                )
                pa = pyaudio.PyAudio()
                audio_stream = pa.open(
                    rate=porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=porcupine.frame_length
                )
                print("Listening for hotword 'Jarvis'...")
                
    except pvporcupine.PorcupineInvalidArgumentError as e:
        print(f"Error: Invalid argument provided to Porcupine. Check your access key or hotword.")
    except KeyboardInterrupt:
        print("\nShutting down hotword listener...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Clean up resources
        # sleep(5)
        if 'porcupine' in locals() and porcupine is not None:
            porcupine.delete()
        if 'audio_stream' in locals() and audio_stream is not None:
            audio_stream.close()
        if 'pa' in locals() and pa is not None:
            pa.terminate()

if __name__ == "__main__":
    hotword_awake()