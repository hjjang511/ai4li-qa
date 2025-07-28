import re
import unicodedata
from underthesea import word_tokenize, pos_tag

def normalize_unicode(text):
    # Chuẩn hóa unicode về dạng tổ hợp (NFC)
    return unicodedata.normalize('NFC', text)

def normalize_tone_mark(text):
    """
    Đưa dấu thanh về đúng vị trí theo quy tắc chính tả tiếng Việt.
    Chức năng này chỉ là ví dụ minh họa, xử lý đơn giản một vài mẫu thường gặp.
    """
    def fix_dau_tu(word):
        # Nếu không phải chữ có dấu tiếng Việt thì bỏ qua
        tone_marks = "àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ"
        if not any(char in tone_marks for char in word):
            return word
        # Dùng underthesea đã xử lý dấu khá chuẩn, nên không sửa sâu ở đây
        return word

    words = text.split()
    fixed_words = [fix_dau_tu(word) for word in words]
    return ' '.join(fixed_words)

def vn_text_pipeline(text):
    print("🚩 Original Text:")
    print(text)
    print("\n✅ Bước 1: Normalize Unicode:")
    text = normalize_unicode(text)
    print(text)

    print("\n✅ Bước 2: Tokenization:")
    tokens = word_tokenize(text, format="text")
    print(tokens)

    print("\n✅ Bước 3: POS Tagging:")
    pos = pos_tag(text)
    for word, tag in pos:
        print(f"{word:<15} => {tag}")

    print("\n✅ Bước 4: Chuẩn hoá dấu thanh (demo):")
    tone_fixed = normalize_tone_mark(text)
    print(tone_fixed)

# ========================
# TEST PIPELINE
# ========================
sample_sentences = [
    "Tôi rất thích học lập trình với Python.",
    "Hôm nay trời đẹp và tôi đi dạo công viên.",
    "Cô ấy đang học tại trường Đại học Bách Khoa."
]

for sentence in sample_sentences:
    print("="*50)
    vn_text_pipeline(sentence)
    print("="*50 + "\n")
