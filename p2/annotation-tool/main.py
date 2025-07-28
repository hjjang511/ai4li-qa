import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import json
import os
from PIL import Image, ImageTk

class VideoAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Annotation Tool")

        # Frame Video
        self.canvas = tk.Canvas(root, width=640, height=480)
        self.canvas.pack()

        # Các nút điều khiển
        controls = tk.Frame(root)
        controls.pack()

        tk.Button(controls, text="Open Video", command=self.load_video).grid(row=0, column=0)
        tk.Button(controls, text="Play", command=self.play_video).grid(row=0, column=1)
        tk.Button(controls, text="Pause", command=self.pause_video).grid(row=0, column=2)
        tk.Button(controls, text="Start Frame", command=self.set_start_frame).grid(row=0, column=3)
        tk.Button(controls, text="End Frame", command=self.set_end_frame).grid(row=0, column=4)
        tk.Button(controls, text="Add Annotation", command=self.add_annotation).grid(row=0, column=5)
        tk.Button(controls, text="Export JSON", command=self.save_annotations).grid(row=0, column=6)
        tk.Button(controls, text="⏮️ Prev", command=lambda: self.move_frame(-1)).grid(row=0, column=7)
        tk.Button(controls, text="⏭️ Next", command=lambda: self.move_frame(1)).grid(row=0, column=8)
        tk.Button(controls, text="-10", command=lambda: self.move_frame(-10)).grid(row=0, column=9)
        tk.Button(controls, text="+10", command=lambda: self.move_frame(10)).grid(row=0, column=10)

        self.translation_entry = tk.Entry(root, width=50)
        self.translation_entry.pack(pady=5)

        self.frame_label = tk.Label(root, text="Frame: 0")
        self.frame_label.pack()

        self.root.bind("<Left>", lambda e: self.move_frame(-1))
        self.root.bind("<Right>", lambda e: self.move_frame(1))

        self.cap = None
        self.current_frame = 0
        self.total_frames = 0
        self.playing = False
        self.start_frame = None
        self.end_frame = None
        self.annotations = []
        self.video_path = ""

    def load_video(self):
        print("📂 Current working directory:", os.getcwd())
        path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
        if not path:
            return
        self.cap = cv2.VideoCapture(path)
        self.video_path = path
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame = 0
        self.annotations = []
        self.start_frame = None
        self.end_frame = None
        self.show_frame()

    def show_frame(self):
        if not self.cap:
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.resize(frame, (640, 480))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.canvas.imgtk = imgtk
        self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        self.frame_label.config(text=f"Frame: {self.current_frame}/{self.total_frames}")
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        current_time = self.current_frame / fps
        self.frame_label.config(text=f"Frame: {self.current_frame}/{self.total_frames} | Time: {current_time:.2f}s")

    def play_video(self):
        self.playing = True
        self.play_loop()

    def play_loop(self):
        if self.playing and self.cap:
            self.current_frame += 1
            if self.current_frame >= self.total_frames:
                self.playing = False
                return
            self.show_frame()
            self.root.after(30, self.play_loop)

    def pause_video(self):
        self.playing = False

    def move_frame(self, step):
        if not self.cap:
            return
        self.pause_video()
        self.current_frame = max(0, min(self.total_frames - 1, self.current_frame + step))
        self.show_frame()

    def set_start_frame(self):
        self.start_frame = self.current_frame
        messagebox.showinfo("Start Frame", f"Start Frame set to: {self.start_frame}")

    def set_end_frame(self):
        self.end_frame = self.current_frame
        messagebox.showinfo("End Frame", f"End Frame set to: {self.end_frame}")

    def add_annotation(self):
        if self.start_frame is None or self.end_frame is None:
            messagebox.showerror("Thiếu thông tin", "Cần đặt cả Start và End frame.")
            return

        text = self.translation_entry.get().strip()
        if not text:
            messagebox.showerror("Thiếu bản dịch", "Vui lòng nhập nội dung bản dịch.")
            return

        ann = {
            "start": min(self.start_frame, self.end_frame),
            "end": max(self.start_frame, self.end_frame),
            "text": text
        }
        self.annotations.append(ann)

        messagebox.showinfo("✅ Đã thêm", f"Đã thêm annotation: {ann}")

        # Reset
        self.start_frame = None
        self.end_frame = None
        self.translation_entry.delete(0, tk.END)



    def save_annotations(self):
        if not self.video_path or not self.annotations:
            messagebox.showwarning("Không có dữ liệu", "Không có annotation nào để lưu.")
            return

        try:
            os.makedirs("annotations", exist_ok=True)
            video_name = os.path.splitext(os.path.basename(self.video_path))[0]
            filename = f"annotations/{video_name}_annotations.json"

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.annotations, f, ensure_ascii=False, indent=4)

            messagebox.showinfo("✅ Đã lưu", f"Tất cả annotation đã được lưu vào:\n{filename}")
        except Exception as e:
            messagebox.showerror("❌ Lỗi", f"Không thể lưu annotations!\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoAnnotator(root)
    root.mainloop()
