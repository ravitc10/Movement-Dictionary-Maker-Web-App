"""
The first import statements import Flask to make an application using the Flask framework. the flask import statement also specifically imports the 
necessary modules for prosessing JSON responses, making requests, file sending and URL redirection. 

The import statements also bring Pathlib, Datetime, cv2, mediapipe, numpy, and re into the code. Each having a specific function. Pathlib makes the storing and 
accessing of files simpler, by helping to tell python the paths files will travel as they are uploaded and processed. datetime allows the videos the users record
to be labeled with their date and time (timestamped). cv2 allows for video reading and processing, letting the computer to access the camera when necessary. Mediapipe
is the most important module, and it allows the videos users upload to be processed with landmarks for their skeletel features. This is what gives the videos the 
intended 'stick figure' effect. Numpy is used for the processing of the videos, as Mediapipe requires videos to be processed as individual frames and the 
re module helps to sanatize (make computer readable) the names they gave their movement dictionary entries.
"""
from flask import Flask, request, jsonify, send_file, redirect, url_for
from pathlib import Path
from datetime import datetime
import cv2
import mediapipe as mp
import numpy as np
import re

# creates a flask instance
app = Flask(__name__)

"""
This part of the code establishes the upload paths for the raw user video as well as the eventual mediapiped processed version of these videos.
To do this, it first establishes a root directory called BASE_DIR and also establishes an UPLOAD_DIR within this root directory. UPLOAD_DIR is where 
the unprocessed videos are stored. It also establishes the existence of the movement dictionary directory (MOVEMENT_DICT_DIR) within the base directory. 
This is where the user's videos that are processed with MediaPipe will be stored. MOVEMENT_DICT_DIR is the basis for the second page of the webapp, where users 
can view their processed movement dictionaries.
"""

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
MOVEMENT_DICT_DIR = BASE_DIR / "movement_dictionary"

UPLOAD_DIR.mkdir(exist_ok=True)
MOVEMENT_DICT_DIR.mkdir(exist_ok=True)

"""
The following code contaings the set-up for usage of the MediaPipe module, which tracks Human movement using lines and connectors. It creates a 'stick-figure' 
effect, of lines being drawn on top of the body. The code under LANDMARK_SPEC sets the thickness of these lines to 6 and the color of the lines to pink. The code 
under CONNECTION_SPEC sets the color of the circles that connect the lines to pink and the thickness to 6 You can think of the lines (LANDMARK_SPEC) as bones and 
the circular connectors (CONNECTION_SPEC) as joints. 
"""

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

LANDMARK_SPEC = mp_drawing.DrawingSpec(
    color=(203, 192, 255),  # pink
    thickness=6,
    circle_radius=5,
)
CONNECTION_SPEC = mp_drawing.DrawingSpec(
    color=(203, 192, 255), # pink
    thickness=6,
    circle_radius=5,
)
 
"""
The sanitize_name function makes the name that users enter for their videos readable for the computer. It does this by replacing spaces with underscores, making
the user entered name viable!

The ability for the webapp to allow users to view their movement dictionary entries with actual names instead of a long computer generated string will  help
users remember the concept they created their movement dictionary entry to represent. 
"""
def sanitize_name(name: str) -> str:
    if not name:
        return ""
    cleaned = re.sub(r"[^A-Za-z0-9 _-]+", "", name)
    cleaned = cleaned.strip().replace(" ", "_")
    cleaned = cleaned.strip("_")
    return cleaned
"""
The process_video_to_landmarks() function opens,reads, and processes the video imput that the user creates. If it fails it prints an error message. If it can read 
the video, it retrieves information about the video dimensions(width and height) and number of frames (sets them to 20 per second for a default if the imput
does not specify). Then, it writes an output path that matches the specifications of the input. Next it brings in the MediaPipe module with the 
correct specifications for this task: continous pose detection with medium complexity. Then the function starts a frame processing loop using 'while' for user 
input videos. This loop converts the background of these frames to black, draws landmarks on each, and processes them into video form. 
"""
def process_video_to_landmarks(input_path: Path, output_path: Path) -> bool:

    # Open input video for processing
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        print("Could not open input video:", input_path)
        return False

    # gain information about the input video's fps (frames per second) and frame size
    fps = cap.get(cv2.CAP_PROP_FPS) or 20
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Write output path with same fps and frame size as input
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    # Begins mediapipe pose processing, makes sure the mediapipe settings are appropriate
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    # Begin frame processing loop
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert BGR to RGB for mediapipe processing
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        # Processes frames with black background. 
        black = np.zeros_like(frame)  # same (H, W, 3), all zeros

        # Actually draw the landmarks (stick figrures) on the individual black frames
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                black,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=LANDMARK_SPEC,
                connection_drawing_spec=CONNECTION_SPEC,
            )

        out.write(black)

    cap.release()
    out.release()
    return True


