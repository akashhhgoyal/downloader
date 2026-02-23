import requests
import time
import sys
import os
from dotenv import load_dotenv

# Load .env credentials
load_dotenv()

CLIENT_ID = os.getenv("GENESYS_CLIENT_ID")
CLIENT_SECRET = os.getenv("GENESYS_CLIENT_SECRET")
REGION = os.getenv("GENESYS_REGION", "aps1")

TOKEN_ENDPOINT = f"https://login.{REGION}.pure.cloud/oauth/token"
VOCAB_METADATA_URL = f"https://api.{REGION}.pure.cloud/api/v2/conversations/{{conversation_id}}/recordingmetadata"
VOCAB_MEDIA_URI_URL = f"https://api.{REGION}.pure.cloud/api/v2/conversations/{{conversation_id}}/recordings/{{recording_id}}?formatId=WAV&download=false&mediaFormats=WAV"

OUTPUT_DIR = "recordings"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- TOKEN ----------------
def get_token():
    body = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(TOKEN_ENDPOINT, data=body, timeout=30)
    response.raise_for_status()

    token = response.json().get("access_token")

    if not token:
        raise Exception("Failed to get token")

    return token


# ---------------- METADATA POLLING ----------------
def wait_for_recording(conversation_id, token):
    """
    Genesys dual channel recordings are not instantly available.
    We poll metadata until recording is ready.
    """

    MAX_WAIT = 180      # wait max 3 minutes
    INTERVAL = 5        # check every 5 seconds

    headers = {"Authorization": f"Bearer {token}"}
    url = VOCAB_METADATA_URL.format(conversation_id=conversation_id)

    start = time.time()

    while True:

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            audio_id = next((item['id'] for item in data if item.get('media') == 'audio'), None)

            if audio_id:
                return audio_id

        if time.time() - start > MAX_WAIT:
            raise Exception("Recording still processing in Genesys (timeout)")

        print("Waiting for recording to be available...")
        time.sleep(INTERVAL)


# ---------------- MEDIA URL ----------------
def get_audio_url(conversation_id, recording_id, token):
    url = VOCAB_MEDIA_URI_URL.format(conversation_id=conversation_id, recording_id=recording_id)
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    media_uri_0 = data.get("mediaUris", {}).get("0", {}).get("mediaUri")
    media_uri_1 = data.get("mediaUris", {}).get("1", {}).get("mediaUri")

    if not media_uri_0 or not media_uri_1:
        raise Exception("Dual channel audio not ready yet")

    return media_uri_0, media_uri_1


# ---------------- DOWNLOAD ----------------
def download_audio(conversation_id):

    token = get_token()

    # Wait until recording ready
    recording_id = wait_for_recording(conversation_id, token)

    audio_url_0, audio_url_1 = get_audio_url(conversation_id, recording_id, token)

    headers = {"Authorization": f"Bearer {token}"}

    output_file_0 = os.path.join(OUTPUT_DIR, f"{conversation_id}_customer.wav")
    output_file_1 = os.path.join(OUTPUT_DIR, f"{conversation_id}_agent.wav")

    # timeout VERY IMPORTANT (prevents infinite wait)
    response_0 = requests.get(audio_url_0, headers=headers, stream=True, timeout=120)
    response_0.raise_for_status()

    response_1 = requests.get(audio_url_1, headers=headers, stream=True, timeout=120)
    response_1.raise_for_status()

    with open(output_file_0, 'wb') as f:
        for chunk in response_0.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    with open(output_file_1, 'wb') as f:
        for chunk in response_1.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"SUCCESS:{output_file_0},{output_file_1}")


# ---------------- MAIN ----------------
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("ERROR:Conversation ID missing")
        sys.exit(1)

    conversation_id = sys.argv[1]

    try:
        download_audio(conversation_id)
        sys.exit(0)

    except Exception as e:
        print(f"ERROR:{str(e)}")
        sys.exit(1)
