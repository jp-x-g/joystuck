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

from random import randrange
# Needed to select sound files from lists

from datetime import datetime
# Needed for typing out warning messages (sad).

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

def TypeWarning():
	#keyboard.send("m")
	#time.sleep(1)
	datestring = str(datetime.now().strftime("%B %Y")).lower()
	keyboard.press("shift")
	for char in datestring:
		keyboard.send(char)
		keyboard.release("shift")
		time.sleep(0.03)
	#keyboard.write(datestring, exact=1, delay=0.05)
	#os.system("echo '" + datestring + "'|xclip")
	#keyboard.send("ctrl+v")
	#os.system("echo '{{subst:uw-spam4}} ~~~~'|xclip")
	keyboard.send("tab")
	time.sleep(0.2)
	keyboard.send("ctrl+a")
	time.sleep(0.2)
	keyboard.send("ctrl+v")
	print("Clipboard contents pasted to page.")

print("Joystuck 0.1 -- JPxG, 2021 December 30")

print("Loading enabled configurations:")
cfgPath = "cfg"
sndPath = "snd"
cfg = []
for filename in os.listdir(cfgPath):
	if (filename != "template.toml"):
		file = open(str(cfgPath + "/" + filename))
		text = file.read()
		thistoml = toml.loads(text)
		if (thistoml['metadata']['enabled'] == 'yes'):
			cfg.append(thistoml)
for i in cfg:
	print(">   " + i['metadata']['title'])
#print(cfg)
toggle = 0
soundToggle = 0
bindings = [cfg[toggle]['buttons'][str(x)] for x in range(1,13)]


allInputs = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
			"hatu", "hatd", "hatl", "hatr", "hatul", "hatur", "hatdl", "hatdr",
			"xminus", "xplus", "yminus", "yplus", "zminus", "zplus"]

sounds = {}
emptySounds = {}

for c in allInputs:
	emptySounds[c] = ""

cfg[toggle]['sounds']['0'] = emptySounds

toggleSoundIsBound = 0
if (cfg[toggle]['metadata']['sounds'] == "on"):
	for c in cfg[toggle]['buttons']:
		if cfg[toggle]['buttons'][c] == "togglesound":
			toggleSoundIsBound = 1
			# Check if there's a key set to toggle sound.
if (toggleSoundIsBound == 1) or (cfg[toggle]['metadata']['sounds'] == "off"):
	# If there's a "toggle sound" bind, OR if sounds are disabled for this cfg.
	sounds = emptySounds
else:
	sounds = cfg[toggle]['sounds']['1']

print(bindings)

# Set up sounds for initial configuration file.


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

		midpoint = 512
		dampingx = int(cfg[toggle]['axes']['xdamp'])
		dampingy = int(cfg[toggle]['axes']['ydamp'])
		# We'll send an additional keystroke for every __ positions away from the middle.

		dirX = (stick['x'] - midpoint) // dampingx
		dirY = (stick['y'] - midpoint) // dampingy
		#print (dirX, dirY)

		directions = [0, 0, 0, 0]
		#------------ l  r  u  d
		if (stick['x'] < midpoint):
			directions[0] = (midpoint - stick['x']) // dampingx
		if (stick['x'] > midpoint):
			directions[1] = (stick['x'] - midpoint) // dampingx
		if (stick['y']  < midpoint):
			directions[2] = (midpoint - stick['y']) // dampingy
		if (stick['y']  > midpoint):
			directions[3] = (stick['y'] - midpoint) // dampingy
		#print(directions)

		# For example, if X and Y are positive, you might get:
		# [0, 0, 5, 8]
		# If they're both neutral:
		# [0, 0, 0, 0]
		# If X is all the way left, damping is 8, and Y is neutral:
		# [64, 0, 0, 0]
		# i.e. "send the X-minus hotkey 64 times, do nothing else".

		if cooldown < 0:
			# Old: ["left", "right", "up", "down"]
			for a, b in enumerate([cfg[toggle]['axes']['xminus'], cfg[toggle]['axes']['xplus'], cfg[toggle]['axes']['yminus'], cfg[toggle]['axes']['yplus']]):
				if (b != ""):
					for c in range(directions[a]):
						keyboard.send(b)
						cooldown = cooldownMax


		# Implement Z axis.

		midpointz = 128
		dampingz = int(cfg[toggle]['axes']['zdamp'])

		directionsz = [0, 0]
		#------------- l  r

		if (stick['z'] < midpointz):
			directionsz[0] = (midpointz - stick['z']) // dampingz
		if (stick['z'] > midpointz):
			directionsz[1] = (stick['z'] - midpointz) // dampingz

		# For example, if Z is below the midpoint, you might get [10, 0],
		# if Z is above, [0, 5], and if Z is neutral, [0, 0].

		if cooldown < 0:
			for a, b in enumerate([cfg[toggle]['axes']['zminus'], cfg[toggle]['axes']['zplus']]):
				for c in range(directionsz[a]):
					keyboard.send(b)
					cooldown = cooldownMax

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

		# Parse all of the bindings for button presses.
		for a, b in enumerate(bindings):
			if (stick['b'][a] == 1) and (pstick['b'][a] == 0):
				# If button is pressed, but wasn't last cycle
				if (b == "toggle"):
					toggle = ((toggle + 1) % len(cfg))
					# Increments toggle by 1, unless it is the length of the
					# number of bindings, in which case it puts it back to zero
					bindings = [cfg[toggle]['buttons'][str(x)] for x in range(1,13)]
					print("Bindings toggled to " + cfg[toggle]['metadata']['title'])
					# Now we set the default sounds.
					cfg[toggle]['sounds']['0'] = emptySounds
					toggleSoundIsBound = 0
					for c in cfg[toggle]['buttons']:
						if cfg[toggle]['buttons'][c] == "togglesound":
							toggleSoundIsBound = 1
							# Check if there's a key set to toggle sound.
					if (cfg[toggle]['metadata']['sounds'] == "off") or (toggleSoundIsBound == 1):
						# If sounds are disabled, OR if there's a toggle sound hotkey bound.
						for c in allInputs:		
							sounds[c] = ""
					else:
						sounds = cfg[toggle]['sounds']['1']
				elif (b == "togglesound"):
					print(cfg[toggle]['sounds'])
					print(len(cfg[toggle]['sounds']))
					soundToggle = ((soundToggle + 1) % len(cfg[toggle]['sounds']))
					sounds = cfg[toggle]['sounds'][str(soundToggle)]
				elif (b != ""):
					if (b[:8] == "function"):
						#print(b)
						#print(b[9:])
						locals()[b[9:]]()
					# Allows you to define a function call,
					# if you put "function xyz" as the hotkey.
					else:
						keyboard.send(b)
		#print(sounds)
		#print(stick)
		for a in range(1, 12):
			if (stick['b'][a - 1] == 1) and (pstick['b'][a - 1] == 0):
				# If button is pressed, but wasn't last cycle
				sound = sounds[str(a)]
				if (sound != ""):
					#print(type(sound))
					if (type(sound) is list):
						# If it's a list, select an element randomly.
						sound = sound[randrange(len(sound))]
					if (sounds['path'] == 'relative'):
						sound = sndPath + "/" + sound
					if __name__ == "__main__":
						# Once we have a sound, start a thread to play it.
						print("Sound ", sound)
						threade = threading.Thread(target=playWav(sound), daemon=True)
						threade.start()

		pstick = stick
########## Now the part where we deal with other stuff?


print("Wowie zowie!")

########## When all is said and done, we need to close out the joystick handle.


inputDevice.close()
