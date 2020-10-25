import threading
import azure.cognitiveservices.speech as speechsdk
import pyaudio, wave, os, datetime
import tkinter as tk
from tkinter import scrolledtext
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

#thread
amd : object

class Rib: 
    def __init__(self): 
        window = tttk.ThemedTk(theme='vista', background=True)
        window.title("Run It Back")
        #window.resizable(False, False)
        window.iconbitmap("rib.ico")

        window.rowconfigure(0, minsize=0, weight=1)
        window.columnconfigure(2, minsize=0, weight=1)

        self.txt_scrolltxt = scrolledtext.ScrolledText(window)
        self.txt_scrolltxt.grid(row=0, column=1, sticky = "nsew")
        self.txt_scrolltxt.tag_config("azure", foreground="blue")
        
        # inputs
        input_boxes = tk.ttk.Frame(window)
        tk.ttk.Label(input_boxes, text = "Input Device").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        tk.ttk.Label(input_boxes, text = "Output Device").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        tk.ttk.Label(input_boxes, text = "Playback Length").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        tk.ttk.Label(input_boxes, text = "Key Phrase").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        tk.ttk.Label(input_boxes, text = "Audio File Name").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        tk.ttk.Label(input_boxes, text = "Translation Logs").grid(row=5, column=0, sticky='w', padx=5, pady=2)
        input_boxes.grid(row=0, column=0, sticky='ns', pady=2)
        #tk.Label(window, text = "Audio File Name").grid(row = 5, column = 1, sticky = tk.W)

        self.audio_devices = {}
        self.input_devices = {}
        self.wasapi_devices = {}
        self.device_info = {}
        self.selected_device_name = tk.StringVar(window)
        self.selected_device_id = -1
        self.selected_input_device_name = tk.StringVar(window)
        self.selected_input_device_id = -1
        self.playback_len = tk.StringVar(window)
        self.key_phrase = tk.StringVar(window)
        self.is_translating = tk.StringVar(window)
        self.file_name = tk.StringVar(window)

        self.recorded_frames = []
        self.use_loopback = True
        self.is_done_recording = True
        self.is_running_it_back = False
        self.is_connected = False


        # get all wasapi supported devices and get all input devices
        for i in range(0, p.get_device_count()):
            device = p.get_device_info_by_index(i)
            self.audio_devices[i] = device["name"]
            if (device["name"].find("Microphone") != -1):
                self.input_devices[i] = device["name"]
            if (p.get_host_api_info_by_index(device["hostApi"])["name"] == "Windows WASAPI"):
                self.wasapi_devices[i] = device["name"]

        # get input device names
        input_devices_names = []
        for key in self.input_devices:
            device_info = p.get_device_info_by_index(key)
            input_devices_names.append(device_info["name"])

        device_names = []
        # get output device names
        for key in self.wasapi_devices:
            device_info = p.get_device_info_by_index(key)
            device_names.append(device_info["name"])

        # selected input device
        self.opm_indevices = tk.ttk.Combobox(input_boxes, values = input_devices_names)
        self.opm_indevices.set(input_devices_names[0])
        self.opm_indevices.grid(row=0, column=1, sticky='new', padx=5)
        # selected output device
        self.opm_devices = tk.ttk.Combobox(input_boxes, values = device_names)
        self.opm_devices.set(device_names[0])
        self.opm_devices.grid(row=1, column=1, sticky='new', padx=5)
        # playback len
        self.playback_len.set(10) # default value
        self.ent_playback_len = tk.ttk.Entry(input_boxes, textvariable = self.playback_len, justify = tk.RIGHT)
        self.ent_playback_len.grid(row=2, column=1, sticky='new', padx=5)
        # key phrase
        self.key_phrase.set("run it back") # default value
        self.ent_keyphrase = tk.ttk.Entry(input_boxes, textvariable = self.key_phrase, justify = tk.RIGHT)
        self.ent_keyphrase.grid(row=3, column=1, sticky='new', padx=5)
        # file name
        self.file_name.set(DEFAULT_FILE_NAME) # default value
        self.ent_filename = tk.ttk.Entry(input_boxes, textvariable = self.file_name, justify = tk.RIGHT)
        self.ent_filename.grid(row=4, column=1, sticky='new', padx=5)
        # is_translating
        self.is_translating = True
        self.opm_translation = tk.ttk.Combobox(input_boxes, values = ["Will translate", "Do not translate"], justify = tk.RIGHT)
        self.opm_translation.set("Do not translate")
        self.opm_translation.grid(row=5, column=1, sticky='new', padx=5)

        # start stop
        activate_frame = tk.LabelFrame(input_boxes)
        btn_start = tk.ttk.Button(input_boxes, text="Start", command=self.threadripper)
        btn_start.grid(row = 6, column = 1, sticky='ew', padx=4, pady=2)
        btn_stop = tk.ttk.Button(input_boxes, text="Stop", command=self.stop_azure)
        btn_stop.grid(row = 6, column = 0, sticky='ew', padx=4, pady=2)
        activate_frame.grid()

        window.mainloop() # Create an event loop 

    
    def threadripper(self):
        global amd
        if (self.is_done_recording and not self.is_running_it_back):
            amd = threading.Thread(target=self.start_azure)
            amd.start()
  

    def start_azure(self):
        if (self.is_done_recording):
            self.is_done_recording = False
            self.txt_scrolltxt.insert(tk.END, "Started Azure\n", "azure")
            print("Started Azure")
            #self.selected_input_device_id = self.
            print(p.get_host_api_info_by_index(self.get_selected_input_device_id(self.opm_indevices.get())))
            self.selected_device_id = self.get_selected_device_id(self.opm_devices.get())
            self.device_info = p.get_device_info_by_index(self.selected_device_id)

            is_input = self.device_info["maxInputChannels"] > 0
            is_wasapi = (p.get_host_api_info_by_index(self.device_info["hostApi"])["name"]).find("WASAPI") != -1
            if not is_input and is_wasapi:
                self.use_loopback = True
                self.txt_scrolltxt.insert(tk.END, "Selection is output. Using loopback mode\n")
                print("Selection is output. Using loopback mode")
            else:
                self.txt_scrolltxt.insert(tk.END, "Error: Selection is either input or does not support loopback mode\n<Tip: select an output device!>\n")
                print("Error: Selection is either input or does not support loopback mode\n<Tip: SELECT AN OUTPUT DEVICE!>")
                self.stop_azure()
                return

            #audio_config = AudioConfig(device_name=p.get_host_api_info_by_index())
            speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
            speech_recognizer.start_continuous_recognition()
            if not self.is_connected:
                speech_recognizer.recognized.connect(self.process_input)
                self.is_connected = True
            self.txt_scrolltxt.insert(tk.END, "SPEAK into your microphone or say STOP to terminate the program.\n")
            print("Speak into your microphone or say STOP to terminate the program.")
            self.record_device()


    def stop_azure(self):
        if (not self.is_done_recording and not self.is_running_it_back):
            self.txt_scrolltxt.insert(tk.END, "Stopped Azure\n", "azure")
            print("Stopped Azure\n")
            self.is_done_recording = True
            self.is_running_it_back = False
            speech_recognizer.stop_continuous_recognition()


    def record_device(self):
        stream = p.open(format = pyaudio.paInt16,
                        channels = CHANNELS,
                        rate = int(self.device_info["defaultSampleRate"]),
                        input = True,
                        frames_per_buffer = FRAMES,
                        input_device_index = self.device_info["index"],
                        as_loopback = True)

        self.txt_scrolltxt.insert(tk.END, "Listening...\n")
        print("Listening...")
        for _ in range(0, int(int(self.device_info["defaultSampleRate"]) / FRAMES * MAX_RECORD_SECONDS)):
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
            self.txt_scrolltxt.insert(tk.END, "Recognized: " + text + "\n")
            print("Recognized: " + text)

            if (text.find(self.ent_keyphrase.get()) != -1):
                self.is_running_it_back = True
                speech_recognizer.stop_continuous_recognition()
                self.txt_scrolltxt.insert(tk.END, "RUNNING IT BACK!\n")
                print("RUNNING IT BACK!")
                self.flush_frames()
                self.play_audio(self.ent_filename.get())
                if self.opm_translation.get() == "Will translate":
                    self.translate_audio(self.ent_filename.get())
                self.is_running_it_back = False
                speech_recognizer.start_continuous_recognition()
            elif (text.find("stop") != -1):
                self.stop_azure()


    def translate_audio(self, file_name):
        audio_input = speechsdk.AudioConfig(filename=file_name)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

        result = speech_recognizer.recognize_once_async().get()
        self.txt_scrolltxt.insert(tk.END, "[%s]\nTRANSLATION: %s\n" % (datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"), result.text))
        print(result.text)


    def flush_frames(self):
        self.txt_scrolltxt.insert(tk.END, "Flushing frames...\n")
        print("Flushing frames...")
        #filename = input("Save as [" + DEFAULT_FILE_NAME + "]: ") or DEFAULT_FILE_NAME

        wavefile = wave.open(self.ent_filename.get(), 'wb')
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


    def get_selected_input_device_id(self, device_name):
        for key in self.input_devices:
            device_info = p.get_device_info_by_index(key)
            if (device_info["name"] == device_name):
                return key


    def get_selected_device_id(self, device_name):
        for key in self.wasapi_devices:
            device_info = p.get_device_info_by_index(key)
            if (device_info["name"] == device_name):
                return key
                
  
# launch
Rib() 