import assemblyai as aai
import openai as oa
import elevenlabs as el
from queue import Queue
import os

# Set API keys using environment variables
os.environ["ASSEMBLYAI_API_KEY"] = "YOUR_ASSEMBLYAI_API_KEY"
oa.api_key = "YOUR_OPENAI_API_KEY"
os.environ["ELEVENLABS_API_KEY"] = "YOUR_ELEVENLABS_API_KEY"

transcript_queue = Queue()

def on_data(transcript: aai.RealtimeTranscript):
    if not transcript.text:
        return
    if isinstance(transcript, aai.RealtimeFinalTranscript):
        transcript_queue.put(transcript.text)
        print("User:", transcript.text, end="\r\n")
    else:
        print(transcript.text, end="\r")

def on_error(error: aai.RealtimeError):
    print("An error occurred:", error)

def handle_conversation():
    while True:
        transcriber = aai.RealtimeTranscriber(
            on_data=on_data,
            on_error=on_error,
            sample_rate=44_100,
        )

        # Start the connection
        transcriber.connect()

        # Open the microphone stream
        microphone_stream = aai.extras.MicrophoneStream()

        # Stream audio from the microphone
        transcriber.stream(microphone_stream)

        # Close current transcription session with Ctrl + C
        transcriber.close()

        # Retrieve data from the queue
        transcript_result = transcript_queue.get()

        # Send the transcript to OpenAI for response generation
        response = oa.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": 'You are a highly skilled AI, answer the question given within 10000 characters.'},
                {"role": "user", "content": transcript_result}
            ]
        )

        text = response['choices'][0]['message']['content']

        # Convert response from text to audio and play it
        audio = el.generate(
            text=text,
            voice="Alice"
        )
        print("\nAI:", text, end="\n\r")
        el.play(audio)

handle_conversation()