"""
Now the code moves to specifying the front-end Web-App environment for the Movement Dictionary application. Here, the code switches to HTML. It first specifies
the title and font of the WebApp as well as other dimensions. It also sets up the video recording on the front page of the WebApp, and it sets up the 
text to click to navigate to the movement dictionary page as well. It also explains the video recording experience that the user will have, what the recording
buttons look like, and what error messages the user will recieve if the recording does not go according to plan or if the user's browser will not let them record. 
"""

@app.route("/")
def index():
    html = """
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Let's Make a Movement Dictionary!</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          background: #ffb6c1; 
          margin: 0;
          padding: 20px;
        }
        .container {
          max-width: 800px;
          margin: 0 auto;
          background: #ffe6f2;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        video {
          max-width: 100%;
          border: 1px solid #ccc;
          background: #000;
        }
        button {
          padding: 8px 16px;
          margin: 5px 5px 5px 0;
          font-size: 14px;
          cursor: pointer;
        }
        #status {
          margin-top: 10px;
        }
        .top-links {
          margin-bottom: 10px;
        }
        .top-links a {
          margin-right: 10px;
        }
        label {
          display: inline-block;
          margin-top: 10px;
        }
        input[type="text"] {
          padding: 4px 8px;
          margin-left: 5px;
          font-size: 14px;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="top-links">
          <a href="/dictionary"> Click Here to View Your Movement Dictionary</a>
        </div>
        <h1>Movement Dictionary Maker</h1>
        <p>

          This app will help you create a movement dictionary! You can record short videos that represent a concept and you can name these videos. 
          The app will process them with line animation on a <strong>black background</strong>. It will save the processed videos into the
             <strong>movement_dictionary</strong> folder, which you can access by clicking the link at the top of this page. To get started:<br>
          1. Name your movement concept; it will be saved with that name.<br>
          2. Click <strong>Start Recording</strong> to record a movement.<br>
          3. Click <strong>Stop Recording</strong> to end.<br>
          4. Visit the Movement Dictionary page to view your movement concept.<br>
        </p>

        <label for="clipName">Name this clip:</label>
        <input type="text" id="clipName" placeholder="e.g., verb">

        <br><br>
        <video id="preview" autoplay muted playsinline></video><br>
        <button type="button" onclick="startRecording()">Start Recording</button>
        <button type="button" onclick="stopRecording()">Stop Recording</button>

        <p id="status"></p>
      </div>

      <script>
        let mediaRecorder;
        let recordedChunks = [];
        let streamRef = null;
        const preview = document.getElementById('preview');
        const statusEl = document.getElementById('status');
        const nameInput = document.getElementById('clipName');

        async function startRecording() {
          recordedChunks = [];
          statusEl.textContent = "Requesting camera...";

          try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            streamRef = stream;
            preview.srcObject = stream;
            preview.play();

            // Pick a mimeType that the browser actually supports
            let options = {};
            if (typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported) {
              if (MediaRecorder.isTypeSupported("video/webm;codecs=vp8")) {
                options.mimeType = "video/webm;codecs=vp8";
              }
              // else: leave options empty and let Safari/others pick default
            }

            try {
              mediaRecorder = new MediaRecorder(stream, options);
            } catch (e) {
              console.error("MediaRecorder init failed with options", options, e);
              statusEl.textContent = "MediaRecorder error: " + e.name + " - " + e.message;
              return;
            }

            mediaRecorder.ondataavailable = (e) => {
              if (e.data && e.data.size > 0) {
                recordedChunks.push(e.data);
              }
            };

            mediaRecorder.onstop = async () => {
              statusEl.textContent = "Uploading recording for processing...";
              const blob = new Blob(recordedChunks);
              const formData = new FormData();
              formData.append('video', blob, 'recording.bin');
              formData.append('name', nameInput.value);

              try {
                const response = await fetch('/upload_recording', {
                  method: 'POST',
                  body: formData
                });

                const data = await response.json();
                if (data.status === 'ok') {
                  statusEl.textContent = "Saved to Movement Dictionary as: " + data.filename;
                } else {
                  statusEl.textContent = "Error: " + (data.error || "Unknown error");
                }
              } catch (err) {
                console.error(err);
                statusEl.textContent = "Error uploading recording: " + err;
              }
            };

            mediaRecorder.start();
            statusEl.textContent = "Recording... press 'Stop Recording' when done.";
          } catch (err) {
            console.error("getUserMedia or setup error", err);
            statusEl.textContent = "Camera/setup error: " + err.name + " - " + err.message;
          }
        }

        function stopRecording() {
          if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            statusEl.textContent = "Stopping recording...";
          }

          if (streamRef) {
            const tracks = streamRef.getTracks();
            tracks.forEach(t => t.stop());
            streamRef = null;
          }
        }
      </script>
    </body>
    </html>
    """
    return html


'''
This next section of the code recieves and saves the user's recorded video. Then it processes the 
video into a mediapipe landmark MP4 using the process_video_to_landmarks function. It will then
return a JSON success or error. 
'''

