# import asyncio, threading, json, struct, sys
# import websockets, pvporcupine, pyaudio
# from collections import deque
# from hotword_awake import PICOVOICE_ACCESS_KEY
# from utils.voice_output import say

# PORT = 8765
# CLIENTS = set()

# # 2-second audio history
# RING_BUFFER_SIZE = 2  # seconds
# ring_buffer = None    # will be init after porcupine is created

# def play_welcome_prompt():
#     say("Hello Sir, how can I help you")
# def play_hmm_prompt():
#     say("Hmm")

# async def broadcast_state(state: str):
#     if not CLIENTS:
#         return
#     msg = json.dumps({"event": state})
#     dead = []
#     for ws in list(CLIENTS):
#         try:
#             await ws.send(msg)
#         except Exception:
#             dead.append(ws)
#     for ws in dead:
#         CLIENTS.discard(ws)
#     print(f"Broadcasted state: {state}")

# async def websocket_handler(ws):
#     CLIENTS.add(ws)
#     await ws.send(json.dumps({"event":"ready"}))
#     try:
#         await ws.wait_closed()
#     finally:
#         CLIENTS.discard(ws)

# async def run_assistant_process(prebuffer_snapshot):
#     await broadcast_state("processing")
#     if not prebuffer_snapshot:
#         threading.Thread(target=play_welcome_prompt, daemon=True).start()
    

#     if prebuffer_snapshot:
#         import wave
#         with wave.open("prebuffer.wav", "wb") as wf:
#             wf.setnchannels(1)
#             wf.setsampwidth(2)  # 16-bit
#             wf.setframerate(16000)
#             wf.writeframes(struct.pack("<" + "h"*len(prebuffer_snapshot), *prebuffer_snapshot))

#     proc = await asyncio.create_subprocess_exec(
#         sys.executable, "jarvis_assistant.py", "--prebuffer", "prebuffer.wav"
#     )
#     await proc.wait()
#     await broadcast_state("idle")

# async def notify_hotword(prebuffer_snapshot):
#     await broadcast_state("listening")
#     await run_assistant_process(prebuffer_snapshot)

# async def hotword_loop():
#     print("Initializing Porcupine…")
#     porcupine = pvporcupine.create(access_key=PICOVOICE_ACCESS_KEY, keywords=["jarvis"])
#     global ring_buffer
#     ring_buffer = deque(maxlen=porcupine.sample_rate * RING_BUFFER_SIZE)

#     pa = pyaudio.PyAudio()
#     stream = pa.open(rate=porcupine.sample_rate,
#                      channels=1, format=pyaudio.paInt16,
#                      input=True, frames_per_buffer=porcupine.frame_length)

#     loop = asyncio.get_running_loop()

#     while True:
#         pcm_data = await loop.run_in_executor(None, stream.read, porcupine.frame_length)
#         pcm = struct.unpack_from("h" * porcupine.frame_length, pcm_data)
#         # store in buffer
#         ring_buffer.extend(pcm)
#         if porcupine.process(pcm) >= 0:
#             print("*** Wakeword detected ***")
            
#             collected = []
#             for _ in range(int(3 * porcupine.sample_rate / porcupine.frame_length)):
#                 pcm_data = await loop.run_in_executor(None, stream.read, porcupine.frame_length)
#                 pcm2 = struct.unpack_from("h"*porcupine.frame_length, pcm_data)
#                 collected.extend(pcm2)
                
#             await notify_hotword(prebuffer_snapshot=collected)
#             await asyncio.sleep(2)   # debounce

#         await asyncio.sleep(0)  # yield back

# async def start_websocket_server():
#     async with websockets.serve(websocket_handler, "0.0.0.0", PORT):
#         print(f"Server on ws://localhost:{PORT}")
#         await asyncio.Future()  # run forever
# async def main():
#     # run both tasks concurrently
#     await asyncio.gather(
#         start_websocket_server(),
#         hotword_loop()
#     )

# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio, threading, json, struct, sys, time, tempfile, os, wave
import websockets, pvporcupine, pyaudio, audioop
from collections import deque
from hotword_awake import PICOVOICE_ACCESS_KEY
from utils.voice_output import say

