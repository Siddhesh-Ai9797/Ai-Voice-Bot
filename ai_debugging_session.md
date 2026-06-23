# AI-Assisted Debugging Session

This document shows how I used AI (Claude) iteratively to debug and fix issues
during the development of the PGAI voice bot. Each section shows the problem,
the prompt I used, the AI's response, and the fix I applied.

---

## Bug 1 — Twilio Cannot Reach Local Server

**Problem:**
When I ran the bot for the first time the call connected but immediately dropped.
Twilio was not hitting my local server at all. The ngrok terminal showed zero
connections.

**My prompt to Claude:**
> "My Twilio call connects but immediately drops. Ngrok shows zero HTTP requests.
> The call is being made successfully (I have a Call SID) but nothing is hitting
> my /start endpoint. What's wrong?"

**Claude's diagnosis:**
The server was starting in a background thread at the same time the call was
being made. The call fired before the server was fully ready to accept
connections, so Twilio got no response and dropped the call.

**Fix applied:**
Added a 3 second delay between server start and the first call:

```python
# Before fix
server_thread.start()
make_call(scenario)  # fires immediately, server not ready

# After fix
server_thread.start()
time.sleep(3)  # wait for server to be ready
make_call(scenario)
```

---

## Bug 2 — Agent Transcripts Showing URL Encoded Text

**Problem:**
After the first successful calls I opened the transcript files and saw this:

```
AGENT: Yeah%2C%20sure.%20Uh%2C%20what%20is%20your%20issue%3F
PATIENT: I don't have any immediate issues, just scheduling a routine checkup.
AGENT: Okay%2C%20cool.%20We%20got%20an%20appointment%20for%2010%3A00%20a.m.
```

The agent lines were unreadable — full of %2C, %20, %3F characters.

**My prompt to Claude:**
> "My agent transcripts are showing %2C instead of commas and %20 instead of
> spaces. Example: `AGENT: Yeah%2C%20sure.%20What%20is%20your%20issue%3F`
> What's wrong and how do I fix it?"

**Claude's diagnosis:**
Twilio sends the SpeechResult field in the POST body as URL encoded form data.
%2C is a comma, %20 is a space, %3F is a question mark. I was reading the raw
value without decoding it first.

**Fix applied:**
Added `unquote` from urllib.parse to decode the agent speech before using it:

```python
# Before fix
from urllib.parse import unquote  # missing

agent_speech = params.get('SpeechResult', '')  # raw URL encoded

# After fix
from urllib.parse import unquote  # added at top

agent_speech = unquote(params.get('SpeechResult', ''))  # decoded
```

Result — clean readable transcripts:
```
AGENT: Yeah, sure. Uh, what is your issue?
PATIENT: I don't have any immediate issues, just scheduling a routine checkup.
AGENT: Okay, cool. We got an appointment for 10:00 a.m.
```

---

## Bug 3 — All Patients Sounded Identical

**Problem:**
Maria Garcia (52 year old female) sounded exactly the same as John Smith
(35 year old male). Both used the same robotic voice which made conversations
feel unrealistic.

**My prompt to Claude:**
> "All my patient personas sound identical. Maria Garcia is supposed to be a
> 52 year old woman but she sounds the same as John Smith. How do I give each
> patient a different voice using OpenAI TTS?"

**Claude's diagnosis:**
I was hardcoding `voice="alloy"` in the text_to_speech function for every
patient. OpenAI TTS supports multiple voices — alloy, echo, fable, onyx, nova,
shimmer — each with different characteristics.

**Fix applied:**
Added a `voice` field to each scenario and passed it through to TTS:

```python
# Before fix — hardcoded voice
def text_to_speech(text, filename, voice="alloy"):
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",  # always alloy
        input=text
    )

# After fix — dynamic voice per patient
def text_to_speech(text, filename, voice="alloy"):
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice=voice,  # uses scenario's voice
        input=text
    )

# scenarios.py — voice assigned per patient
{
    "id": 1,
    "name": "Simple Appointment Scheduling",
    "voice": "alloy",  # male
    "persona": "You are John Smith..."
},
{
    "id": 2,
    "name": "Medication Refill Request",
    "voice": "nova",  # female
    "persona": "You are Maria Garcia..."
}
```

Voice assignments used:
- Male patients: alloy, echo, onyx
- Female patients: nova, shimmer, fable
- Elderly male: onyx (deeper voice)

---

## Bug 4 — Bot Responding to Intro Message

**Problem:**
When the call connected the bot immediately responded to "This call will be
recorded for monitoring purposes" as if it was the agent's first message.
The patient's opening line made no sense as a response to that intro.

**My prompt to Claude:**
> "My bot is responding to the clinic's intro message 'this call will be
> recorded for monitoring purposes' before the actual agent speaks. How do
> I make the bot wait for the real agent to start talking?"

