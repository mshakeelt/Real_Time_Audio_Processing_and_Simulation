import matplotlib.animation as animation
import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav
import pyaudio
import struct
from matplotlib.widgets import Button
from matplotlib import gridspec
import scipy.io.wavfile as wav
import scipy.signal as sig

CHUNK = 2048 #Blocksize
WIDTH = 2 #2 bytes per sample
CHANNELS = 1 #2
RATE = 32000  #Sampling Rate in Hz
frame = 0  # frame number of file
framenum = 0  # animation frame number
filternum = 0  # 0 = FIR, 1 = IIR

# read audio file
fs, data = wav.read("Track_32kh.wav")
data1 = data[:,0] 
data2 = data[:,1]
frame = np.floor(len(data1)/CHUNK)
print("Current Frame:",frame)

fig, (p1,p2) = plt.subplots(2,1)  # two subplots
fig.set_size_inches(6, 6, forward=True)   # window size
line1, = p1.plot([],[],lw=2)
line2, = p2.plot([],[],lw=2)

p1.set_xlim(0,np.pi)  # x axis range for spectrum
p2.set_xlim(0,np.pi)  


p1.grid(True)
p1.set_title('Original Signal')
p2.grid(True)
p2.set_title('Filtered and Downsampled Signal')
fig.subplots_adjust(hspace=.5)

# pyaudio setting
p = pyaudio.PyAudio()
#a = p.get_device_count()

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=False,
                output=True,
                frames_per_buffer=CHUNK)

# FIR Filter coeffecients
num1 = [0.3235,0.2665,0.2940,0.2655,0.3235]
def FIR_Filter(input_signal):
    filtered = sig.lfilter(num1, 1, input_signal)
    filtered = np.clip(filtered, -32000,32000)
    return filtered

# IIR Filter coeffecients
num2= [0.256,0.0512,0.256]
denum2 = [1.0,-1.3547,0.6125]
def IIR_Filter(input_signal):
    filtered = sig.lfilter(num2, denum2, input_signal)
    filtered = np.clip(filtered, -32000,32000)
    return filtered


#buttons
class Index(object):

    def play(self, event):  # recover and play
        print("Start Animation")
        ani.event_source.start()

    def stop(self, event):  # stop recording
        print("stop Animation")
        ani.event_source.stop()

    def IIRFILTER1(self, event):  # change filter
        global filternum
        if filternum == 0:
            filternum = 1
            print("Slected filter is IIR")
    
    def FIRFILTER1(self, event):  # change filter
        global filternum
        if filternum == 1:
            filternum = 0
            print("Slected filter is FIR")
   
   
   

# create frames for animation
def animate(i):
    #print("frame number",i)
    global framenum 
    framenum = i
    x = np.arange(CHUNK)  # x coordinate
    # read audio of length CHUNK
    samples = data1[CHUNK*i:CHUNK*(i+1)]
    
    w1,h1 = sig.freqz(samples)
    y1_max = np.max(h1)
    y1_min = np.min(h1)
    p1.set_ylim(-600000,600000) 
    line1.set_data(w1,h1)
    
    if filternum == 0 :
       filtered1 = FIR_Filter(samples)
    elif filternum==1 :
       filtered1 = IIR_Filter(samples)
    downsampled = np.zeros(CHUNK)
    downsampled[::4] = filtered1[::4]
    # spectrum of processed signal
    w2,h2 = sig.freqz(downsampled)   
    y2_max = np.max(h2)
    y2_min = np.min(h2)
    p2.set_ylim(-600000,600000)
    #line2.set_data(w2,h2)
    upsampled = np.zeros(CHUNK)
    upsampled[::4] = downsampled[::4]
    # filter 2
    if filternum == 0 :
       filtered2 = FIR_Filter(upsampled)
    elif filternum == 1 :
       filtered2 = IIR_Filter(upsampled)
    w3,h3 = sig.freqz(filtered2)
    line2.set_data(w3,h3)
    #print(filtered2)
    samples=np.clip(filtered2,-2**15,2**15-1)  # playback the reconstructed audio
    sound = (samples.astype(np.int16).tostring())
    stream.write(sound)
    return line1,line2,

def init():
    print("Starting Over")
    line1.set_data([],[]) 
    line2.set_data([],[]) 
    return line1,line2,

ani = animation.FuncAnimation(fig, animate, init_func = init, frames = int(frame) , interval=15, blit=True)

callback = Index()
axstop = plt.axes([0.2, 0.02, 0.1, 0.05])
axplay = plt.axes([0.4, 0.02, 0.1, 0.05])
#axchangeFilt = plt.axes([0.6, 0.02, 0.1, 0.05])
FIRFilt = plt.axes([0.6, 0.02, 0.1, 0.05])
IIRFilt = plt.axes([0.8, 0.02, 0.1, 0.05])
bplay = Button(axplay, 'play')
bplay.on_clicked(callback.play)
bstop = Button(axstop, 'stop')
bstop.on_clicked(callback.stop)
bFIRFilt = Button(FIRFilt, 'FIR filter')
bFIRFilt.on_clicked(callback.FIRFILTER1)

bIIRFilt = Button(IIRFilt, 'IIR filter')
bIIRFilt.on_clicked(callback.IIRFILTER1)

plt.show()

print("Exit")

stream.stop_stream()
stream.close()
p.terminate()
