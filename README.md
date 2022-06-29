# LiveLT
This Python script allows you to scan QRCodes and transmit them directly to a NewTek Tricaster via their DataLink feature. The script uses PyQt5 for the main GUI and opencv-python for capturing webcam input and QR decoding.

### Dependencies
This script requires Python 3.10 or higher. You'll need to install a few dependencies as well by running `pip3 install -r ./requirements.txt` once you've cloned the repo.

### How to Use
1. On your Tricaster, start up a live switching project and click on the globe in the top-right corner. Take note of your Tricaster's IP address and save that for later. I highly recommend giving your Tricaster a static IP address or reserving the DHCP address on your router. See your router's manual for more information on this.

2. Go to GFX 1 or GFX 2 and import a pre-made live text file.

3. Click on the little gear icon on the live text file you just imported. This will allow you to edit the GFX asset.

4. In one of the text boxes, type `%WebKey 01%`. You can rename it something more specific, but you'll have to reconfigure `TricasterDataLink.py` to have it match. I wouldn't bother, personally.

5. Clone the repository and install dependencies onto a windows machine with a webcam.

6. Start the program with `python3 ./LiveLT.py`. This will start the GUI.

7. Click the dropdown menu at the top of the GUI to select which webcam you want to use as a capture device. It should show up in the viewfinder window once you select it. You can use any camera (virtual or not) that you want, just make sure it's well-lit to read the QR codes properly.

8. Click on the button that says "Change IP". Paste the Tricaster's IP address here and click "OK".

9. You can click the "Test Connection" button to make sure that LiveLT can communicate with the Tricaster. A little dialog will show up in the GUI's footer if successful. If not, the GUI will throw an error at you. You'll know when you see it.

10. You can add names by scanning QR codes or by clicking on "Add Custom Name". The custom name button is useful for adding your organization's name if you want.

11. You can change slides in one of three ways: 1. use the left/right arrows on your keyboard, 2. click the "Next Name" or "Previous Name" buttons, or selecting a name from the list. All accomplish the same thing.

12. If you encounter an error, you can click the "Display Default" button.

### Tips and Tricks
The program saves its running config once you close it out. You can edit this by opening the `config.json` file in the repo folder. Most things are self-explanatory, but don't go too crazy.

### Planned Updates
- Create an executable file for ease of transport
