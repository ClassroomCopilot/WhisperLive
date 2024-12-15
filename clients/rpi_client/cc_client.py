import os
import requests
from datetime import datetime
import time
import modules.whisperlive_client as whisper_client
import threading

# Load environment variables
from dotenv import load_dotenv
print("Loading environment variables...")
load_dotenv(dotenv_path='/home/kcar/.env')  # Adjust the path to your .env file
print("Environment variables loaded.")

# Verify environment variables
print("VITE_FASTAPI_HOST:", os.getenv('VITE_FASTAPI_HOST'))
print("VITE_FASTAPI_PORT:", os.getenv('VITE_FASTAPI_PORT'))
print("WHISPERLIVE_HOST:", os.getenv('WHISPERLIVE_HOST'))
print("WHISPERLIVE_PORT:", os.getenv('WHISPERLIVE_PORT'))

# RPi login to get token
def login():
    print("Attempting to login...")
    try:
        response = requests.post(f"http://{os.environ['VITE_FASTAPI_HOST']}:{os.environ['VITE_FASTAPI_PORT']}/rpi/login", json={"device_id": "rpi_zero"})
        print(f"Login response status: {response.status_code}")
        if response.status_code == 200:
            print("Login successful")
            return response.json()["token"]
        else:
            print("Login failed")
            raise Exception("Failed to login")
    except Exception as e:
        print(f"Exception during login: {e}")
        raise

# Setup directories
def setup_directories():
    print("Setting up directories...")
    user_dir = os.path.expanduser("~/data/users")  # Changed to user's home directory
    user_id = "rpi_user"
    user_transcript_dir = f"{user_dir}/{user_id}/transcripts"
    print(f"Transcript directory: {user_transcript_dir}")
    if not os.path.exists(user_transcript_dir):
        print(f"Directory does not exist. Creating directory: {user_transcript_dir}")
        os.makedirs(user_transcript_dir)
    else:
        print("Directory already exists.")
    return user_transcript_dir

# Global variables to manage accumulated text and timing
accumulated_text = ""
last_start = 0.0
last_end = 0.0
send_timer = None

def send_accumulated_text():
    global accumulated_text, last_start, last_end
    if accumulated_text:
        message = {"utterance": accumulated_text.strip(), "start": last_start, "end": last_end}
        print(f"Sending utterance to backend: {message}, start: {last_start}, end: {last_end}")
        response = requests.post(f"http://{os.environ['VITE_FASTAPI_HOST']}:{os.environ['VITE_FASTAPI_PORT']}/transcribe/utterance/handle_whisper_live_eos_utterance", json=message)
        if response.status_code == 200:
            print("Utterance sent successfully")
        else:
            print(f"Failed to send utterance: {response.status_code}, Response: {response.text}")
        accumulated_text = ""  # Reset the accumulated text after sending

def reset_send_timer():
    global send_timer
    if send_timer:
        send_timer.cancel()
    send_timer = threading.Timer(3.0, send_accumulated_text)
    send_timer.start()

def eos_callback(text, start, end):
    global accumulated_text, last_start, last_end
    print(f"Callback received: {text}, Start: {start}, End: {end}")

    start = float(start)
    end = float(end)

    # Update the accumulated text and times with the latest callback data
    if accumulated_text:
        accumulated_text += " " + text
    else:
        accumulated_text = text
        last_start = start

    last_end = end

# Main function to run the transcription client
def main():
    print("Starting RPi client")
    # Check for backend service readiness
    while True:
        try:
            response = requests.get(f"http://{os.environ['VITE_FASTAPI_HOST']}:{os.environ['VITE_FASTAPI_PORT']}/health")
            print(f"Health check response status: {response.status_code}")
            if response.status_code == 200:
                print("Backend service is ready")
                break
        except requests.exceptions.RequestException as e:
            print(f"Exception during health check: {e}")
        print("Waiting for the backend service to be ready...")
        # time.sleep(10)

    print("Logging in to get token...")
    token = login()
    print(f"Token received: {token}")
    user_transcript_dir = setup_directories()
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H-%M-%S")
    print(f"Current date: {current_date}, Current time: {current_time}")

    print("Initializing TranscriptionClient...")
    try:
        client = whisper_client.TranscriptionClient(
            host=os.environ["WHISPERLIVE_HOST"],
            port=os.environ["WHISPERLIVE_PORT"],
            lang="en",
            translate=False,
            model="small",
            use_vad=True,
            save_output_recording=True,
            output_recording_filename=f"{user_transcript_dir}/rec_{current_date}_{current_time}.wav",
            output_transcription_path=f"{user_transcript_dir}/trans_{current_date}_{current_time}.srt",
            callback=eos_callback
        )
        print("Starting TranscriptionClient...")
        client()
        print("TranscriptionClient started.")
    except Exception as e:
        print(f"Error during TranscriptionClient initialization: {e}")

if __name__ == "__main__":
    main()