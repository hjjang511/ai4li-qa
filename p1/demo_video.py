import copy
import numpy as np
import cv2
import os
import argparse
import json
import subprocess
from pathlib import Path
from typing import NamedTuple

# openpose setup
from src import model
from src import util
from src.body import Body
from src.hand import Hand

body_estimation = Body('model/body_pose_model.pth')
hand_estimation = Hand('model/hand_pose_model.pth')

def process_frame(frame, body=True, hands=True):
    canvas = copy.deepcopy(frame)
    frame_data = {"hands": []}
    if body:
        candidate, subset = body_estimation(frame)
        canvas = util.draw_bodypose(canvas, candidate, subset)
    else:
        candidate, subset = [], []

    if hands:
        hands_list = util.handDetect(candidate, subset, frame)
        all_hand_peaks = []
        for x, y, w, is_left in hands_list:
            peaks = hand_estimation(frame[y:y+w, x:x+w, :])
            peaks[:, 0] = np.where(peaks[:, 0]==0, peaks[:, 0], peaks[:, 0]+x)
            peaks[:, 1] = np.where(peaks[:, 1]==0, peaks[:, 1], peaks[:, 1]+y)
            all_hand_peaks.append(peaks.tolist())
        frame_data["hands"] = all_hand_peaks
        canvas = util.draw_handpose(canvas, all_hand_peaks)

    return canvas, frame_data

# --- FFmpeg support ---
class FFProbeResult(NamedTuple):
    return_code: int
    json: str
    error: str

def ffprobe(file_path) -> FFProbeResult:
    command_array = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", file_path
    ]
    result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return FFProbeResult(return_code=result.returncode, json=result.stdout, error=result.stderr)

import ffmpeg

class Writer():
    def __init__(self, output_file, input_fps, input_framesize, input_pix_fmt, input_vcodec):
        if os.path.exists(output_file):
            os.remove(output_file)
        self.ff_proc = (
            ffmpeg
            .input('pipe:',
                   format='rawvideo',
                   pix_fmt='bgr24',
                   s=f"{input_framesize[1]}x{input_framesize[0]}",
                   r=input_fps)
            .output(output_file, pix_fmt=input_pix_fmt, vcodec=input_vcodec)
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )

    def __call__(self, frame):
        self.ff_proc.stdin.write(frame.tobytes())

    def close(self):
        self.ff_proc.stdin.close()
        self.ff_proc.wait()

# --- Main ---
parser = argparse.ArgumentParser(description="Process a video annotating poses detected.")
parser.add_argument('file', type=str, help='Video file location to process.')
parser.add_argument('--no_hands', action='store_true', help='No hand pose')
parser.add_argument('--no_body', action='store_true', help='No body pose')
args = parser.parse_args()

video_file = args.file
cap = cv2.VideoCapture(video_file)

# lấy thông tin video
ffprobe_result = ffprobe(video_file)
info = json.loads(ffprobe_result.json)
videoinfo = [i for i in info["streams"] if i["codec_type"] == "video"][0]
input_fps = eval(videoinfo["avg_frame_rate"])
input_pix_fmt = videoinfo["pix_fmt"]
input_vcodec = videoinfo["codec_name"]

postfix = info["format"]["format_name"].split(",")[0]
output_file = ".".join(video_file.split(".")[:-1]) + ".processed." + postfix

# json
json_output = []
frame_index = 0
writer = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret or frame is None:
        break

    posed_frame, frame_data = process_frame(frame, body=not args.no_body, hands=not args.no_hands)
    frame_data["frame_index"] = frame_index
    json_output.append(frame_data)
    frame_index += 1

    # Khởi tạo writer tại frame đầu tiên
    if writer is None:
        input_height, input_width = posed_frame.shape[:2]
        if input_width % 2 != 0:
            input_width += 1
        posed_frame = cv2.resize(posed_frame, (input_width, input_height))
        input_framesize = (input_height, input_width)
        writer = Writer(output_file, input_fps, input_framesize, input_pix_fmt, input_vcodec)

    else:
        posed_frame = cv2.resize(posed_frame, (input_width, input_height))

    cv2.imshow("frame", posed_frame)
    writer(posed_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
writer.close()
cv2.destroyAllWindows()

# Lưu JSON
os.makedirs("json", exist_ok=True)
basename = os.path.basename(video_file).split(".")[0]
json_path = os.path.join("json", f"{basename}.hands.json")
with open(json_path, "w") as f:
    json.dump(json_output, f, indent=2)

print(f"✅ Đã lưu kết quả keypoints vào: {json_path}")
