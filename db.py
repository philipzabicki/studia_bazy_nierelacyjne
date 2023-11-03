import sqlite3


def temp_connection(f):
    def wrapper(*args):
        print(f'Connecting to {args[0].fname}')
        print(f'    connection: {args[0].connection}')
        if not args[0].connection:
            args[0].connection = sqlite3.connect(args[0].fname)
            args[0].cur = args[0].connection.cursor()
        ret = f(*args)
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

    @temp_connection
    def _add_new_tags(self, tag_list: list[str]):
        ids = []
        seq = ','.join('?' * len(tag_list))
        for row in self.cur.execute(f'SELECT * FROM tag WHERE id IN ({seq});',
                                    (*tag_list,)):
            tag_list.remove(row['name'])
            ids.append(row['id'])
        for tag in tag_list:
            ids.append(self.add_tag(tag))
        return ids

    @temp_connection
    def add_tag(self, tag: str):
        self.cur.execute("INSERT INTO tag (name) VALUES (?)",
                         (tag,))
        return self.cur.lastrowid

    @temp_connection
    def add_document(self, doc_name: str, tag_list: list[str], doc_description: str = None):
        if doc_description is None:
            doc_description = 'Simple document '+doc_name

        self.cur.execute("INSERT INTO document (name, description) VALUES (?, ?)",
                         (doc_name, doc_description))
        doc_id = self.cur.lastrowid

        if tag_list is not None:
            tag_ids = self._add_new_tags(tag_list)
            for tag_id in tag_ids:
                self.attach_tag(doc_id, tag_id)

    @temp_connection
    def attach_tag(self, doc_id, tag_id):
        self.cur.execute("INSERT INTO document_tag (document_id, tag_id) VALUES (?,?)",
                         (doc_id, tag_id))

    @temp_connection
    def show_all_documents(self, order_by: str = 'id'):
        for row in self.cur.execute(f'SELECT * FROM tag ORDER BY {order_by};'):
            print(row)
