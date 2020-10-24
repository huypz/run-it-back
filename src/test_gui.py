import azure.cognitiveservices.speech as speechsdk
import pyaudio, wave, os, time

import tkinter as tk

# pyaudio interface
p = pyaudio.PyAudio()


class Rib: 
    def __init__(self): 
        window = tk.Tk()
        window.title("Run It Back")

        tk.Label(window, text = "Output Device").grid(row = 1, column = 1, sticky = tk.W) 
        tk.Label(window, text = "Playback Length (seconds)").grid(row = 2, column = 1, sticky = tk.W) 
        tk.Label(window, text = "Key Phrase").grid(row = 3, column = 1, sticky = tk.W) 
        tk.Label(window, text = "Audio File Name").grid(row = 4, column = 1, sticky = tk.W) 
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
        opm_devices = tk.OptionMenu(window, self.selected_device_name, *device_names)
        opm_devices.grid(row = 1, column = 2) 
        # playback len
        self.playback_len.set(10) # default value
        ent_playback_len = tk.Entry(window, textvariable = self.playback_len, justify = tk.RIGHT)
        ent_playback_len.grid(row = 2, column = 2)
        # key phrase
        self.key_phrase.set("run it back") # default value
        ent_playback_len = tk.Entry(window, textvariable = self.key_phrase, justify = tk.RIGHT)
        ent_playback_len.grid(row = 3, column = 2)
        # file name
        self.file_name.set("out") # default value
        ent_playback_len = tk.Entry(window, textvariable = self.file_name, justify = tk.RIGHT)
        ent_playback_len.grid(row = 4, column = 2)

        # fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
        # fr_buttons.pack()
        btn_start = tk.Button(window, text="Start", command=self.start_azure).grid(row = 6, column = 2)
        btn_stop = tk.Button(window, text="Stop", command=self.stop_azure).grid(row = 6, column = 1)


        window.mainloop() # Create an event loop 
  
    def start_azure(self):
        pass


    def stop_azure(self):
        pass

    def get_selected_device_id(self, device_name):
        for key in self.wasapi_devices:
            device_info = p.get_device_info_by_index(key)
            if (device_info["name" == device_name]):
                return key
  
# call the class to run the program. 
Rib() 