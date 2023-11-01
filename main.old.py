import sqlite3


def connect(func):
    def wrapper():
        pass
    return wrapper


def create_db() -> bool:
    connection = sqlite3.connect("documents.db")
    if connection is None:
        return False
    #print(connection)
    with open("init_db.sql") as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()
    return True


def populate_with_data():
    connection = sqlite3.connect("documents.db")
    cur = connection.cursor()

    cur.execute("INSERT INTO tag (name, description) VALUES (?, ?)",
                ("tag_1",
                 "Description of tag 1")
                )
    tag_1_id = cur.lastrowid

    cur.execute("INSERT INTO tag (name) VALUES (?)",
                ("tag_2",)
                )
    tag_2_id = cur.lastrowid

    cur.execute("INSERT INTO document (name, description) VALUES (?, ?)",
                ("Document_1",
                 "Description of document 1")
                )
    doc_1_id = cur.lastrowid

    cur.execute("INSERT INTO document_tag (document_id, tag_id) VALUES (?,?)",
                (doc_1_id, tag_1_id))

    cur.execute("INSERT INTO document (name, description) VALUES (?, ?)",
                ("Document_2",
                 "Description of document 2")
                )
    doc_2_id = cur.lastrowid

    cur.execute("INSERT INTO document_tag (document_id, tag_id) VALUES (?,?)",
                (doc_2_id, tag_2_id))

    cur.execute("INSERT INTO document (name, description) VALUES (?, ?)",
                ("Document_3",
                 "Description of document 3")
                )
    doc_3_id = cur.lastrowid

    data = [
        (doc_3_id, tag_1_id),
        (doc_3_id, tag_2_id)
    ]
    cur.executemany("INSERT INTO document_tag (document_id, tag_id) VALUES (?,?)", data)

    connection.commit()
    connection.close()


def select_basic_data():
    connection = sqlite3.connect("documents.db")
    cur = connection.cursor()

    for row in cur.execute("SELECT * FROM tag ORDER BY id;"):
        print(row)

    for row in cur.execute("SELECT * FROM document ORDER BY id;"):
        print(row)

    for row in cur.execute("SELECT * FROM document_tag ORDER BY id;"):
        print(row)

    connection.close()


if __name__ == '__main__':
    create_db()
    populate_with_data()
    select_basic_data()