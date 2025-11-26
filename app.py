from flask import Flask, request, jsonify, send_file, redirect, url_for
from pathlib import Path
from datetime import datetime
import cv2
import mediapipe as mp
import numpy as np
import re

app = Flask(__name__)

# ---------- Paths ----------

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
MOVEMENT_DICT_DIR = BASE_DIR / "movement_dictionary"

UPLOAD_DIR.mkdir(exist_ok=True)
MOVEMENT_DICT_DIR.mkdir(exist_ok=True)

# ---------- MediaPipe setup ----------

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Thicker pose drawing settings
LANDMARK_SPEC = mp_drawing.DrawingSpec(
    color=(0, 255, 0),  # bright green
    thickness=4,
    circle_radius=5,
)
CONNECTION_SPEC = mp_drawing.DrawingSpec(
    color=(0, 255, 0),
    thickness=4,
    circle_radius=5,
)


def sanitize_name(name: str) -> str:
    """
    Turn a user-entered name into a safe filename base:
    - keep letters, numbers, spaces, underscores, dashes
    - collapse spaces to underscores
    - strip leading/trailing underscores
    """
    if not name:
        return ""
    cleaned = re.sub(r"[^A-Za-z0-9 _-]+", "", name)
    cleaned = cleaned.strip().replace(" ", "_")
    cleaned = cleaned.strip("_")
    return cleaned


def process_video_to_landmarks(input_path: Path, output_path: Path) -> bool:
    """
    Take an input video file, convert each frame to pose-landmark overlays
    on a BLACK BACKGROUND, and save as a new MP4 at output_path.
    """
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        print("Could not open input video:", input_path)
        return False

    fps = cap.get(cv2.CAP_PROP_FPS) or 20
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Write output as MP4
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Run pose detection on the original frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        # Create a black background image
        black = np.zeros_like(frame)  # same (H, W, 3), all zeros

        # Draw landmarks onto the black canvas
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


# ---------- Front page: record in browser ----------

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
          background: #f5f5f5;
          margin: 0;
          padding: 20px;
        }
        .container {
          max-width: 800px;
          margin: 0 auto;
          background: #ffffff;
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

          1. This app will record parts of your movement sentence and process them with line animation on a <strong>black background</strong>. It saves the processed videos into the
             <strong>movement_dictionary</strong> folder. <br>
          2. Click <strong>Start Recording</strong> to record a movement.<br>
          3. Click <strong>Stop Recording</strong> to end.<br>
          4. Name your clip (optional) and it will be saved with that name.<br>
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


# ---------- API: receive recording, process, save ----------

@app.route("/upload_recording", methods=["POST"])
def upload_recording():
    file = request.files.get("video")
    if not file:
        return jsonify({"status": "error", "error": "No video uploaded"}), 400

    user_name = request.form.get("name", "") or ""
    safe_name = sanitize_name(user_name)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save raw recording (container/codec depends on browser; extension is just a label)
    input_path = UPLOAD_DIR / f"record_{timestamp}.bin"
    file.save(str(input_path))

    # Decide final filename
    if safe_name:
        base_name = safe_name
    else:
        base_name = f"movement_{timestamp}"

    final_name = base_name + ".mp4"
    final_path = MOVEMENT_DICT_DIR / final_name

    # If a file with that name already exists, append timestamp suffix
    if final_path.exists():
        final_name = f"{base_name}_{timestamp}.mp4"
        final_path = MOVEMENT_DICT_DIR / final_name

    # Process recording directly into landmarks video saved in movement_dictionary
    if not process_video_to_landmarks(input_path, final_path):
        return jsonify({"status": "error", "error": "Processing failed"}), 500

    return jsonify({"status": "ok", "filename": final_name})


# ---------- View & manage Movement Dictionary ----------

@app.route("/dictionary")
def dictionary():
    files = sorted(MOVEMENT_DICT_DIR.glob("*.mp4"))

    items_html = ""
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
          background: #f5f5f5;
          margin: 0;
          padding: 20px;
        }}
        .container {{
          max-width: 900px;
          margin: 0 auto;
          background: #ffffff;
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
        <h1>📚 Movement Dictionary</h1>
        {items_html}
      </div>
    </body>
    </html>
    """
    return html


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


@app.route("/movement/<path:filename>")
def serve_movement_file(filename):
    file_path = MOVEMENT_DICT_DIR / filename
    if not file_path.exists():
        return "File not found", 404
    # Force MIME type so the browser knows how to play it
    return send_file(file_path, mimetype="video/mp4")


if __name__ == "__main__":
    app.run(debug=True)

