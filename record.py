#!/usr/bin/python
import pyaudio
import wave

def start_audio(time = 3,save_file="test.wav"):
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 16000
	RECORD_SECONDS = time
	WAVE_OUTPUT_FILENAME = save_file

	p = pyaudio.PyAudio()
	print("ON")

	stream = p.open(format=FORMAT,
	                channels=CHANNELS,
	                rate=RATE,
	                input=True,
		                frames_per_buffer=CHUNK)
	frames = []

	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	    data = stream.read(CHUNK)
	    frames.append(data)

	print("OFF")

	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()

start_audio()

