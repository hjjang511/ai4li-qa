import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QComboBox
from gtts import gTTS
from pydub import AudioSegment
import simpleaudio as sa

class TTSApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vietnamese TTS - gTTS")
        self.setGeometry(200, 200, 400, 200)

        # Label nhập câu
        self.label = QLabel("Nhập câu tiếng Việt:", self)

        # Ô nhập văn bản
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Nhập câu để chuyển thành giọng nói...")

        # Label tốc độ
        self.label_speed = QLabel("Chọn tốc độ phát:", self)

        # ComboBox chọn tốc độ
        self.speed_box = QComboBox(self)
        self.speeds = [0.5, 0.75, 1.0, 1.5, 2.0]
        for sp in self.speeds:
            self.speed_box.addItem(f"{sp}x", sp)
        self.speed_box.setCurrentIndex(2)  # mặc định 1.0x

        # Nút chuyển thành giọng nói
        self.button_tts = QPushButton("Tạo file MP3", self)
        self.button_tts.clicked.connect(self.generate_tts)

        # Nút phát file MP3
        self.button_play = QPushButton("Phát file MP3", self)
        self.button_play.clicked.connect(self.play_audio)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.text_input)
        layout.addWidget(self.label_speed)
        layout.addWidget(self.speed_box)
        layout.addWidget(self.button_tts)
        layout.addWidget(self.button_play)
        self.setLayout(layout)

        # Tạo thư mục mp3 nếu chưa có
        if not os.path.exists("mp3-tts"):
            os.makedirs("mp3-tts")

        self.mp3_path = os.path.join("mp3-tts", "output.mp3")

    def generate_tts(self):
        """Tạo file MP3 từ gTTS"""
        text = self.text_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập câu tiếng Việt!")
            return

        try:
            tts = gTTS(text=text, lang='vi', slow=False)
            tts.save(self.mp3_path)
            QMessageBox.information(self, "Thành công", f"Đã tạo file MP3: {self.mp3_path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tạo giọng nói:\n{str(e)}")

    def play_audio(self):
        """Phát file MP3 với tốc độ đã chọn"""
        if not os.path.exists(self.mp3_path):
            QMessageBox.warning(self, "Lỗi", "Chưa có file MP3! Vui lòng tạo trước.")
            return

        try:
            # Lấy tốc độ
            speed = self.speed_box.currentData()

            # Load file MP3
            sound = AudioSegment.from_mp3(self.mp3_path)

            # Điều chỉnh tốc độ (dùng thay đổi frame rate)
            new_frame_rate = int(sound.frame_rate * speed)
            sound_with_speed = sound._spawn(sound.raw_data, overrides={"frame_rate": new_frame_rate})
            sound_with_speed = sound_with_speed.set_frame_rate(44100)  # chuẩn hóa lại

            # Xuất ra file tạm WAV để phát
            temp_wav = "temp.wav"
            sound_with_speed.export(temp_wav, format="wav")

            # Phát âm thanh
            wave_obj = sa.WaveObject.from_wave_file(temp_wav)
            play_obj = wave_obj.play()
            play_obj.wait_done()

            os.remove(temp_wav)  # xóa file tạm sau khi phát

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể phát âm thanh:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TTSApp()
    window.show()
    sys.exit(app.exec_())
