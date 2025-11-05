from dispatch_no_extractor import DispatchNoExtractor
from i_document_processor import DocumentProcessor

class ReceiptProcessor(DocumentProcessor):
    def process_document(self, file_path: str) -> str:
        cleaned_text = self._get_cleaned_text(file_path)

        extractor = DispatchNoExtractor()

        irsaliye_nos = extractor.extract(cleaned_text)

        if irsaliye_nos:
            return f": {', '.join(irsaliye_nos)}"
        else:
            return "İrsaliye No bulunamadı."


class InvoiceProcessor(DocumentProcessor):
    def process_document(self, file_path: str) -> str:
        cleaned_text = self._get_cleaned_text(file_path)

        extractor = DispatchNoExtractor()
        numbers = extractor.extract(cleaned_text)

        if numbers:
            return f": {', '.join(numbers)}"
        else:
            return f"İşlenen Fatura ({file_path}): Numara bulunamadı."


class DispatchNoteProcessor(DocumentProcessor):
    def process_document(self, file_path: str) -> str:
        cleaned_text = self._get_cleaned_text(file_path)

        extractor = DispatchNoExtractor()

        irsaliye_nos = extractor.extract(cleaned_text)

        if irsaliye_nos:
            return f": {', '.join(irsaliye_nos)}"
        else:
            return "İrsaliye No bulunamadı."