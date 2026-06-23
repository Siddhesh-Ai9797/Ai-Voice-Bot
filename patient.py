import os
from openai import OpenAI

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_patient_response(scenario_persona, conversation_history, agent_said):
    """Ask GPT-4o what the patient should say next"""

    conversation_history.append({
        "role": "user",
        "content": agent_said
    })

    messages = [
        {
            "role": "system",
            "content": f"""You are playing the role of a patient calling a medical clinic's automated phone system.

{scenario_persona}

IMPORTANT RULES:
- Keep responses SHORT — 1-2 sentences max, like real phone conversation
- Sound natural and human, not robotic
- Stay in character at all times
- Do NOT end the call until your request is FULLY completed
- Your request is complete ONLY when: appointment is confirmed with date and time, OR refill is confirmed, OR your question is fully answered
- If the agent gives vague or incomplete answers, keep asking until you get a clear answer
- If the agent asks you a question, answer it and then redirect back to your goal
- Only say "Thank you, goodbye" when you are 100% satisfied with the outcome
- Do not repeat yourself unnecessarily
- React naturally to what the agent says"""
        }
    ] + conversation_history

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=100,
        temperature=0.7
    )

    patient_reply = response.choices[0].message.content.strip()

    conversation_history.append({
        "role": "assistant",
        "content": patient_reply
    })

    return patient_reply


def text_to_speech(text, filename, voice="alloy"):
    """Convert text to audio using OpenAI TTS"""
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    os.makedirs("recordings", exist_ok=True)
    filepath = f"recordings/{filename}"
    with open(filepath, 'wb') as f:
        f.write(response.content)
    return filepath