PORT = 8765
CLIENTS = set()
ASSISTANT_ACTIVE = False

# --- CONFIG ---
RING_BUFFER_SECONDS = 3
DEBOUNCE_SECONDS = 2
SILENCE_THRESHOLD = 200     # amplitude level for silence detection
SILENCE_DURATION = 1.2      # seconds of silence to stop recording

# --- WebSocket Notifications ---
async def broadcast_state(state: str):
    if not CLIENTS: return
    msg = json.dumps({"event": state})
    dead = []
    for ws in list(CLIENTS):
        try:
            await ws.send(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        CLIENTS.discard(ws)
    print(f"[WebSocket] Broadcasted: {state}")

async def websocket_handler(ws):
    CLIENTS.add(ws)
    await ws.send(json.dumps({"event": "ready"}))
    try:
        await ws.wait_closed()
    finally:
        CLIENTS.discard(ws)

# --- Helper ---
def save_wav(filename, pcm, rate=16000):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(struct.pack("<" + "h"*len(pcm), *pcm))

def is_silence(pcm):
    return audioop.rms(struct.pack("<" + "h"*len(pcm), *pcm), 2) < SILENCE_THRESHOLD

# --- Assistant Handling ---
async def run_assistant_process(prebuffer_snapshot):
    global ASSISTANT_ACTIVE
    ASSISTANT_ACTIVE = True
    await broadcast_state("processing")

    # write temp audio file
    tmp_path = os.path.join(tempfile.gettempdir(), f"prebuffer_{int(time.time())}.wav")
    save_wav(tmp_path, prebuffer_snapshot)

    def play_prompt():
        say("Hmm")

    threading.Thread(target=play_prompt, daemon=True).start()

    proc = await asyncio.create_subprocess_exec(
        sys.executable, "jarvis_assistant.py", "--prebuffer", tmp_path,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        print("[Assistant Error]", stderr.decode())
    else:
        print("[Assistant Output]", stdout.decode())

    # os.remove(tmp_path)
    ASSISTANT_ACTIVE = False
    await broadcast_state("idle")

# --- Hotword + Recording Loop ---
async def hotword_loop():
    print("🎧 Initializing Porcupine wakeword engine…")
    porcupine = pvporcupine.create(
        access_key=PICOVOICE_ACCESS_KEY,
        keywords=["jarvis"],
        sensitivities=[0.6]
    )

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    ring_buffer = deque(maxlen=porcupine.sample_rate * RING_BUFFER_SECONDS)
    print("✅ Listening for wakeword 'Jarvis'...")

    loop = asyncio.get_running_loop()

    try:
        while True:
            pcm_data = await loop.run_in_executor(None, stream.read, porcupine.frame_length)
            pcm = struct.unpack_from("h"*porcupine.frame_length, pcm_data)
            ring_buffer.extend(pcm)

            if porcupine.process(pcm) >= 0 and not ASSISTANT_ACTIVE:
                print("✨ Wakeword detected! Recording command...")
                await broadcast_state("listening")

                collected = list(ring_buffer)

                silence_time = 0
                start = time.time()

                while silence_time < SILENCE_DURATION and (time.time() - start) < 10:
                    pcm_data = await loop.run_in_executor(None, stream.read, porcupine.frame_length)
                    pcm = struct.unpack_from("h"*porcupine.frame_length, pcm_data)
                    collected.extend(pcm)
                    if is_silence(pcm):
                        silence_time += porcupine.frame_length / porcupine.sample_rate
                    else:
                        silence_time = 0

                asyncio.create_task(run_assistant_process(collected))
                await asyncio.sleep(DEBOUNCE_SECONDS)

            await asyncio.sleep(0.01)

    except KeyboardInterrupt:
        print("🛑 Exiting hotword listener...")
    finally:
        print("🔧 Cleaning up resources...")
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()

# --- WebSocket Server ---
async def start_websocket_server():
    async with websockets.serve(websocket_handler, "0.0.0.0", PORT):
        print(f"🌐 WebSocket server ready on ws://localhost:{PORT}")
        await asyncio.Future()  # run forever

# --- Main ---
async def main():
    await asyncio.gather(start_websocket_server(), hotword_loop())

if __name__ == "__main__":
    asyncio.run(main())
