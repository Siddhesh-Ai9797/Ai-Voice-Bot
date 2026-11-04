# PGAI Voice Bot

An automated voice bot that simulates patients calling Pretty Good AI's Athena healthcare voice agent. The bot makes outbound calls, conducts realistic patient conversations, records and transcribes both sides, and identifies bugs in the agent's responses.

## Architecture

See `architecture.md` for full details.

## Project Structure
pgai-voice-bot/
├── main.py           # Entry point — starts server and orchestrates calls
├── server.py         # HTTP server handling Twilio webhooks
├── patient.py        # GPT-4o patient brain and OpenAI TTS
├── call_manager.py   # Twilio call management and recording downloads
├── transcript.py     # Transcript saving
├── scenarios.py      # 10 patient personas and test scenarios
├── bug_report.md     # Bugs found in Athena agent
├── architecture.md   # System design decisions
├── .env.example      # Environment variable template
├── transcripts/      # Saved call transcripts
└── recordings/       # Full call recordings (mp3)

## Requirements

- Python 3.11+
- Twilio account (paid, not trial)
- OpenAI API key
- ngrok

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Siddhesh-Ai9797/pgai-voice-bot.git
cd pgai-voice-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Fill in your values in `.env`:
TWILIO_ACCOUNT_SID=your_account_sid

TWILIO_AUTH_TOKEN=your_auth_token

TWILIO_PHONE_NUMBER=+1xxxxxxxxxx

OPENAI_API_KEY=your_openai_key

TARGET_NUMBER=+18054398008

SERVER_URL=https://your-ngrok-url.ngrok-free.app

### 4. Start ngrok

In a separate terminal:

```bash
ngrok http 8080
```

Copy the forwarding URL and set it as `SERVER_URL` in your `.env` file.

### 5. Run the bot

```bash
python main.py
```

The bot will make 10 calls sequentially with 3 minutes between each call. Total runtime is approximately 35-40 minutes.

## How It Works

1. `main.py` starts a local HTTP server on port 8080
2. ngrok exposes that server to the public internet
3. For each scenario the bot calls the target number via Twilio
4. Twilio hits `/start` on our server — GPT-4o generates the patient's opening line
5. OpenAI TTS converts it to audio and Twilio plays it on the call
6. Their agent responds — Twilio transcribes it and sends it to `/respond`
7. GPT-4o reads the agent's response and generates the next patient reply
8. This loop continues until the conversation ends naturally or hits 20 turns
9. Transcripts are saved to `transcripts/` and full recordings downloaded from Twilio

## Test Scenarios

| # | Patient | Scenario |
|---|---------|----------|
| 1 | John Smith | Simple appointment scheduling |
| 2 | Maria Garcia | Medication refill request |
| 3 | David Lee | Appointment rescheduling |
| 4 | Susan White | Insurance question |
| 5 | Robert Johnson | Confused elderly patient |
| 6 | Emily Chen | Urgent same-day appointment |
| 7 | Michael Brown | Weekend appointment request |
| 8 | Jennifer Davis | Cancellation request |
| 9 | James Wilson | Multiple requests in one call |
| 10 | Patricia Martinez | Unclear and rambling patient |

## Cost Estimate

- Twilio phone number: ~$1.15/month
- Twilio call charges: ~$0.013/min × 10 calls × 3 min = ~$0.39
- OpenAI TTS: ~$0.015 per 1K characters × 10 calls = ~$1.50
- OpenAI GPT-4o: ~$2.00 for 10 calls
- **Total: ~$5.00**

## Environment Variables

| Variable | Description |
|----------|-------------|
| TWILIO_ACCOUNT_SID | Your Twilio Account SID |
| TWILIO_AUTH_TOKEN | Your Twilio Auth Token |
| TWILIO_PHONE_NUMBER | Your Twilio phone number in E.164 format |
| OPENAI_API_KEY | Your OpenAI API key |
| TARGET_NUMBER | Pretty Good AI test number |
| SERVER_URL | Your ngrok public URL |