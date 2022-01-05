# JPxG, 2021 December 29
# I'm going to try various things from the Internet that claim to accept input.

#import keyboard
#while True:
#	dog = keyboard.read_event(suppress=False)
#	print(dog)

# Notes on "keyboard": It seems very cool: reads keyboard events even if focused elsewhere.
# Also, it can also emit them. However, I need to run it as root (wtf) and the documentation is abysmally shit.
# Anyway, it doesn't do anything for my mouse or joystick, so I am relegating it to idle curiosity.

import hid
# This needs to be run as root to work.
#from pynput import keyboard
#from pynput.keyboard import Key
import keyboard
# This needs to be run as root to work.
import time

import os
#from playsound import playsound

import threading
# Needed for non-blocking audio file play

import toml
# Needed to read config files

verbose = 0

def parseReport(report):
	#print(report)
	# 0 = left-to-right (increasing to right)
	# 1 = towards-to-away (increasing to towards)
	# 2 = hat button on top, also encodes rollover for [1]
	# 3 = twist (far CCW is 0, far CW is 255)
	# 4 = buttons 1 (trigger) through 8
	# 5 = paddle (0 = top "+", 255 = bottom "-")
	# 6 = buttons 9 through 12
	stick = {	"x": 0,
				"y": 0,
				"z": 0,
				"t": 0,
				"hx": 0,
				"hy": 0,
				"b": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
			}
	# x (left to right), y (towards to away), z (left to right), t (down to up)
	# x and y go from 0 to 1023, z and t go from 0 to 255
	# hx and hy are either -1, 0 or 1
	# buttons are all either 0 or 1
	##### Now we will decode the raw output from the controller into values.
	yroll = report[2] % 16
	xroll = report[1] % 4
	# yes, they really encoded the rollover from the x pitch into the y pitch, an ADC readout whose rollover is itself encoded into the hat switch readout
	# even though they had a completely unused four bits in the encoding for the seventh position
	# lmao

	stick['x'] = (xroll * 256) + report[0]
	stick['y'] = (yroll * 64) + ((report[1] - xroll) // 4)
	#print(report[2] % 16)
	stick['z'] = report[3]
	stick['t'] = (255 - report[5])
	# Now to decode the hat button.
	h = (report[2] - yroll) // 16		
	#     0
	#  7     1
	#           
	# 6   8   2
	#             
	#  5     3
	#     4
	#print(h)
	stick['hy'] += (h==0)+(h==1)+(h==7)
	stick['hy'] -= (h==3)+(h==4)+(h==5)
	if (h % 4 != 0):
		stick['hx'] = (h < 4) - (h > 4) 
		# Hint: a bool is either "1" or "0" and can have math done to it.
	# Now to decode the bitfield for buttons 1-8.
	stick['b'] = [((report[4] >> n) & 1) for n in range(8)]
	# Bit shift it by n, and store bool as ['b'][n], for n in 0-7
	# Decode bitfield for buttons 9 - 12.
	stick['b'] += [((report[6] >> n) & 1) for n in range(4)]
	# Bit shift it by n, and store bool as ['b'][7+n], for n in 0-3

	return(stick)

def makeDebugString(stick):
	string = ""
	for item in stick:
		string += str(item)
		string += ":"
		if (item == 'x') or (item == 'y'):
			string += str(stick[item]).zfill(4)
		if (item == 'z') or (item == 't'):
			string += str(stick[item]).zfill(3)
		if (item == 'hx') or (item == 'hy'):
			string += str(stick[item]).zfill(2)
		if (item == 'b'):
			string += str(stick[item])
		string += " | "
	return string

def playWav(file):
	os.system("sudo -u x XDG_RUNTIME_DIR=/run/user/1000 paplay " + file + "&")

print("Joystuck 0.1 -- JPxG, 2021 December 30")

print("Attempting to load configuration data.")
cfgPath = "cfg"
cfg = []
for filename in os.listdir(cfgPath):
	if (filename != "template.toml"):
		file = open(str(cfgPath + "/" + filename))
		text = file.read()
		toml = toml.loads(text)
		cfg.append(toml)
for i in cfg:
	print(">   " + i['metadata']['title'])


print("Attempting to open device.")

for device in hid.enumerate():
	print(device)
	print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x}")

