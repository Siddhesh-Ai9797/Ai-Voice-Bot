import os
import requests
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")
TARGET_NUMBER = os.getenv("TARGET_NUMBER")

# Global state per call
call_states = {}


def make_call(scenario):
    """Make a single outbound call"""
    print(f"\nCalling for scenario: {scenario['name']}")

    call = twilio_client.calls.create(
        to=TARGET_NUMBER,
        from_=TWILIO_PHONE,
        url=f"{os.getenv('SERVER_URL')}/start",
        method='POST',
        record=True,
        recording_channels='dual'
    )

    call_states[call.sid] = {
        'scenario': scenario,
        'history': [],
        'transcript': [],
        'turn': 0
    }

    print(f"Call SID: {call.sid}")
    return call.sid


def download_recordings(session_call_sids):
    """Download full call recordings from Twilio for this session only"""
    os.makedirs("recordings", exist_ok=True)

    for call_sid in session_call_sids:
        recordings = twilio_client.recordings.list(call_sid=call_sid)
        for recording in recordings:
            filename = f"recordings/full_call_{recording.call_sid}_{recording.sid}.mp3"
            if not os.path.exists(filename):
                url = f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"
                response = requests.get(url, auth=(
                    os.getenv("TWILIO_ACCOUNT_SID"),
                    os.getenv("TWILIO_AUTH_TOKEN")
                ))
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: {filename}")