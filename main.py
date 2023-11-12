from db import DocumentsDB


if __name__ == '__main__':
    bazka = DocumentsDB(db_filename='documents.db')
    bazka.add_document('Dokument nr 1', ['tag1'])
    bazka.add_document('Dokument nr 2', ['tag1', 'tag2'], 'Jakis dokument')
    bazka.get_all_documents_with_tags()
    bazka.get_tags('Dokument nr 1')