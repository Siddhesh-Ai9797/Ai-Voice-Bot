import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from twilio.twiml.voice_response import VoiceResponse, Gather
from urllib.parse import unquote
from patient import get_patient_response, text_to_speech
from transcript import save_transcript
from call_manager import call_states
from scenarios import SCENARIOS


class CallHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0) or 0)
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''

        # Parse form data
        params = {}
        for item in post_data.split('&'):
            if '=' in item:
                key, value = item.split('=', 1)
                params[key] = value.replace('+', ' ')

        call_sid = params.get('CallSid', '')
        response = VoiceResponse()

        if self.path == '/start':
            state = call_states.get(call_sid, {})
            scenario = state.get('scenario', SCENARIOS[0])

            opening_line = get_patient_response(
                scenario['persona'],
                state.get('history', []),
                "The call just connected and the intro message finished. Say your opening line as this patient calling the clinic. Be natural and wait for the agent to respond."
            )

            state.setdefault('transcript', [])
            state['transcript'].append(f"PATIENT: {opening_line}")
            call_states[call_sid] = state

            voice = state.get('scenario', {}).get('voice', 'alloy')
            text_to_speech(opening_line, f"{call_sid}_patient_0.mp3", voice)

            # Wait for intro message to finish
            response.pause(length=6)

            gather = Gather(
                input='speech',
                timeout=10,
                speech_timeout='auto',
                action='/respond',
                method='POST',
                enhanced=True,
                speech_model='phone_call'
            )
            gather.play(f"{os.getenv('SERVER_URL')}/audio/{call_sid}_patient_0.mp3")
            response.append(gather)

        elif self.path == '/respond':
            agent_speech = unquote(params.get('SpeechResult', ''))
            state = call_states.get(call_sid, {})

            state['transcript'].append(f"AGENT: {agent_speech}")

            turn = state.get('turn', 0)
            state['turn'] = turn + 1

            if turn >= 20 or 'goodbye' in agent_speech.lower() or 'thank you for calling' in agent_speech.lower():
                response.say("Thank you, goodbye.")
                state['transcript'].append("PATIENT: Thank you, goodbye.")
                call_states[call_sid] = state
                save_transcript(call_sid, state)
                response.hangup()
            else:
                scenario = state.get('scenario', SCENARIOS[0])
                patient_reply = get_patient_response(
                    scenario['persona'],
                    state.get('history', []),
                    agent_speech
                )

                state['transcript'].append(f"PATIENT: {patient_reply}")
                call_states[call_sid] = state

                audio_filename = f"{call_sid}_patient_{turn+1}.mp3"
                voice = state.get('scenario', {}).get('voice', 'alloy')
                text_to_speech(patient_reply, audio_filename, voice)

                gather = Gather(
                    input='speech',
                    timeout=10,
                    speech_timeout='auto',
                    action='/respond',
                    method='POST',
                    enhanced=True,
                    speech_model='phone_call'
                )
                gather.play(f"{os.getenv('SERVER_URL')}/audio/{audio_filename}")
                response.append(gather)

                if 'goodbye' in patient_reply.lower():
                    save_transcript(call_sid, state)
                    response.hangup()

            call_states[call_sid] = state

        elif self.path.startswith('/audio/'):
            filename = self.path.replace('/audio/', '')
            filepath = f"recordings/{filename}"

            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        self.send_response(200)
        self.send_header('Content-Type', 'text/xml')
        self.end_headers()
        self.wfile.write(str(response).encode())

    def do_GET(self):
        if self.path.startswith('/audio/'):
            self.do_POST()
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot server running')

    def log_message(self, format, *args):
        pass


def run_server():
    server = HTTPServer(('0.0.0.0', 8080), CallHandler)
    print("Server running on port 8080")
    server.serve_forever()