inputDevice = hid.device()
inputDevice.open(0x046D, 0xC215)
#inputDevice.open(0xC215, 0x046D)
# This is the vendor ID and product ID for the device.
print("Device opened, with vendor ID 0x046D and product ID 0xC215.")
inputDevice.set_nonblocking(True)

# Set up debug for y-roll
#values = [0 for n in range(4100)]


# The following thing sets up an infinite loop to read input from the stick. Not ideal.

cooldown = 0

defaultBindings = [
	"enter",
	"ctrl+w",
	"",
	"",
	"ctrl+page up",
	"ctrl+page down",
	"",
	"",
	"",
	"",
	"",
	""]

defaultZ = ["shift+tab", "tab"]

defaultSounds = [
	"/home/x/2k2k/sound/twispark-15ai-b1.wav",
	"/home/x/2k2k/sound/twispark-15ai-2.wav",
	"/home/x/2k2k/sound/twispark-15ai-3.wav",
	"/home/x/2k2k/sound/twispark-15ai-4.wav",
	"/home/x/2k2k/sound/twispark-15ai-5.wav",
	"/home/x/2k2k/sound/twispark-15ai-6.wav",
	"/home/x/2k2k/sound/twispark-15ai-7.wav",
	"/home/x/2k2k/sound/twispark-15ai-8.wav",
	"/home/x/2k2k/sound/twispark-15ai-9.wav",
	"/home/x/2k2k/sound/twispark-15ai-10.wav",
	"/home/x/2k2k/sound/twispark-15ai-11.wav",
	"/home/x/2k2k/sound/twispark-15ai-toggling.wav"]

huggleBindings = [
	"tab",
	"o",
	"q",
	"9",
	"z",
	"4",
	"`",
	"w",
	"r",
	"enter",
	"c",
	""]

huggleZ = ["up", "down"]


huggleSounds = [
	"/home/x/2k2k/sound/saw-220-1s-08-taperafter01.wav",
	"/home/x/2k2k/sound/saw-440-1s-08-taperafter01.wav",
	"/home/x/2k2k/sound/saw-494-1s-08-taperafter01.wav",
	"/home/x/2k2k/sound/saw-523-1s-08-taperafter01.wav",
	"/home/x/2k2k/sound/saw-587-1s-08-taperafter01.wav",
	"/home/x/2k2k/sound/saw-659-1s-08-taperafter01.wav",
	"/home/x/2k2k/sound/saw-698-1s-08-taperafter01.wav",
	"/home/x/2k2k/sound/saw-783-1s-08-taperafter01.wav",
	"/home/x/2k2k/sound/saw-880-1s-08-taperafter01.wav",
	"",
	"",
	""]

huggleSounds = [
	"/home/x/2k2k/sound/glados-revisionpassed.wav",
	"/home/x/2k2k/sound/glados-editopenedinbrowser.wav",
	"/home/x/2k2k/sound/glados-revertedandwarned.wav",
	"/home/x/2k2k/sound/glados-unexplaineddeletionrv.wav",
	"/home/x/2k2k/sound/glados-unsourcedrevert.wav",
	"/home/x/2k2k/sound/glados-mosviolation.wav",
	"/home/x/2k2k/sound/glados-promotionalwarning.wav",
	"/home/x/2k2k/sound/glados-nonconstructivewarning.wav",
	"/home/x/2k2k/sound/glados-onlyreverting.wav",
	"/home/x/2k2k/sound/glados-confirmingdialogue.wav",
	"/home/x/2k2k/sound/glados-contribs.wav",
	"/home/x/2k2k/sound/glados-toggling.wav",
]

