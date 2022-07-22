# LiveLT

![LiveLT GUI](https://github.com/migillett/LiveLT/blob/main/LiveLT/assets/livelt_gui.png)

This Python script allows you to scan QRCodes and transmit them directly to a NewTek Tricaster via their DataLink feature. The script uses PyQt5 for the main GUI and opencv-python for capturing webcam input and QR decoding.

This program is meant to help with Graduation ceremonies. What you'd do is give every student a piece of paper with their name and their custom QR code on it. They walk up to the stage, scan the QR code, then give their piece of paper to the reader. Someone is off to the side running this application and sends the name over the network to the techncial director running the Tricaster. The TD will be the one in charge of putting the lower thirds on and off of program.

### Dependencies
This script requires Python 3.10 or higher. You'll need to install a few dependencies as well by running `pip3 install -r ./requirements.txt` once you've cloned the repo.

Also make sure it's running on a MacOS or Windows machine. I'm trying to get it to work on Linux, but haven't had any luck with my install of Pop_OS yet.

### How to Use
1. On your Tricaster, start up a live switching project and click on the globe in the top-right corner. Take note of your Tricaster's IP address and save that for later. I highly recommend giving your Tricaster a static IP address or reserving the DHCP address on your router. See your router's manual for more information on this.

2. Go to GFX 1 or GFX 2 and import a pre-made live text file.

3. Click on the little gear icon on the live text file you just imported. This will allow you to edit the GFX asset.

4. In one of the text boxes, type `%WebKey 01%`. You can rename it something more specific, but you'll have to reconfigure `TricasterDataLink.py` to have it match. I wouldn't bother, personally.

5. Clone the repository and install dependencies onto a Windows or MacOS machine with a webcam and speakers. I've had limited luck with Linux sadly, but I'm working on that.

6. Start the program with `python3 ./LiveLT.py`. This will start the GUI.

7. Click the dropdown menu at the top of the GUI to select which webcam you want to use as a capture device. It should show up in the viewfinder window once you select it. You can use any camera (virtual or not) that you want, just make sure it's well-lit to read the QR codes properly. If you don't see your camera, close the program, reseat the camera connection, and then re-launch the program. If you still have issues, let me know in a bug report. So far I've used NDI sources, OBS virtual cameras, built-in webcams, and USB webcams with no issues.

8. Click on the button that says "Change IP". Paste the Tricaster's IP address here and click "OK".

9. You can click the "Test Connection" button to make sure that LiveLT can communicate with the Tricaster. A little dialog will show up in the GUI's footer if successful. If not, the GUI will throw an error at you. You'll know when you see it.

10. You can add names by scanning QR codes or by clicking on "Add Custom Name".

11. You can also change the default slide by clicking the "Change Default Slide" button, which is great for if you want to display your institution's name.

12. You can change slides in one of three ways: 1. use the left/right arrows on your keyboard, 2. click the "Next Name" or "Previous Name" buttons, or selecting a name from the list. All accomplish the same thing.

13. If you need to display the default slide again, you can click the "Display Default" button or press the space bar.

### Tips and Tricks
- The Tricaster and the machine running this software need be on the same network. Ideally, plugged into the same network switch. I've been able to send names across subnets with no issue, but you won't be able to reach the tricaster if they're not on the same LAN. And please, DON'T open a port for this.

- The program saves its running config once you close it out. You can edit this by opening the `config.json` file in the repo folder. Most things are self-explanatory, but don't go too crazy.

### Utilities
You can create your own QR codes to scan using a built-in utility in the file menu. Just go to `File > Create QR Codes...` and it will bring up a GUI interface. Simply select a CSV file and where you want to export the qr code PNG files. The GUI may freeze if you have a lot of QR codes to make. I am aware of this issue, but I have yet to implement a workaround just yet.

One thing to note is that the CSV needs to have specific column titles for it to work properly. You need to have names split into 2 columns: FirstName and LastName. The program will combine the names into one once scanned.

### Planned Updates
- Fix QR Code GUI freezing when making PNG files en-masse
- Create an executable file for ease of transport
- Bug testing
- Port to Linux