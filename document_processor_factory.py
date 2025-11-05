from document_processors import *
from i_document_processor import DocumentProcessor


class DocumentProcessorFactory:
    @staticmethod
    def get_processor(document_type: str) -> DocumentProcessor:
        doc_type = document_type.lower()

        if "irsaliye" in doc_type or "dispatch" in doc_type:
            return DispatchNoteProcessor()
        elif "fatura" in doc_type or "invoice" in doc_type:
            return InvoiceProcessor()
        elif "fiş" in doc_type or "receipt" in doc_type:
            return ReceiptProcessor()
        else:
            raise ValueError(f"Bilinmeyen belge türü: {document_type}")