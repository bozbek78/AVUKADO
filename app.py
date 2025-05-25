import gradio as gr
from PIL import Image
import easyocr
import json
import numpy as np

# JSON dosyasını oku
def load_json():
    with open("json_data.json", encoding="utf-8") as f:
        data = json.load(f)
    return data

json_data = load_json()
reader = easyocr.Reader(['tr'], gpu=False)

# Büro eşlemesi
def match_bureau(tck_code):
    for section, entries in json_data.items():
        for entry in entries:
            if tck_code.strip() in entry["code"]:
                return section, entry["bureau"], entry["duty"]
    return "Eşleşme bulunamadı", "Yok", []

# Görselden analiz yap
def analyze_image(image):
    # OCR
    result = reader.readtext(image)
    text = "\n".join([item[1] for item in result])

    matched_codes = []
    lines = text.split("\n")
    for line in lines:
        if "TCK" in line and any(char.isdigit() for char in line):
            words = line.split()
            for i, word in enumerate(words):
                if "TCK" in word and i + 1 < len(words):
                    matched_codes.append(words[i + 1].replace("(", "").replace(")", ""))

    sevk_list = []
    for code in matched_codes:
        section, bureau, duties = match_bureau(code)
        sevk_list.append(f"Olay, 5237 sayılı TCK {code} maddesi kapsamında değerlendirilmiştir.")

    bureau_result = ""
    if matched_codes:
        section, bureau, duties = match_bureau(matched_codes[0])
        bureau_result = f"Ankara Cumhuriyet Başsavcılığı İş Bölümünün {section} maddesi uyarınca görevli büro **{bureau}**’dur."

    olay_ozeti = "Bilgi bulunamadı."

    sevk_maddeleri = "\n• " + "\n• ".join(sevk_list) if sevk_list else "Veri yok."

    return f"""1. Kısa Olay Özeti:

{olay_ozeti}

2. Sevk Maddeleri:
{sevk_maddeleri}

3. Görevli Büro:

{bureau_result}
"""

# Arayüz
demo = gr.Interface(
    fn=analyze_image,
    inputs=gr.Image(type="numpy", label="Tutanak Görselini Yükleyin"),
    outputs=gr.Textbox(label="Analiz Sonucu (Olay Özeti + Sevk Maddeleri + Görevli Büro)")
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
