# Architecture

## System Overview

The bot is built on a webhook-driven architecture using Twilio for telephony,
OpenAI GPT-4o for the patient brain, and OpenAI TTS for voice synthesis.
When the bot calls the target number, Twilio connects the call and immediately
hits a local HTTP server via an ngrok tunnel. From that point, every agent
utterance triggers a POST request to our server, GPT-4o decides what the
patient says next, TTS converts it to audio, and Twilio plays it on the call.
This loop continues until the conversation ends naturally or hits the 20-turn
safety cap.

## Key Design Decisions

**Twilio + ngrok over a hosted server:** The challenge required making real
outbound calls without production infrastructure. Twilio handles all telephony
complexity — dialing, audio streaming, recording, and speech recognition —
while ngrok exposes our local server to Twilio's webhooks without deploying
anything to the cloud. This kept costs under $5 total and setup under 30
minutes.

**GPT-4o as the patient brain:** Each patient has a detailed persona prompt
describing their name, age, medical situation, personality, and goal. GPT-4o
reads the full conversation history on every turn and decides what the patient
says next. Crucially, the patient is instructed not to end the call until their
request is fully resolved — confirmed appointment with date and time, confirmed
refill, or complete answer to their question. This makes the bot a genuine
stress-tester rather than a scripted benchmark runner.

**OpenAI TTS with persona-specific voices:** Each of the 10 patient personas
uses a different OpenAI TTS voice (alloy, nova, echo, shimmer, onyx, fable)
to simulate demographic diversity. Male and female voices are assigned to match
each patient's gender, making conversations more realistic for their agent's
speech recognition.

**Separation of concerns across 5 modules:** The codebase is split into
`patient.py` (GPT-4o and TTS), `server.py` (Twilio webhook handling),
`call_manager.py` (outbound calls and recording downloads), `transcript.py`
(saving conversation logs), and `scenarios.py` (patient personas). Each module
has a single responsibility, making the system easy to extend with new scenarios
or swap out components (e.g. replacing OpenAI TTS with ElevenLabs).

**Dual recording strategy:** Twilio records the full dual-channel call (both
the patient bot and the Athena agent) which is downloaded after all calls
complete. This gives a complete audio record of every conversation for review
and bug documentation.