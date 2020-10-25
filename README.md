# Run It Back
POG

## Inspiration
Due to the ongoing COVID-19 pandemic, students across the world have had to adjust to an online learning environment where it can be very easy to periodically 'blank out'. We wanted to make a program that lets students replay the last few moments of a lecture so they can follow what they missed, leaving no gaps in their notes.

## What it does
We created this multipurpose application that allows users to instantly replay audio from a certain length of time in the past and then translate it to a log file with timestamps. The GUI allows you to easily configure your audio devices and other settings, and the console displays the program's events and logs while allowing text editing.

## How we built it
We built it using Python and mainly its two libraries, PyAudio and Tkinter, for their flexibility with streaming audio and simple GUI creation, respectively. Microsoft Azure powered our speech-to-text functionality that brought the project together.

## Challenges we ran into
Most of our challenges arose from our inadequate understanding of the many modules required for what we intended to do. We were especially confused as to why PyAudio could not record speaker outputs, why the Tkinter GUI froze whenever voice recognition started, and which functions we needed from Microsoft Azure’s Speech to Text API.

## What we learned
Apparently, an API named WASAPI is needed for PyAudio to record speaker output using the loopback mode, and there exists a PyAudio fork specifically created to support WASAPI. We then learned how to develop a GUI using the Tkinter module. Another one of our discoveries was that we needed to run Azure’s Speech to Text code on a separate thread from the GUI to prevent the latter from locking up, requiring us to introduce Python’s threading module.

## What's next for Run It Back
_Run It Back_ would feature more customization like audio equalization, the ability to select specific instances of Windows to stream with, and the option to mute other audio sources during replay.
