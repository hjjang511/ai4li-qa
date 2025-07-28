import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextEdit, QPushButton, QVBoxLayout
from underthesea import word_tokenize, pos_tag
import unicodedata

# ===== BẢNG GIẢI NGHĨA POS TAG (từ loại) =====
POS_TAGS_DESCRIPTION = {
    'N': 'Danh từ (Noun)',
    'Np': 'Danh từ riêng (Proper noun)',
    'Nu': 'Danh từ đơn vị (Unit noun)',
    'V': 'Động từ (Verb)',
    'A': 'Tính từ (Adjective)',
    'P': 'Đại từ (Pronoun)',
    'R': 'Giới từ (Preposition)',
    'L': 'Từ định lượng (Determiner)',
    'C': 'Liên từ (Conjunction)',
    'M': 'Số từ (Numeral)',
    'E': 'Giới từ (Preposition)',
    'I': 'Thán từ (Interjection)',
    'T': 'Trợ từ (Particle)',
    'Y': 'Từ viết tắt',
    'Z': 'Dấu câu',
    'X': 'Không xác định'
}

# ===== Chuẩn hóa dấu thanh điệu (loại bỏ) =====
def normalize_tone(text):
    text_nfd = unicodedata.normalize('NFD', text)
    return ''.join(c for c in text_nfd if unicodedata.category(c) != 'Mn')

# ===== Chuyển đổi sang cấu trúc ngôn ngữ ký hiệu =====
def convert_to_sign_structure(text):
    pos_tags = pos_tag(text)

    # Bỏ các từ không cần thiết
    skip_words = {"đã", "đang", "sẽ", "vào", "rất", "là", "một", "các", "những", "có", "bị", "được", "thì"}

    subject, verb, object_ = [], [], []
    question_words = []
    is_negative = False

    for word, tag in pos_tags:
        word_lower = word.lower()
        if word_lower in {"ai", "gì", "cái gì", "nào", "bao nhiêu", "khi nào", "ở đâu", "vì sao", "tại sao"}:
            question_words.append(word)
            continue
        if word_lower == "không":
            is_negative = True
            continue
        if word_lower in skip_words:
            continue

        if tag.startswith("V"):
            verb.append(word)
        elif tag.startswith("A"):
            object_.append(word)
        elif tag.startswith("N") or tag.startswith("P"):
            subject.append(word)

    result = subject + object_ + verb
    if question_words:
        result += question_words
    if is_negative:
        result.append("không")

    return " ".join(result)

# ===== Giao diện PyQt5 =====
class SignLanguageConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎯 Chuyển đổi tiếng Việt sang ngôn ngữ ký hiệu")

        self.input_label = QLabel("Nhập câu tiếng Việt:")
        self.input_text = QTextEdit()

        self.process_button = QPushButton("Xử lý và Chuyển đổi")
        self.result_label = QLabel("Kết quả:")

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_text)
        layout.addWidget(self.process_button)
        layout.addWidget(self.result_label)
        layout.addWidget(self.output_text)
        self.setLayout(layout)

        self.process_button.clicked.connect(self.process_text)

    def process_text(self):
        text = self.input_text.toPlainText()
        if not text.strip():
            self.output_text.setPlainText("⚠️ Vui lòng nhập câu.")
            return

        # Token hóa & POS Tag
        tokens = word_tokenize(text, format="text")
        pos = pos_tag(text)
        normalized = normalize_tone(text)
        sign_structure = convert_to_sign_structure(text)

        result = f"📌 Câu gốc: {text}\n"
        result += f"🔹 Tokenization: {tokens}\n"
        result += f"🔸 POS Tagging:\n"
        for w, t in pos:
            meaning = POS_TAGS_DESCRIPTION.get(t, "Không rõ")
            result += f"   {w:<15} - {t:<4} ({meaning})\n"

        result += f"\n🔻 Chuẩn hóa không dấu: {normalized}\n"
        result += f"🧩 Cấu trúc ngôn ngữ ký hiệu: {sign_structure}\n"

        self.output_text.setPlainText(result)

# ===== Chạy ứng dụng =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignLanguageConverter()
    window.resize(700, 550)
    window.show()
    sys.exit(app.exec_())
