from abc import ABC, abstractmethod
from ocr_engine import OcrEngine


class DocumentProcessor(ABC):
    def _get_cleaned_text(self, file_path: str) -> str:
        engine = OcrEngine()
        raw_text = engine.extract_text(file_path)

        cleaned_text = engine._clean_text(raw_text)
        return cleaned_text

    @abstractmethod
    def process_document(self, file_path: str) -> str:
        pass