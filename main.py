import time
import threading
from dotenv import load_dotenv

load_dotenv()

from server import run_server
from call_manager import make_call, download_recordings, call_states
from transcript import save_transcript
from scenarios import SCENARIOS


def main():
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to be ready
    print("Server started. Waiting 3 seconds for server to be ready...")
    time.sleep(3)

    print("Making calls...")
    print("NOTE: Make sure ngrok is running and SERVER_URL is set in .env")

    session_sids = []
    for i, scenario in enumerate(SCENARIOS):
        print(f"\n--- Call {i+1}/10 ---")
        sid = make_call(scenario)
        session_sids.append(sid)
        time.sleep(180)

    print("\nCalls made. Waiting for final call to complete...")
    time.sleep(300)

    print("Downloading full call recordings...")
    download_recordings(session_sids)
    print("Done!")


if __name__ == "__main__":
    main()