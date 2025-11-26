Movement Dictionary App

This app lets you or your students:
1. Record a movement with your webcam in the browser
2. Automatically convert it to MediaPipe pose landmarks drawn in thick green lines on a black background
3. Save and review clips in a personal Movement Dictionary
4. Rename clips and delete them from the dictionary
5. It runs entirely on your own computer. You do not upload your videos to any external server.

What you need
1. A computer with a webcam
2. Python 3.10 or 3.11 installed
3. A web browser (Chrome, Safari, or Edge)

To check your Python version (Mac) Type:

  python3 --version

**Download the project**
If using GitHub (recommended):

1.  Go to the repository link:

[https://github.com/YOUR_USERNAME/movement-dictionary-app](https://github.com/ravitc10/Movement-Dictionary-Maker-Web-App)

2. Click Code → Download ZIP
3. Unzip the folder somewhere easy (like Desktop)

**You should now see a folder containing:**
  a. app.py
  b. requirements.txt
  c. README.md
  d. Folders like movement_dictionary and uploads (they may be empty)

4. Open a terminal in that folder
   
On Mac:
  a. Open Terminal
  b. Type cd (with a space)
  c. Drag the project folder into the Terminal window → press Enter

**Example:**
cd /Users/yourname/Desktop/movement-dictionary-app

5. Create a virtual environment (one time)
  a. Inside the folder:
  b. python3 -m venv .venv
  c. Activate it (do this every time before running):
    source .venv/bin/activate

**You should now see something like (.venv) at the beginning of your terminal prompt.**
To stop using it later:
****deactivate****

6. Install required Python packages
**With the virtual environment activated, run:**
1. pip install --upgrade pip
2. pip install -r requirements.txt
_This may take a few minutes (MediaPipe and OpenCV can be large)._

7. Run the app
python app.py

You’ll see:
 * Running on http://127.0.0.1:5000/

Now open your browser to:

http://127.0.0.1:5000/

7. How to use the app
  a. Optionally enter a name for your movement clip
  b. click Start Recording
  c. The browser will ask for camera permission → click Allow
  d. Move/dance in front of your webcam
  e. Click Stop Recording
The app will:
  a. Send the clip to the backend
  b. Run MediaPipe Pose on each frame
  c. Draw landmarks on a black background
  d. Save the processed video into your movement_dictionary folder
  e. When finished, you’ll see:
  f. Saved to Movement Dictionary as: your_name.mp4

Movement Dictionary page (/dictionary)
Navigate to:
http://127.0.0.1:5000/dictionary

or click the link at the top of the main page.

_Here you can:_
  a. Play all saved movement clips
  b. View them inline
  c. Delete any clip you no longer want
  d. Click Delete
    i. Confirm the popup
    ii. The clip is removed from the folder and the list
    iii. All processed videos are stored in:
    movement_dictionary/

7. Stopping the app

  a. In the Terminal where it’s running, press:
  Ctrl + C
  b. To leave the virtual environment (optional):
  c. deactivate

8. Running the app again later

Each time you want to use the app:

  cd /path/to/movement-dictionary-app
  source .venv/bin/activate
  python app.py

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
  Try a different browser
  Right-click a video → Save As → try playing it in QuickTime or VLC
  Processed videos are black or broken
_Ensure all dependencies installed correctly_
  Reinstall opencv-python or mediapipe if needed
  Try recording a shorter test clip

**Technical Details (for advanced users)**
This app uses:
  1. Flask for the backend
  2. MediaRecorder API in the browser to capture webcam video
  3. OpenCV to read video frames
  4. MediaPipe Pose to detect landmarks
  5. Custom drawing on black frames (numpy.zeros_like)
  6. MP4 encoding via cv2.VideoWriter (no ffmpeg needed)
  7. Processed videos are stored in:
    movement_dictionary/
  8. Raw recordings are stored in:
    uploads/
  (These can be deleted safely)
