import speech_recognition as sr
from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.playback import play
import openai

debug = True
def synthesize_text(text, output_file):
    # Set up OpenAI API credentials
    openai.api_key = ""

    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name='en-US-Studio-O'
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        if debug:
            print(f'Audio content written to file "{output_file}"')

def updateTalkLog(text, speaker, talkLog):
    talkLog.append({"role": speaker, "content": text})
    return talkLog

def play_audio(output_file):
    audio = AudioSegment.from_file(output_file, format="mp3")
    play(audio)

def recognize_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        audio = recognizer.listen(source)

    try:
        user_input = recognizer.recognize_google(audio)
        if debug:
            print(f"You: {user_input}")
        return user_input
    except sr.UnknownValueError:
        if debug:
            print("Speech recognition could not understand audio.")
    except sr.RequestError as e:
        if debug:
            print(f"Could not request results from speech recognition service: {e}")

    return ""

# Generate and play TTS audio
synthesize_text("Hey Adam, How can I help?", "output.mp3")
play_audio("output.mp3")

talkLog = [{"role": "system", "content": "You are a helpful assistant named Talia who is smart, friendly and generally concise (a few sentances max) in your responses unless the complexity of the ask warrents a longer response "},]

# Simulate conversation
while True:
    # Receive user speech input
    user_input = recognize_speech()
    
    # Check for conversation end keyword
    if user_input.lower() == "bye":
        if debug:
            print("Chat ended.")
        break

    # Generate and play TTS audio for user input
    synthesize_text(user_input, "output.mp3")
    if debug:
        print(talkLog)
    talkLog = updateTalkLog(user_input, "user", talkLog)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=talkLog
    )

    # Print and play TTS audio for the response
    if debug:
        print(f"Bot: {response}")
    responseContent = response.choices[0].message.content
    updateTalkLog(responseContent, "assistant", talkLog)
    synthesize_text(responseContent, "output.mp3")
    play_audio("output.mp3")


