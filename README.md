Movement Dictionary App

This app lets you or your students:
1. Record a movement with your webcam in the browser
2. Automatically convert it to MediaPipe pose landmarks drawn in thick pink lines on a black background
3. Save and review clips in a personal Movement Dictionary, linked at the top of the first page
4. Delete clips from the dictionary

Directions to run the app locally on your own computer:

What you need
1. A computer with a webcam
2. Python 3.10 or 3.11 installed
3. A Web Browser (Preferably Safari)

**Step One: Download the project**
1.  Go to the repository link:

[https://github.com/YOUR_USERNAME/movement-dictionary-app](https://github.com/ravitc10/Movement-Dictionary-Maker-Web-App)

2. Click Code → Download ZIP
3. Upload the folder into your coding environment

_You should now see a folder containing:_
  a. app.py
  b. requirements.txt
  c. README.md
  d. Folders like movement_dictionary and uploads (they will be empty)

4. Open a terminal in that folder and verify that you are in the correct location by prompting python with: pwd
Click enter and you should see something like:
   
/Users/yourname/Desktop/movement-dictionary-app

5. If you do not see: /Users/yourname/Desktop/movement-dictionary-app , you can navigate here with the following commands:
6. cd /Users/yourname/Desktop
7. cd /Users/yourname/Desktop/movement-dictionary-app

**Step Two: Create a Virtual Environment**
Once you verify your location as /Users/yourname/Desktop/movement-dictionary-app , you must create a new virtual environment:
1. First, you need to make sure you are using python 10 or 11. Verify this by typing python3 --version (mac) or python --version (mac)
2. Next, after verifying you are using python 3.11 or 3.10, you can create the environemnt by typing in the terminal:
  python3 -m venv .venv
  You can name your vertual environment anything you would like for example: my_movement_dictionary.venv
3. Activate your virtual en(do this every time before running the app) by running the following command in your terminal: 
source (name of your virtual environment).venv/bin/activate


**You should now see something like (.venv) at the beginning of your terminal prompt.**
To stop using it later write:
**deactivate**

4. Install required Python packages
**With the virtual environment activated, run:**
5. pip install --upgrade pip
6. pip install -r requirements.txt
_This may take a few minutes (MediaPipe and OpenCV can be large)._

**Step Three: Run the app.py File in your Terminal**
1. To run the app in your terminal use the command: python app.py
2. After your terminal finishes processing, navigate to http://127.0.0.1:5000/ to use the app.

**The App Runs Best on Safari**

3. To stop running the app press **Ctrl + C** in the terminal the app is running in

8. Running the app again later

**Troubleshooting**
_Browser says “Camera/setup error”_
  Make sure you clicked Allow when asked for camera access
_If denied accidentally, re-enable camera permissions in browser settings_
  Quit other apps using the webcam (Zoom, Teams, etc.)
_Terminal says: ModuleNotFoundError_
  Install missing packages:
    pip install -r requirements.txt
  If it still complains, install individually:
    pip install package_name
_Videos don’t play in the browser_
  Refresh the page
  Try a different browser, safari is reccomended
  Right-click a video → Save As → try playing it in QuickTime or VLC
_Processed videos are black or broken_
  Ensure all dependencies installed correctly
  Reinstall opencv-python or mediapipe if needed
  Try recording a shorter test clip


