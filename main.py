import os
from document_processor_factory import DocumentProcessorFactory
from ocr_engine import OcrEngine


# İmaj dosyalarının bulunduğu klasör (bu klasör proje dizininde olcak)
INPUT_DIR = "input_docs"
# Desteklenen dosya uzantıları
SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.pdf')

def determine_doc_type(filename: str) -> str:
    name_lower = filename.lower()

    # Gerçek projede bu mantık Görüntü işlenerek gelcek fakat şu anda o kısımları çekemedim
    if "irsaliye" in name_lower or "dispatch" in name_lower:
        return "irsaliye"
    elif "fatura" in name_lower or "invoice" in name_lower:
        return "fatura"
    elif "fis" or "kabul" in name_lower or "receipt" in name_lower:
        return "fiş"
    else:
        return ""


def run_pipeline():
    print("--- 1. Proje Başlangıcı ---")

    # Singleton'ın tek bir örnek oluşturduğunu doğrulama
    engine1 = OcrEngine()
    engine2 = OcrEngine()
    if engine1 is engine2:
        print("OCR Motoru (Singleton) başarıyla başlatıldı ve tek örnektir.")
    else:
        print("Singleton hatası!")
        return

    # Klasör kontrolü
    if not os.path.exists(INPUT_DIR):
        print(f"UYARI: '{INPUT_DIR}' klasörü bulunamadı. Lütfen oluşturun ve içine dosyaları koyun.")
        # Klasörü oluşturma
        os.makedirs(INPUT_DIR)
        return

    print(f"\n--- 2. '{INPUT_DIR}' Klasörü Taranıyor ---")

    results = []

    # Klasördeki tüm dosyaları çekip işleme alma
    for filename in os.listdir(INPUT_DIR):
        file_path = os.path.join(INPUT_DIR, filename)

        # Sadece dosyaları ve desteklenen uzantıları kontrol et
        if os.path.isfile(file_path) and filename.lower().endswith(SUPPORTED_EXTENSIONS):

            # Belge Türünü Belirleme
            doc_type = determine_doc_type(filename)
            print(f"-> Dosya: {filename}, Belge Türü: {doc_type}")

            try:
                processor = DocumentProcessorFactory.get_processor(doc_type)

                processing_result = processor.process_document(file_path)

                results.append((filename, doc_type, processing_result))

            except ValueError as e:
                print(f"HATA: {e} - Dosya atlanıyor.")
            except Exception as e:
                print(f"BEKLENMEYEN HATA işlenirken {filename}: {e}")

    print("\n--- 3. İşlem Tamamlandı ---")

    if not results:
        print("İşlenecek dosya bulunamadı veya tümü hata verdi.")
        return

    # Sonuçları Konsola Yazdırma ve Kaydetme
    print("\n\n--- SONUÇLAR ---")
    output_filename = "irsaliye_no_sonuclari.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("Dosya Adı | Belge Türü | Çıkarılan Bilgi\n")
        f.write("-" * 50 + "\n")

        for name, doc_type, result in results:
            output_line = f"{name} | {doc_type} | {result}\n"
            print(output_line, end='')
            f.write(output_line)

    print(f"\n✔ Tüm sonuçlar '{output_filename}' dosyasına kaydedildi.")


if __name__ == "__main__":
    run_pipeline()