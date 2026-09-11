# RPi Based Car Display
---
The project aims to develop an in-car mini-computer based on the Raspberry Pi platform. The device will connect to the vehicle via the OBD-II interface to read data transmitted over the CAN bus. Communication and data processing will be implemented in Python using the OBD library, which enables the retrieval of diagnostic information from the vehicle's onboard computer.


## Table of Contents
1. [Necessary devices](#1-necessary-devices)
2. [Raspberry Pi configuration](#2-raspberry-pi-configuration)
3. [Python script](#3-python-script)
4. [Raspberry Pi housing](#4-raspberry-pi-housing)
5. [Result](#5-final-result)

---

### 1. Necessary Devices

|Device|Name|Description|
|---|---|---|
|<img width="217" height="133" alt="image" src="https://github.com/user-attachments/assets/c6095634-1763-4c63-9a1b-ce9408a16871" />|Raspberry Pi 4B+|Main component. Receives and processes data from ELM, then displays them on screen|
|<img width="207" height="140" alt="image" src="https://github.com/user-attachments/assets/724cb51f-8fa6-4860-8925-afd21ae34953" />|ELM327 Mini|Device sniffing CAN Data. Sends it to RPi via Bluetooth|
|<img width="202" height="128" alt="image" src="https://github.com/user-attachments/assets/5e5fd2de-0fce-489a-81b6-b8361e6b9b21" />|Waveshare 16239|DSI Display connected to RPi|
|<img width="158" height="138" alt="image" src="https://github.com/user-attachments/assets/4efa36be-aae0-4c12-bed1-d9591971e135" />|USB-A -> USB-C Cable|Neccessary for powering RPi|
|<img width="144" height="154" alt="image" src="https://github.com/user-attachments/assets/ce26bdbf-8201-4010-b7fe-5c66907856f1" />|Car Charger|In this Case we are using Mojietu Music Blue C, but can be any other one that has current-carrying capacity more than 1.8A|

---

### 2. Raspberry Pi configuration
To start, You need to have Raspberry Pi OS installed on Raspberry Pi, if you don't have it - you can get it from the official site https://www.raspberrypi.com/software/
After You have the Raspberry Pi OS ready to go. We can start to configure it

#### Connecting the ELM327

Connect the ELM327 Mini into the car's OBD II port. On Raspberry Pi put into the terminal `bluetoothctl` and then run `scan on`.

You will see the list of Bluetooth devices nearby

<p align="center">
  <img width="414" height="274" alt="image" src="https://github.com/user-attachments/assets/007a5320-6165-461d-9300-9d57e8a97fa2" />
</p>

Search for the one that has the format `Device XX:XX:XX:XX:XX:XX OBD II`, and then pair it with raspberry pi using command `pair {MAC Address}` and then to set autoconnect go for `trust {MAC Address}`.

You can check if the device was paired successfully by putting `scan off` and then `paired devices`. This will display the list of the paired devices.

<p align="center">
  <img width="297" height="47" alt="image" src="https://github.com/user-attachments/assets/67f20ee9-19cd-4144-b181-3d800ef38be0" />
</p>

Then we need to map this device to a COM Port used by python script to get the data. To do this, open the file `/etc/rc.local` by text editor and put `rfcomm bind rfcomm99 {MAC Address}`.
You can use any port number but in this case we put 99 to be sure, that it will not interfere with any other COM Ports.

<p align="center">
  <img width="766" height="386" alt="image" src="https://github.com/user-attachments/assets/bdc1ebc0-47f6-4641-a682-bac6c73f604b" />
</p>

We will need also to edit the Bluetooth daemon initializer file located in `/etc/systemd/system/dbus-org.bluez.service`.

Add there those two lines 
`ExecStart=/usr/lib/bluetooth/bluetoothd –C` and 
`ExecStartPost=/usr/bin/sdptool add SP`.

<p align="center">
  <img width="452" height="294" alt="image" src="https://github.com/user-attachments/assets/9ac6b293-18a4-4479-b607-c6e9f293bbc8" />
</p>

First one enables Bluetooth to Virtual COM port mapping. Second one adds support for SPP for Bluetooth which allows to set the connection to a mapped COM Port

#### Putting the Script into autostart

To put the Script into an autostart simply paste the path to a script into the `/etc/rc.local` file with the `python` attached at the start. so for example `sudo python /home/pi/script.py`

---

### 3. Python Script
You can see the python script in repository. To run it you need 3 things
- Installed Python on Raspberry PI (it is installed by default)
- Installed libraries OBD for working with ELM327 and Pygame for GUI (if not installed run `python pip install {library name}`
- Installed fonts crossover and sport pulse demo (optional)

To install the fonts download the files from
- https://befonts.com/sport-pulse-font.html
- https://befonts.com/crossover.charmap
and copy them to `/usr/share/fonts`
You can also run `fc-cache -f -v` to refresh font cache

#### OBD Library

This library is working in ASync mode which is indicated by the `connection = obd.Async(fast=False)` in the script.
It automatically opens the OBD II device binded to rfcomm99.
And gets the 3 parameters

- Speed of the vehicle (SPEED)
- Coolant temperature (COOLANT_TEMP)
- Throttle Position (THROTTLE_POS)

These parameters are then displayed by the GUI created in PyGame library

#### PyGame

PyGame controls all 3 gauges visible on the screen.
First one is speed gauge

<p align="center">
  <img width="298" height="266" alt="image" src="https://github.com/user-attachments/assets/ec35088d-bc74-41b1-9c08-0ce856cf063c" />
</p>

It is a car speed gauge look-alike with the speed value in center and the red indicator showing the number in the more "analog" way.

Second one is Coolant Temperature gauge
It has 3 states it can be in.

- Green (temps lower than 100)

<p align="center">
  <img width="225" height="174" alt="image" src="https://github.com/user-attachments/assets/860e413e-1c5f-4033-8db8-1d412b376492" />
</p>

- Yellow (temps 100-115)

<p align="center">
  <img width="239" height="189" alt="image" src="https://github.com/user-attachments/assets/6e2b4088-c587-4431-98f3-35a9137ca60d" />
</p>

- Red (temps higher than 115)

<p align="center">
  <img width="242" height="185" alt="image" src="https://github.com/user-attachments/assets/8b0c829b-e21a-4730-9371-abdfc34feafc" />
</p>

It has a form of coolant reservoir with the temperature (in Celsius) displayed inside the reservoir.
The cool feature it has is also that the level of coolant inside reservoir is dynamic and dependent of the temperature 

Third one is Throttle position gauge which works the same as coolant position gauge but of course with different values
for example

<p align="center">
  <img width="144" height="198" alt="image" src="https://github.com/user-attachments/assets/7ee95c91-8ecf-4eb7-a25b-55950d716873" />
</p>

---

### 4. Raspberry Pi housing

for the housing you can use your own e.g. 3D Printed or any custom suitable for this waveshare display

I created one by myself because why not :)

The parts i need to combine i cut out of the wooden plywood of 4mm thick

<p align="center">
  <img width="625" height="343" alt="image" src="https://github.com/user-attachments/assets/2537fd74-1af0-4696-aa5b-a7b9168ed2f9" />
</p>
<p align="center">
  <img width="609" height="322" alt="image" src="https://github.com/user-attachments/assets/e29e2685-98f9-4827-9d1c-68a0cbd07934" />
</p>

Then used 2mm screws to mount the whole thing to a housing and the black paint to paint it to match more the dark interior of the car

---

### 5. Final result

After you have prepared everything you can connect everything together in the car (raspberry pi to a charger and charger to the socket, don't forget about ELM327 - connect it to a OBD port)
You should be able to see something like this (i used it in my 2009 Opel Astra)

<p align="center">
  <img width="870" height="530" alt="image" src="https://github.com/user-attachments/assets/68446153-7310-4ed4-a5ef-dffb8b8c92a9" />
</p>