# Trigger: tab (next edit)
# B2 :		o (open edit in browser)
# B3 :		q (revert+warn)
# B4 :		9 (unexplained deletion)
# B5 :	 	z (no verifiable reliable source)
# B6 :		4 (mos)
# B7 :		` (warn for spam)
# B8 :		w (warn non-constructive)
# B9 :		r (revert with no warning)
# B10:		enter (enter)
# B11:		c (open user contributions)
# B12:	 	Toggle
# H-left:	[
# H-right: 	]

toggle = 0

sounds = [defaultSounds, huggleSounds]
bindings = [defaultBindings, huggleBindings]
z = [defaultZ, huggleZ]

cooldown = 255

while True:
	#report = inputDevice.read(64)
	# Works with 64
	report = inputDevice.read(256)
	cooldown -= 0.001
	if report:
		stick = parseReport(report)
		if verbose: print(makeDebugString(stick), cooldown)
		cooldownMax = 255 - stick['t']
		# Extremely baroque way to parse x/y joystick input for scrolling.
		"""
		midpoint = 512
		intervals = 16
		goby = midpoint / intervals
		directions = [0, 0, 0, 0]
		for amount in range(1, intervals):
			if stick['x'] < (midpoint - (goby * amount)):
				directions[0] += 1
			if stick['x'] > (midpoint + (goby * amount)):
				directions[1] += 1
			if stick['y'] < (midpoint - (goby * amount)):
				directions[2] += 1
			if stick['y'] > (midpoint + (goby * amount)):
				directions[3] += 1
		damping = 4
		for a, b in enumerate(["left", "right", "up", "down"]):
			#print(a, b)
			directions[a] = directions[a] // damping
			for c in range(directions[a]):
				if cooldown < 0:
					cooldown = cooldownMax
					keyboard.send(b)
		"""
		# Slightly less baroque way.

		midpoint = cfg[toggle]
		damping = 32
		# We'll send an additional keystroke for every __ positions away from the middle.

		dirX = (stick['x'] - midpoint) // damping
		dirY = (stick['y'] - midpoint) // damping
		#print (dirX, dirY)

		directions = [0, 0, 0, 0]
		#------------ l  r  u  d
		if (stick['x'] < midpoint):
			directions[0] = (midpoint - stick['x']) // damping
		if (stick['x'] > midpoint):
			directions[1] = (stick['x'] - midpoint) // damping
		if (stick['y']  < midpoint):
			directions[2] = (midpoint - stick['y']) // damping
		if (stick['y']  > midpoint):
			directions[3] = (stick['y'] - midpoint) // damping
		#print(directions)

		if cooldown < 0:
			for a, b in enumerate(["left", "right", "up", "down"]):
				for c in range(directions[a]):
					keyboard.send(b)
					cooldown = cooldownMax


		# Implement Z axis.

		midpointz = 128
		dampingz = 8

		directionsz = [0, 0]
		#------------ l  r

		if (stick['z'] < midpointz):
			directionsz[0] = (midpointz - stick['z']) // dampingz
		if (stick['z'] > midpointz):
			directionsz[1] = (stick['z'] - midpointz) // dampingz

		if cooldown < 0:
			for a, b in enumerate(z[toggle]):
				for c in range(directionsz[a]):
					keyboard.send(b)
					cooldown = cooldownMax

		# Baroque way for Z.
		midpoint = 127
		intervals = 16
		goby = midpoint / intervals
		directions = [0, 0]
		for amount in range(1, intervals):
			if stick['z'] < (midpoint - (goby * amount)):
				directions[0] += 1
			if stick['z'] > (midpoint + (goby * amount)):
				directions[1] += 1
		damping = 16
		for a, b in enumerate(["shift+tab", "tab"]):
			#print(a, b)
			#print(directions[a])
			directions[a] = directions[a] // damping
			for c in range(directions[a]):
				if cooldown < 0:
					cooldown = cooldownMax
					keyboard.send(b)



		if (stick['hx'] == -1) and (pstick['hx'] != -1):
			pass
			keyboard.send("[")
		if (stick['hx'] == 1) and (pstick['hx']!= 1):
			pass
			keyboard.send("]")

		try:
			pstick
		except NameError:
			pstick = stick

		for a, b in enumerate(bindings[toggle]):
			if (stick['b'][a] == 1) and (pstick['b'][a] == 0):
				if (b != ""):
					keyboard.send(b)
		for a, b in enumerate(sounds[toggle]):
			if (stick['b'][a] == 1) and (pstick['b'][a] == 0):
				if (b != ""):
					print(b)
					#playsound(b)
					#os.system("paplay " + b)
					# Doesn't work as root.
					if __name__ == "__main__":
						threade = threading.Thread(target=playWav(b), daemon=True)
						threade.start()

		if (stick['b'][11] == 1) and (pstick['b'][11] == 0):
			toggle = ((toggle + 1) % len(bindings))
			print("Bindings toggled to ")
			# Increments toggle by 1, unless it is the length of the bindings list-of-lists, in which case it puts it back to zero.


		"""
		# Stupid, baroque way of doing this.
		if stick['b'][0] and (pstick['b'][0] == 0):
			#if cooldown < 0:
			#	cooldown = cooldownMax
			#	keyboard.send("enter")
			keyboard.send("enter")
		if stick['b'][1] and (pstick['b'][1] == 0):
			#if cooldown < 0:
			#	cooldown = cooldownMax
			#	keyboard.send("ctrl+w")
			keyboard.send("ctrl+w")
		if stick['b'][2] and (pstick['b'][2] == 0):
			pass
		if stick['b'][3] and (pstick['b'][3] == 0):
			pass
		if stick['b'][4] and (pstick['b'][4] == 0):
			#if cooldown < 0:
			#	cooldown = cooldownMax
			#	keyboard.send("ctrl+page up")
			keyboard.send("ctrl+page up")
		if stick['b'][5] and (pstick['b'][5] == 0):
			#if cooldown < 0:
			#	cooldown = cooldownMax
			#	keyboard.send("ctrl+page down")
			keyboard.send("ctrl+page down")
		if stick['b'][6] and (pstick['b'][6] == 0):
			pass
		if stick['b'][7] and (pstick['b'][7] == 0):
			pass
		if stick['b'][8] and (pstick['b'][8] == 0):
			pass
		if stick['b'][9] and (pstick['b'][9] == 0):
			pass
		if stick['b'][10] and i(ptick['b'][10] == 0):
			keyboard.send("f6")
			time.sleep(0.5)
			keyboard.write("https://www.youtube.com/watch?v=_-GaXa8tSBE", exact=True, delay=0.05)
			keyboard.send("enter")
			time.sleep(4)
			keyboard.send("space")
			keyboard.send("f")
			keyboard.send("f11")

		if stick['b'][11] and i(ptick['b'][11] == 0):
			pass
		"""
		pstick = stick

		#keyboard.write('asdf')

########## Now the part where we deal with other stuff?


print("Wowie zowie!")













########## When all is said and done, we need to close out the joystick handle.


inputDevice.close()


# Here is some thing that Johnny found. Does not work if sudoed.

"""

from pynput import mouse, keyboard
from pynput.keyboard import Key, Listener
from pynput.mouse import Listener, Button, Controller


def on_prass(key):
    print(f"{key} pressed")


def on_release(key):
    print(f"{key} release")
    if key == Key.esc:
        # Stop listener
        return False

##### Mouse stuff. 

def on_click(x, y, button, pressed):
    print(f"{button}")


def on_unclick(button):
	print(f"{button} release")

def on_mouve(x, y):
	print(f"Moved to {x}, {y}")

# Collect events until released
#with keyboard.Listener(on_press=on_prass, on_release=on_release) as listener:
#    listener.join()

#with mouse.Listener(on_press=on_click, on_move=on_mouve) as mauslistener:
#	mauslistener.join()

keyListen = keyboard.Listener(on_press=on_prass, on_release=on_release)
keyListen.start()

mouseListen = mouse.Listener(on_click=on_click, on_move=on_mouve)
mouseListen.start()

while True:
	pass

	"""