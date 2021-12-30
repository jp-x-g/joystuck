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

for device in hid.enumerate():
	print(device)
	print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x}")

j = hid.device()
j.open(0x046D, 0x215)
j.set_nonblocking(True)




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

"""
 The joystick is 046d:c215 Logitech, Inc. Extreme 3D Pro
 {'path': b'5-4:1.0', 'vendor_id': 1133, 'product_id': 49685, 'serial_number': '', 'release_number': 22289, 'manufacturer_string': '', 'product_string': '', 'usage_page': 0, 'usage': 0, 'interface_number': 0}



 sudo cat /dev/hidraw2 = my mouse
 sudo cat /dev/hidraw4 = my kezboard


 sudo cat /sys/kernel/debug/usb/devices
 returns this:

 T:  Bus=05 Lev=01 Prnt=01 Port=03 Cnt=02 Dev#= 16 Spd=12   MxCh= 0
 D:  Ver= 2.00 Cls=00(>ifc ) Sub=00 Prot=00 MxPS= 8 #Cfgs=  1
 P:  Vendor=046d ProdID=c215 Rev=57.11
 S:  Manufacturer=Logitech
 S:  Product=Extreme 3D pro
 S:  SerialNumber=00000000002A
 C:* #Ifs= 1 Cfg#= 1 Atr=80 MxPwr=100mA
 I:* If#= 0 Alt= 0 #EPs= 1 Cls=03(HID  ) Sub=01 Prot=00 Driver=(none)
 E:  Ad=81(I) Atr=03(Int.) MxPS=   7 Ivl=1ms

https://askubuntu.com/questions/15570/configure-udev-to-change-permissions-on-usb-hid-device

Normally, this is done by adding to /etc/udev/rules.d a file maybe named 50-usb-scale.conf with contents like this:
SUBSYSTEM=="usb", ATTR{idVendor}=="HEX1", ATTR{idProduct}=="HEX2", MODE="0666"
Where HEX1 and HEX2 are replaced with the vendor and product id respectively.
To match on the Interface type instead, you could try replacing ATTR{idVendor}=="HEX1", ATTR{idProduct}=="HEX2" with a match for bInterfaceClass being 03 (HID):
SUBSYSTEM=="usb", ATTR{bInterfaceClass}=="03", MODE="0666"
But be warned, that will catch mice and keyboards too.

In my case:
	sudo nano /etc/udev/rules.d/2021-12-29-joystick.conf
	SUBSYSTEM=="usb", ATTR{idVendor}=="046D", ATTR{idProduct}=="C215", MODE="0666"

Nothing. Tried changing to
	SUBSYSTEM=="usb", ATTR{idVendor}=="046D", ATTR{idProduct}=="C215", MODE="0666"

Now moving it to /etc/udev/rules.d/2021-12-29-joystick.rules

Same fucking error. 

	python3: io.c:2115: handle_events: Assertion `ctx->pollfds_cnt >= internal_nfds' failed.



Diagnostic:
	udevadm info --attribute-walk /dev/bus/usb/008/023



Okay, so: trying to open 0xC215, 0x046D (the reverse order) gives me a different error: "OSError: open failed".
This means that I have them the right way around and it really is kinda-sorta succeeding at accessing the device.

Oh my GOD. I literally had to just add "j.close()" after the damn thing. Everything was actually completely fine.



[0, 2, 136, 127, 0, 0, 0]

 0  1  2    3    4  5  6

First three are bizarre.


0: Left-to-right (increasing to right, rolls over several times, seems to have nothing as an incrementor)
	Looks almost like it's incremented by [1] (0 on the left, 3 on the right), but this makes no sense.
1: Towards-to-away (increasing to towards, rolls over several times
	Incremented by [2] from 128 to 143.
2: C-stick in center, but also looks like it does some incrementing with [1]. When towards-to-away is neutral:
	N	136
	<	104
	<^	120
	^	8
	^>	24
	>	40
	>v	56
	v	72
	v<	88
	(they go up by 16 each time)



3: Twist (far CCW = 0, far CW = 255)
4: Buttons 1 through 8
	(1 = 1, 2 = 2, 3 = 4, 4 = 8 [...] 8 = 128)
5: Paddle (0 = top "+", 255 = bottom "-")
6: Buttons 8 - 12

6: Buttons 2




1    1    1    1    1    1    1    1    
128  64   32   16   8    4    2    1



"""


