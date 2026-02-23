import requests
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("GENESYS_CLIENT_ID")
CLIENT_SECRET = os.getenv("GENESYS_CLIENT_SECRET")
REGION = os.getenv("GENESYS_REGION")

TOKEN_ENDPOINT = f"https://login.{REGION}.pure.cloud/oauth/token"
VOCAB_METADATA_URL = f"https://api.{REGION}.pure.cloud/api/v2/conversations/{{conversation_id}}/recordingmetadata"
VOCAB_MEDIA_URI_URL = f"https://api.{REGION}.pure.cloud/api/v2/conversations/{{conversation_id}}/recordings/{{recording_id}}?formatId=WAV&download=true&mediaFormats=WAV"

OUTPUT_DIR = "recordings"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_token():
    body = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(TOKEN_ENDPOINT, data=body)
    response.raise_for_status()
    return response.json()["access_token"]


def get_audio_id(conversation_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = VOCAB_METADATA_URL.format(conversation_id=conversation_id)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    audio_id = next(
        (item['id'] for item in data if item.get('media') == 'audio' and item.get('mediaSubtype') == 'Trunk'),
        None
    )

    if not audio_id:
        raise Exception("No audio recording found")

    return audio_id


def get_audio_url(conversation_id, recording_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = VOCAB_MEDIA_URI_URL.format(conversation_id=conversation_id, recording_id=recording_id)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["mediaUris"]["S"]["mediaUri"]


def download_audio(conversation_id):
    token = get_token()

    recording_id = get_audio_id(conversation_id, token)
    audio_url = get_audio_url(conversation_id, recording_id, token)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(audio_url, headers=headers, stream=True)
    response.raise_for_status()

    output_file = os.path.join(OUTPUT_DIR, f"{conversation_id}_single.wav")

    with open(output_file, "wb") as f:
        for chunk in response.iter_content(8192):
            if chunk:
                f.write(chunk)

    print(f"SUCCESS:{output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: Conversation ID missing")
        sys.exit(1)

    conversation_id = sys.argv[1]

    try:
        download_audio(conversation_id)
        sys.exit(0)
    except Exception as e:
        print(f"ERROR:{str(e)}")
        sys.exit(1)
