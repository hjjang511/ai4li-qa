import cv2
import numpy as np
import json
import sys
import os

def draw_hand(canvas, keypoints):
    edges = [
        (0,1), (1,2), (2,3), (3,4),
        (0,5), (5,6), (6,7), (7,8),
        (0,9), (9,10), (10,11), (11,12),
        (0,13), (13,14), (14,15), (15,16),
        (0,17), (17,18), (18,19), (19,20)
    ]
    for x, y in keypoints:
        if x > 0 and y > 0:
            cv2.circle(canvas, (x, y), 4, (0, 255, 0), -1)
    for i, j in edges:
        x1, y1 = keypoints[i]
        x2, y2 = keypoints[j]
        if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
            cv2.line(canvas, (x1, y1), (x2, y2), (255, 0, 0), 2)
    return canvas

def main():
    if len(sys.argv) != 3:
        print("❌ Usage: python convert.py input.json output.mp4")
        return

    json_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(json_path):
        print(f"❌ JSON file not found: {json_path}")
        return

    with open(json_path, 'r') as f:
        frames = json.load(f)

    width, height = 960, 720
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), 15, (width, height))

    for frame_data in frames:
        frame = np.ones((height, width, 3), dtype=np.uint8) * 255  # white background
        hands = frame_data.get('hands', [])
        for hand in hands:
            keypoints = [(int(x), int(y)) for x, y in hand]
            frame = draw_hand(frame, keypoints)
        out.write(frame)

    out.release()
    print(f"✅ Video saved to: {output_path}")

if __name__ == "__main__":
    main()