**Claude's diagnosis:**
The `/start` endpoint was immediately playing the patient's opening line the
moment the call connected. There was no delay to let the intro message finish
playing before the patient started speaking.

**Fix applied:**
Added a `response.pause(length=6)` before the patient speaks so the intro
message has time to finish:

```python
# Before fix — patient speaks immediately on connect
gather = Gather(input='speech', ...)
gather.play(patient_audio_url)
response.append(gather)

# After fix — 6 second pause lets intro finish first
response.pause(length=6)  # wait for intro message
gather = Gather(input='speech', ...)
gather.play(patient_audio_url)
response.append(gather)
```

---

## Bug 5 — Bot Ending Conversations Too Early

**Problem:**
The bot was cutting off conversations after 6 turns even when the patient's
request hadn't been resolved yet. In several calls the agent was mid-sentence
when the bot said goodbye and hung up.

**My prompt to Claude:**
> "My bot ends the call after 6 turns but some conversations need more turns
> to resolve. The agent is still talking when my bot says goodbye. How do I
> make the bot smarter about knowing when to end the call?"

**Claude's diagnosis:**
Two problems — the hard turn limit of 6 was too low for complex scenarios,
and the GPT-4o prompt wasn't instructing the patient to stay on the call until
the request was actually fulfilled.

**Fix applied:**

Increased turn limit to 20 as a safety cap:
```python
# Before fix
if turn >= 6 or 'goodbye' in agent_speech.lower():

# After fix
if turn >= 20 or 'goodbye' in agent_speech.lower():
```

Updated the GPT-4o system prompt to be goal-oriented:
```python
# Before fix
"If the conversation feels complete, end with 'Thank you, goodbye'"

# After fix
"""- Do NOT end the call until your request is FULLY completed
- Your request is complete ONLY when: appointment is confirmed with date
  and time, OR refill is confirmed, OR your question is fully answered
- If the agent gives vague or incomplete answers, keep asking
- Only say 'Thank you, goodbye' when you are 100% satisfied"""
```

Result — John Smith's call went 14 turns and successfully pushed back when
the agent said there was a problem booking, staying in character until
the appointment was confirmed.

---

## Bug 6 — 2-3 Second Delay Between Turns

**Problem:**
There was a noticeable 2-3 second gap between when the agent finished speaking
and when the patient responded. This made conversations feel unnatural.

**My prompt to Claude:**
> "There is a 2-3 second delay between the agent finishing and my patient
> responding. How do I reduce this latency?"

**Claude's diagnosis:**
The delay comes from 4 sequential steps that all take time:
1. Twilio detects silence and decides agent has finished speaking (~1 sec)
2. Twilio sends SpeechResult to our server (~0.2 sec)
3. GPT-4o generates the patient response (~0.5-1 sec)
4. OpenAI TTS converts text to audio (~0.5-1 sec)

Total: ~2-3 seconds unavoidable with this architecture.

**Attempted fix — reduced Twilio silence detection:**
```python
# Tried reducing timeout
gather = Gather(
    input='speech',
    timeout=3,          # reduced from 10
    speech_timeout='1'  # reduced from 'auto'
)
```

**Result:** This caused the bot to cut off mid-sentence. Reverted.

**Final fix — better speech model:**
```python
gather = Gather(
    input='speech',
    timeout=10,
    speech_timeout='auto',
    enhanced=True,
    speech_model='phone_call'  # more accurate for phone conversations
)
```

This improved speech recognition accuracy without cutting off sentences.
The 2-3 second delay remains as an accepted tradeoff.

**How to fully fix this in production:**
The proper solution is streaming TTS — start playing audio while it is still
being generated instead of waiting for the full audio file. This requires:

1. Switch from OpenAI TTS to a streaming-capable provider like ElevenLabs
   or Deepgram TTS
2. Use Twilio Media Streams instead of pre-generated audio files — this
   allows real-time audio streaming over WebSocket
3. Pipeline the steps — start TTS generation the moment GPT-4o begins
   responding, not after it finishes

This architecture would reduce latency from 2-3 seconds to under 500ms.
It was not implemented here as it requires production-grade WebSocket
infrastructure which is outside the scope of this challenge.

---

## Summary of Iterations

| # | Problem | Fix | Impact |
|---|---------|-----|--------|
| 1 | Server not ready when call fires | Added 3 sec delay | Calls now connect properly |
| 2 | URL encoded agent transcripts | Added unquote() | Transcripts now readable |
| 3 | All patients same voice | Added per-persona TTS voice | Conversations more realistic |
| 4 | Bot responds to intro message | Added 6 sec pause on connect | Patient waits for real agent |
| 5 | Bot ends calls too early | Increased turn limit, updated prompt | Longer more complete conversations |
| 6 | 2-3 sec response delay | Better speech model | Marginal improvement, accepted tradeoff |
