import threading
import azure.cognitiveservices.speech as speechsdk
import pyaudio, wave, os, time
import tkinter as tk
from ttkthemes import themed_tk as tttk

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
MAX_RECORD_SECONDS = 1800

#threadd
amd : object

class Rib: 
    def __init__(self): 
        window = tttk.ThemedTk(theme='vista', background=True)
        window.title("Run It Back")
        window.resizable(False, False)

        tk.ttk.Label(window, text = "Output Device").grid(row = 1, column = 1, sticky = tk.W, padx=5, pady=2)
        tk.ttk.Label(window, text = "Playback Length (seconds)").grid(row = 2, column = 1, sticky = tk.W, padx=5, pady=2)
        tk.ttk.Label(window, text = "Key Phrase").grid(row = 3, column = 1, sticky = tk.W, padx=5, pady=2)
        tk.ttk.Label(window, text = "Audio File Name").grid(row = 4, column = 1, sticky = tk.W, padx=5, pady=2)
        #tk.Label(window, text = "Audio File Name").grid(row = 5, column = 1, sticky = tk.W) 


        self.audio_devices = {}
        self.wasapi_devices = {}
        self.device_info = {}
        self.selected_device_name = tk.StringVar(window)
        self.selected_device_id = -1
        self.playback_len = tk.StringVar(window)
        self.key_phrase = tk.StringVar(window)
        self.logs_enabled = tk.StringVar(window)
        self.file_name = tk.StringVar(window)

        self.recorded_frames = []
        self.use_loopback = True
        self.is_done_recording = True
        self.is_running_it_back = False

        # get all wasapi supported devices
        for i in range(0, p.get_device_count()):
            device = p.get_device_info_by_index(i)
            self.audio_devices[i] = device["name"]
            if (p.get_host_api_info_by_index(device["hostApi"])["name"] == "Windows WASAPI"):
                self.wasapi_devices[i] = device["name"]

        device_names = []
        # get device names and set default to wasapi speakers
        for key in self.wasapi_devices:
            device_info = p.get_device_info_by_index(key)
            device_names.append(device_info["name"])
            if (device_info["maxOutputChannels"] > 0):
                self.selected_device_name.set(device_info["name"])

        # selected device
        opm_devices = tk.ttk.Combobox(window, values=device_names)
        opm_devices.grid(row = 1, column = 2, padx=5, pady=2)
        # playback len
        self.playback_len.set(10) # default value
        ent_playback_len = tk.ttk.Entry(window, textvariable = self.playback_len, justify = tk.RIGHT)
        ent_playback_len.grid(row = 2, column = 2)
        # key phrase
        self.key_phrase.set("run it back") # default value
        ent_playback_len = tk.ttk.Entry(window, textvariable = self.key_phrase, justify = tk.RIGHT)
        ent_playback_len.grid(row = 3, column = 2)
        # file name
        self.file_name.set("out") # default value
        ent_playback_len = tk.ttk.Entry(window, textvariable = self.file_name, justify = tk.RIGHT)
        ent_playback_len.grid(row = 4, column = 2)

        # fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
        # fr_buttons.pack()

        tk.ttk.Button(window, text="Start", command=self.threadripper).grid(row = 6, column = 2, pady=2)
        tk.ttk.Button(window, text="Stop", command=self.stop_azure).grid(row = 6, column = 1, pady=2)


        window.mainloop() # Create an event loop 

    
    def threadripper(self):
        global amd
        if (self.is_done_recording):
            amd = threading.Thread(target=self.start_azure)
            amd.start()
  

    def start_azure(self):
        if (self.is_done_recording):
            self.is_done_recording = False
            print("Starting Azure...")
            self.selected_device_id = self.get_selected_device_id(self.selected_device_name.get())
            self.device_info = p.get_device_info_by_index(self.selected_device_id)

            is_input = self.device_info["maxInputChannels"] > 0 and (self.device_info["name"]).find("Microphone") != -1
            print("IS INPUT: " + str(is_input))
            is_wasapi = (p.get_host_api_info_by_index(self.device_info["hostApi"])["name"]).find("WASAPI") != -1
            if not is_input and is_wasapi:
                self.use_loopback = True
                print("Selection is output. Using loopback mode")
            else:
                print("Error: Selection is either input or does not support loopback mode\n<Tip: select an output device!>")
                self.stop_azure()
                return

            speech_recognizer.recognized.connect(self.process_input)
            speech_recognizer.start_continuous_recognition()
            print("Speak into your microphone or say STOP to terminate the program.")
            self.record_device()


    def stop_azure(self):
        if (not self.is_done_recording and not self.is_running_it_back):
            print("Stopping Azure...")
            self.is_done_recording = True
            speech_recognizer.stop_continuous_recognition()


    def record_device(self):
        stream = p.open(format = pyaudio.paInt16,
                        channels = CHANNELS,
                        rate = int(self.device_info["defaultSampleRate"]),
                        input = True,
                        frames_per_buffer = FRAMES,
                        input_device_index = self.device_info["index"],
                        as_loopback = True)

        print("Recording...")
        for i in range(0, int(int(self.device_info["defaultSampleRate"]) / FRAMES * MAX_RECORD_SECONDS)):
            if (self.is_done_recording): 
                break
            if (len(self.recorded_frames) > int(int(self.device_info["defaultSampleRate"]) / FRAMES * int(self.playback_len.get()))):
                del self.recorded_frames[0]
            self.recorded_frames.append(stream.read(FRAMES))

        stream.stop_stream()
        stream.close()

    
    def process_input(self, evt):
        if not self.is_running_it_back and evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = evt.result.text.lower()
            if (len(text) <= 0):
                return
            print("Recognized: " + text)

            if (text.find(self.key_phrase.get()) != -1):
                self.is_running_it_back = True
                print("Running it back!")
                self.flush_frames()
                self.play_audio(DEFAULT_FILE_NAME)
            elif (text.find("stop") != -1):
                self.stop_azure()


    def flush_frames(self):
        print("Flushing frames...")
        #filename = input("Save as [" + DEFAULT_FILE_NAME + "]: ") or DEFAULT_FILE_NAME

        wavefile = wave.open(DEFAULT_FILE_NAME, 'wb')
        wavefile.setnchannels(CHANNELS)
        wavefile.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(int(self.device_info["defaultSampleRate"]))
        wavefile.writeframes(b''.join(self.recorded_frames))
        wavefile.close()


    def play_audio(self, file_name):
        wf = wave.open(file_name, "rb")

        stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)
        
        data = wf.readframes(CHUNK)

        while not self.is_done_recording and data != "":
            if(len(data) == 0):
                break
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.close()
        self.is_running_it_back = False


    def get_selected_device_id(self, device_name):
        for key in self.wasapi_devices:
            device_info = p.get_device_info_by_index(key)
            if (device_info["name"] == device_name):
                return key
  
# call the class to run the program. 
Rib() 