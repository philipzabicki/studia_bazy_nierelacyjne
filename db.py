import sqlite3


def temp_connection(f):
    def wrapper(*args):
        print(f'DB connection call from {f.__name__}')
        # print(f'    connection: {args[0].connection}')
        try:
            args[0].cur = args[0].connection.cursor()
            print(f'args[0].cur {args[0].cur}')
        except Exception as e:
            print(e)
            args[0].connection = sqlite3.connect(args[0].fname)
            args[0].cur = args[0].connection.cursor()
        ret = f(*args)
        print('Closing connection...')
        args[0].connection.commit()
        args[0].connection.close()
        return ret
    return wrapper


class DocumentsDB:
    def __init__(self, sql_script_filename='init_db.sql', db_filename='documents.db'):
        self.fname = db_filename
        self.connection = sqlite3.connect(self.fname)
        self.cur = self.connection.cursor()
        with open(sql_script_filename) as f:
            self.connection.executescript(f.read())
        self.connection.commit()
        self.connection.close()

    def __str__(self):
        return f'SQLite database, filename: {self.fname}'

    def _check_connection(self):
        try:
            self.cur = self.connection.cursor()
            # print(f'{self.cur}')
        except Exception as e:
            # print(e)
            self.connection = sqlite3.connect(self.fname)
            self.cur = self.connection.cursor()

    def _add_new_tags(self, tag_list: list[str]):
        self._check_connection()
        ids = []
        seq = ','.join('?' * len(tag_list))
        print(f'tag_list: {tag_list}')
        for row in self.cur.execute(f'SELECT * \
                                            FROM tag \
                                            WHERE name IN ({seq});',
                                    (*tag_list,)):
            print(f'row: {row}')
            tag_list.remove(row[1])
            ids.append(row[0])
        for tag in tag_list:
            ids.append(self.add_tag(tag))
        return ids

    def _attach_tag(self, doc_id: int, tag_id: int) -> None:
        print(f'attach_tag: {type(tag_id)} to doc: {doc_id}')
        self._check_connection()
        self.cur.execute("INSERT INTO document_tag (document_id, tag_id) VALUES (?,?)",
                         (doc_id, tag_id))
        self.connection.commit()

    def add_tag(self, tag: str):
        print(f'adding tag: {tag}')
        self._check_connection()
        self.cur.execute("INSERT INTO tag (name) VALUES (?)",
                         (tag,))
        self.connection.commit()
        return self.cur.lastrowid

    def add_document(self, doc_name: str, tag_list: list[str], doc_description: str = None):
        self._check_connection()
        if doc_description is None:
            doc_description = 'Simple document '+doc_name

        self.cur.execute("INSERT INTO document (name, description) VALUES (?, ?)",
                         (doc_name, doc_description))
        self.connection.commit()
        doc_id = self.cur.lastrowid

        if tag_list is not None:
            tag_ids = self._add_new_tags(tag_list)
            for tag_id in tag_ids:
                self._attach_tag(doc_id, tag_id)

    def attach_tag(self, document_name: str, tag_name: str) -> None:
        '''print(f'attach_tag: {type(tag_id)} to doc: {doc_id}')
        self._check_connection()
        self.cur.execute("INSERT INTO document_tag (document_id, tag_id) VALUES (?,?)",
                         (doc_id, tag_id))
        self.connection.commit()'''

    def get_tags(self, document_name: str = None, order_by: str = 'id') -> list[tuple[int, str, None | str]]:
        self._check_connection()
        if document_name is None:
            print('All tags in db:')
            query = f'SELECT * \
                      FROM tag \
                      ORDER BY {order_by};'
        else:
            print(f'{document_name} tags in db:')
            query = f'SELECT t.id, t.name, t.description \
                      FROM document doc, tag t, document_tag dt \
                      WHERE doc.name = "{document_name}" AND dt.document_id = doc.id \
                      ORDER BY t.{order_by};'
        response = [tag for tag in self.cur.execute(query)]
        print(*response, sep="\n")
        return response

    def get_all_documents_with_tags(self, order_by: str = 'id') -> list[tuple[int, str, str, str, str, None | str]]:
        self._check_connection()
        query = f'SELECT doc.id, doc.created, doc.name, doc.description, t.name, t.description \
                  FROM document doc, tag t, document_tag dt \
                  WHERE dt.document_id = doc.id AND \
                        dt.tag_id = t.id \
                  ORDER BY doc.{order_by};'
        response = [doc for doc in self.cur.execute(query)]
        print(*response, sep="\n")
        return response
