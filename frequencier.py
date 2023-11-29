#2021 December 29
# All this does is make a dict of all the keys you press when the script runs, and how often you press them.
# This can assist in coming up with a control scheme!

#import keyboard
#while True:
#	dog = keyboard.read_event(suppress=False)
#	print(dog)

# Notes on "keyboard": It seems very cool: reads keyboard events even if focused elsewhere.
# Also, it can also emit them. However, I need to run it as root (wtf) and the documentation is abysmally shit.
# Anyway, it doesn't do anything for my mouse or joystick, so I am relegating it to idle curiosity.

import hid
#from pynput import keyboard
#from pynput.keyboard import Key
import keyboard
import time

presses = {}
"""
while True:
	press = str(keyboard.read_event())
	if (press[-5:] != "down)"):
		press = press.replace("KeyboardEvent(","").replace(" up)", "")
		print(press)
		if press in presses:
			presses[press] += 1
		else:
			presses[press] = 1
		print(presses)
		"""