# Reads the user 'video' and returns an error message if there is no video to be read
@app.route("/upload_recording", methods=["POST"])
def upload_recording():
    file = request.files.get("video")
    if not file:
        return jsonify({"status": "error", "error": "No video uploaded"}), 400

    # Reads the name the user provided, it will use an empty string if there was no provided name, causing the video to just be labeled with the timestamp
    user_name = request.form.get("name", "") or ""
    # Converts the user name to a sanitized, readable name
    safe_name = sanitize_name(user_name)

    # Creates a timestamp for the file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Saves the video to a upload folder and uses .bin to account for video containers that vary by browser. 
    input_path = UPLOAD_DIR / f"record_{timestamp}.bin"
    file.save(str(input_path))

    # This names the output file using the sanitized user input or a tiemstamp string
    # Creates MP4 and a specifies that the processed MP4 should go to the movement_dictionary folder
    if safe_name:
        base_name = safe_name
    else:
        base_name = f"movement_{timestamp}"

    final_name = base_name + ".mp4"
    final_path = MOVEMENT_DICT_DIR / final_name

    # If a file with that name already exists, add the timestamp to differentiate and not overwrite existing video
    if final_path.exists():
        final_name = f"{base_name}_{timestamp}.mp4"
        final_path = MOVEMENT_DICT_DIR / final_name

    # Processes the output video into mediapipe landmarks and returns an error if this does not works
    if not process_video_to_landmarks(input_path, final_path):
        return jsonify({"status": "error", "error": "Processing failed"}), 500

    # return jsonify when successful
    return jsonify({"status": "ok", "filename": final_name})


'''
This next section of code specifies the front-end for the Movement Dictionary page of the WebApp, where the processed MediaPipe videos are viewable for the users.
It begins by defining a dictionary() function to alphebetically sort all the user files in the MOVEMENT_DICT_DIR directory, which are the MediaPipe processed files. 
It will either return a message that there are no files yet in the MOVqEMENT_DICT_DIR directory or it will initiate a for loop to create HTML for each clip. It is 
this HTML that is linked and presented to users on the movement dictionary page of the app. 

It also specifies the aesthetics of the movement dictionary page, including a delete button for each video, the backend function of which is explained in the
delete_clip() function in the next section of the code. 
'''

@app.route("/dictionary")
def dictionary():
    files = sorted(MOVEMENT_DICT_DIR.glob("*.mp4"))

    items_html = ""

    # This shows a message if the user has not recorded any files yet
    if not files:
        items_html = "<p>You don't have any saved clips yet.</p>"
    else:
        for f in files:
            src = f"/movement/{f.name}"
            items_html += f"""
            <div style="margin-bottom: 20px; border-bottom: 1px solid #ddd; padding-bottom: 10px;">
              <video controls style="max-width: 100%; display: block; margin-bottom: 5px;">
                <source src="{src}" type="video/mp4">
                Your browser does not support the video tag.
              </video>
              <div style="display: flex; align-items: center; gap: 10px;">
                <span>{f.name}</span>
                <form method="POST" action="/delete_clip" onsubmit="return confirm('Delete this clip?');">
                  <input type="hidden" name="filename" value="{f.name}">
                  <button type="submit" style="padding: 4px 8px; font-size: 12px; cursor: pointer;">
                    Delete
                  </button>
                </form>
              </div>
            </div>
            """

    html = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Movement Dictionary</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background: #ffb6c1;
          margin: 0;
          padding: 20px;
        }}
        .container {{
          max-width: 900px;
          margin: 0 auto;
          background: #ffe6f2;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}
        a {{
          color: #007bff;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <p><a href="/">⬅︎ Back to Recorder</a></p>
        <h1>Movement Dictionary</h1>
        {items_html}
      </div>
    </body>
    </html>
    """
    return html

"""
The next section of the code defines the delete_clip() function which creates the user's ability to delete entries into their movement dictionaries that 
they no longer want to have in the dictionary. It specifies that the file exists. If the file does not exist, it returns an
error. If the file does exist, it deletes the file (this is done through the file_path.unlink() method in line 474).
Then it redirects the user back to the movement dictionary page. 
"""
@app.route("/delete_clip", methods=["POST"])
def delete_clip():
    filename = request.form.get("filename", "")
    if not filename:
        return redirect(url_for("dictionary"))

    file_path = MOVEMENT_DICT_DIR / filename
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print("Error deleting file:", file_path, e)

    return redirect(url_for("dictionary"))

"""
This part of the code defines a function, serve_movement_file(), that specifies to the 
browser the MIME (Multipurpose Internet Mail Extentions) of the videos, which in this case is mp4, so that
the browser knows how to play the videos on the movement dictionary page
"""
@app.route("/movement/<path:filename>")
def serve_movement_file(filename):
    file_path = MOVEMENT_DICT_DIR / filename
    if not file_path.exists():
        return "File not found", 404
    # Force MIME (Multipurpose Internet Mail Extentions) type so the browser knows how to play it
    return send_file(file_path, mimetype="video/mp4")


"""
This part of the code runs the app with the debugger enabled.
"""
if __name__ == "__main__":
    app.run(debug=True)
