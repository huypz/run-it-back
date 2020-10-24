import azure.cognitiveservices.speech as speechsdk
import pyaudio, wave, os, time
import gui as g

speech_key, service_region = "0b7fca8db83b454cab8ea579c7bb92aa", "eastus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

# pyaudio interface
p = pyaudio.PyAudio()

# pyaudio config
CHUNK = 1024  
FRAMES = 512
SAMPLE_FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100  
DEFAULT_FILE_NAME = "out.wav"
MAX_RECORD_SECONDS = 3600
# audio devices dict {"index": "name"}
# ex. {6: 'Speakers (Realtek High Definition Audio)', 7: 'Speakers (NVIDIA RTX Voice)', 8: 'Microphone (Realtek High Definition Audio)', 9: 'Microphone (NVIDIA RTX Voice)'}
audio_devices = {}
wasapi_devices = {}
device_info = {}
recorded_frames = []
use_loopback : bool
done_recording = False
done_playing = False
# input_device_id = p.get_default_output_device_info()
# output_device_id = p.get_default_output_device_info()
# input_device_info = {}
# output_device_info = {}

# azure config
done = False

# user config
keyword = "run it back"
enable_playback = True
record_seconds = 5
enable_logs = True

def main():
    gui = g.GUI()
    gui.root.mainloop()

    #speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    # speech_recognizer.recognized.connect(process_input)
    # start()


def start():
    # get devices and set default
    for i in range(0, p.get_device_count()):
        device = p.get_device_info_by_index(i)
        audio_devices[i] = device["name"]
        if (p.get_host_api_info_by_index(device["hostApi"])["name"] == "Windows WASAPI"):
            wasapi_devices[i] = device["name"]

    process_devices()
    speech_recognizer.recognized.connect(process_input)
    speech_recognizer.start_continuous_recognition()
    print("Speak into your microphone or say STOP to terminate the program.")
    record_device()
    global done_recording
    done_recording = False
    global done
    done = False


def stop():
    speech_recognizer.stop_continuous_recognition()
    global done_recording
    done_recording = True
    global done
    done = True
    time.sleep(1)
    p.terminate()


def process_input(evt):
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        text = evt.result.text.lower()
        print("Recognized: " + text)

        if (text.find(keyword) != -1):
            print("Running it back")
            speech_recognizer.stop_continuous_recognition()
            flush_frames()
            play_audio(DEFAULT_FILE_NAME)
            speech_recognizer.start_continuous_recognition()
        elif (text.find("stop") != -1):
            stop()

    
def process_devices():
    print_wasapi_devices()
    device_id = int(input("Choose output device to run it back (index): "))

    global device_info
    device_info = p.get_device_info_by_index(device_id)

    is_input = device_info["maxInputChannels"] > 0
    is_wasapi = (p.get_host_api_info_by_index(device_info["hostApi"])["name"]).find("WASAPI") != -1
    if not is_input and is_wasapi:
        global use_loopback
        use_loopback = True
        print("Selection is output. Using loopback mode")
    else:
        print("Error: Selection is either input or does not support loopback mode\n<Tip: select an output device!>")
        exit()


def record_device():
    stream = p.open(format = pyaudio.paInt16,
                    channels = CHANNELS,
                    rate = int(device_info["defaultSampleRate"]),
                    input = True,
                    frames_per_buffer = FRAMES,
                    input_device_index = device_info["index"],
                    as_loopback = True)

    print("Recording...")

    global recorded_frames
    for i in range(0, int(int(device_info["defaultSampleRate"]) / FRAMES * MAX_RECORD_SECONDS)):
        if (done_recording): 
            break
        if (len(recorded_frames) > int(int(device_info["defaultSampleRate"]) / FRAMES * record_seconds)):
            del recorded_frames[0]
        recorded_frames.append(stream.read(FRAMES))

    stream.stop_stream()
    stream.close()


def flush_frames():
    #filename = input("Save as [" + DEFAULT_FILE_NAME + "]: ") or DEFAULT_FILE_NAME

    wavefile = wave.open(DEFAULT_FILE_NAME, 'wb')
    wavefile.setnchannels(CHANNELS)
    wavefile.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wavefile.setframerate(int(device_info["defaultSampleRate"]))
    wavefile.writeframes(b''.join(recorded_frames))
    wavefile.close()


def print_wasapi_devices():
    for key in wasapi_devices:
        print(str(key) + ": " + wasapi_devices[key])


def play_audio(file_name):
    wf = wave.open(file_name, "rb")

    stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)
    
    data = wf.readframes(CHUNK)

    while not done and data != "":
        if(len(data) == 0):
            break
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.close()


def log_audio(file_name):
    audio_input = speechsdk.AudioConfig(filename=file_name)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    result = speech_recognizer.recognize_once_async().get()
    print(result.text)



if __name__ == "__main__":
    main()