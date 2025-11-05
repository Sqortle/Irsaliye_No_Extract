import re


class DispatchNoExtractor:
    IRSA_NO_PATTERNS = [
        # Ana 16 karakterlik numara formatı (Orijinal hali korundu, numara çekmek için)
        r'\b([A-Za-z][A-Za-z0-9]{2}[0-9]{13})\b',

        # e-İrsaliye / E-İRSALİYE (Türkçe 'İ')
       # r'(?:e[ -]İrsaliye|E[ -]İRSALİYE)',

       # r'(?:e[ -]İr|E[ -]İR).*'

        # e-Irsaliye / E-IRSALIYE (İngilizce 'I', OCR hatalarına karşı)
       # r'(?:e[ -]Irsaliye|E[ -]IRSALIYE)',

       # r'(?:e[ -]Ir|E[ -]IR).*'

        # e-Fatura / E-FATURA
       # r'(?:e[ -]Fatura|E[ -]FATURA)',

       # r'(?:e[ -]Fa|E[ -]FA).*'

        # GİRİŞ FİŞİ / Giriş Fişi (Türkçe ve İngilizce karakter toleranslı)
       # r'(?:GİRİŞ\sFİŞİ|Giriş\sFişi|GIRIS\sFISI)',

       # r'(?:GİR|GIR).*'
    ]

    def extract(self, raw_text: str) -> list[str]:

        found_numbers = set()
        text_lines = raw_text.splitlines()

        for pattern in self.IRSA_NO_PATTERNS:
            compiled_pattern = re.compile(pattern)

            for line in text_lines:
                # Metnin normalize edilmesi: Satır temizliği
                normalized_line = line.strip()

                # Satırın temizlenmiş hali üzerinden arama yapıyoruz
                matches = compiled_pattern.findall(normalized_line)

                for match in matches:
                    # Sadece grup yakalanmışsa (parantez içindeki kısım)
                    if isinstance(match, tuple):
                        found_numbers.add(match[0].strip())
                    else:
                        found_numbers.add(match.strip())

        return list(found_numbers)