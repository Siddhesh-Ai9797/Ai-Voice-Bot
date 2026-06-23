import os
from datetime import datetime


def save_transcript(call_sid, state):
    """Save transcript to file"""
    os.makedirs("transcripts", exist_ok=True)
    scenario = state.get('scenario', {})
    scenario_id = scenario.get('id', 0)
    scenario_name = scenario.get('name', 'unknown').replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcripts/call_{scenario_id:02d}_{scenario_name}_{timestamp}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Scenario: {scenario.get('name', 'unknown')}\n")
        f.write(f"Call SID: {call_sid}\n")
        f.write(f"Time: {datetime.now()}\n")
        f.write("=" * 50 + "\n\n")
        for line in state.get('transcript', []):
            f.write(line + "\n")

    print(f"Transcript saved: {filename}")