# JPxG, 2021 December 29
# I'm going to try various things from the Internet that claim to accept input.

import keyboard
#while True:
#	dog = keyboard.read_event(suppress=False)
#	print(dog)

# Notes on "keyboard": It seems very cool: reads keyboard events even if focused elsewhere.
# Also, it can also emit them. However, I need to run it as root (wtf) and the documentation is abysmally shit.
# Anyway, it doesn't do anything for my mouse or joystick, so I am relegating it to idle curiosity.


import hid

print("Joystuck 0.1 -- JPxG, 2021 December 30")
print("Attempting to open device.")

for device in hid.enumerate():
	print(device)
	print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x}")

j = hid.device()
j.open(0x046D, 0xC215)
#j.open(0xC215, 0x046D)
# This is the vendor ID and product ID for the device.
print("Device opened, with vendor ID 0x046D and product ID 0xC215.")
j.set_nonblocking(True)

# Set up debug for y-roll
#values = [0 for n in range(4100)]

while True:
	#report = j.read(64)
	# Works with 64
	report = j.read(256)
	if report:
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
		# x and y go from 0 to max, z and t go from 0 to 255
		##### Now we will decode the raw output from the controller into values.

		yroll = report[2] % 16
		xroll = report[1] % 4
		# yes, they really encoded the rollover from the x pitch into the y pitch, an analog readout whose rollover is itself encoded into the hat switch readout.
		# even though they had a completely unused four bits in the encoding for the seventh position.
		# lmao.

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
			# Hint: a bool is either "1" or "0".

		# Now to decode the bitfield for buttons 1-8.

		stick['b'] = [((report[4] >> n) & 1) for n in range(8)]
		# Bit shift it by n, and store bool as ['b'][n], for n in 0-8

		# Decode bitfield for buttons 9 - 12.
		stick['b'] += [((report[6] >> n) & 1) for n in range(4)]

		"""
		# Debug (prints the contents of stick).
		string = ""
		for item in stick:
			string += " | "
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
			pass
		#print(string, bin(report[1]).zfill(10), report[1] % 4)
		#print(string, stick['y'], values[62], values[63], values[64], values[65])
		print(string)
		values[stick['y']] = 1

		if stick['b'][0] == 1:
			j.close()
		#	# If trigger is pulled, debug the shiznit.
		#	print(values)
		"""
		

########## Now the part where we deal with other stuff?


print("Wowie zowie!")













########## When all is said and done, we need to close out the joystick handle.


j.close()


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