import pytesseract
import os
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance
import numpy as np
import cv2

# 1. Tesseract Motorunun Yolu
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

# 2. TESSDATA_PREFIX'i Ayarlama(türkçe desteği için)
TESSDATA_PATH = '/opt/homebrew/share/tessdata/'

#Poppler path
POPPLER_PATH = r'/opt/homebrew/bin'


class OcrEngine:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            #türkçe desteği otomatik gelmediyse ayarlama
            if 'TESSDATA_PREFIX' not in os.environ:
                os.environ['TESSDATA_PREFIX'] = TESSDATA_PATH

            cls._instance = super(OcrEngine, cls).__new__(cls)
            print(f"OCR Motoru başlatıldı (Singleton). TESSDATA_PREFIX ayarlandı.")
        return cls._instance

    def _clean_text(self, text: str) -> str:
        text = text.replace('\n', ' ')
        text = ' '.join(text.split())
        text = ' '.join(text.split())
        return text

    def extract_text(self, image_path: str) -> str:
        # Dosya tipini kontrol etme
        if image_path.lower().endswith('.pdf'):
            return self._extract_text_from_pdf(image_path)
        else:
            return self._extract_text_from_image(image_path)

    def _extract_text_from_image(self, image_path: str) -> str:
        try:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 1. Parlaklık Kontrolü
            mean_intensity = np.mean(gray)

            # Eşik değerleri
            T_SOLUK = 65
            T_PARLAK = 155

            if mean_intensity < T_SOLUK:
                fx_val = 1.5  # Yeniden boyutlandırmayı biraz azaltabiliriz
                contrast_enhance = 4.0
                sharpness_enhance = 5.0
                gray = cv2.resize(gray, None, fx=fx_val, fy=1.105, interpolation=cv2.INTER_LINEAR)
                print("Görüntü: KARANLIK/SOLUK Algılandı. Güçlü iyileştirme uygulanıyor.")

            elif mean_intensity > T_PARLAK:
                fx_val = 2.0
                contrast_enhance = 1.5 # Kontrastı çok artırmamaya çalış
                sharpness_enhance = 2.0
                gray = cv2.resize(gray, None, fx=fx_val, fy=1.105, interpolation=cv2.INTER_LINEAR)
                print("Görüntü: ÇOK PARLAK Algılandı. Dengeleyici iyileştirme uygulanıyor.")

            else:
                # Normal/Dengeli için İşlemler (Mevcut optimizasyonları kullan)
                fx_val = 1.6
                contrast_enhance = 3.5
                sharpness_enhance = 4.0
                print("Görüntü: NORMAL/DENGELİ Algılandı. Standart iyileştirme uygulanıyor.")
                gray = cv2.resize(gray, None, fx=fx_val, fy=1.0, interpolation=cv2.INTER_LINEAR)

            # Ortak Ön İşleme Adımları
            gray = cv2.medianBlur(gray, 3)

            # Adaptif threshold
            thresh = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                31, 7 # C değerini (son parametre) parlak/soluk duruma göre değiştirmek de bir optimizasyon olabilir
            )

            kernel = np.ones((2, 2), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

            pil_img = Image.fromarray(thresh)

            # Koşullu olarak belirlenen geliştirme katsayılarını kullanma
            enhancer_contrast = ImageEnhance.Contrast(pil_img)
            pil_img = enhancer_contrast.enhance(contrast_enhance)

            enhancer_sharpness = ImageEnhance.Sharpness(pil_img)
            pil_img = enhancer_sharpness.enhance(sharpness_enhance)

            config = "--oem 3 --psm 3"
            text = pytesseract.image_to_string(pil_img, lang='tur', config=config)

            return self._clean_text(text)

        except Exception as e:
            return f"Metin çıkarma hatası: {e}"


    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        full_text = []
        try:
            images = convert_from_path(pdf_path,
                                       dpi=400,
                                       poppler_path=POPPLER_PATH)

            for i, image in enumerate(images):
                img = np.array(image)
                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                gray = cv2.medianBlur(gray, 3)

                thresh = cv2.adaptiveThreshold(
                    gray, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    31, 10
                )

                # Morfolojik açma
                kernel = np.ones((1, 1), np.uint8)
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

                # PIL'e çevir
                pil_img = Image.fromarray(thresh)

                enhancer_contrast = ImageEnhance.Contrast(pil_img)
                pil_img = enhancer_contrast.enhance(2.0)

                enhancer_sharpness = ImageEnhance.Sharpness(pil_img)
                pil_img = enhancer_sharpness.enhance(2.5)

                config = "--oem 3 --psm 6"
                page_text = pytesseract.image_to_string(pil_img, lang='tur', config=config)

                full_text.append(f"--- Sayfa {i + 1} ---\n{page_text}")

            return "\n\n".join(full_text)

        except Exception as e:
            return f"Metin çıkarma hatası (PDF): İşleme sırasında hata oluştu: {e}"