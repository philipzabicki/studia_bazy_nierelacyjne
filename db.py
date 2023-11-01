import sqlite3


def connect(f):
    def wrapper(*args):
        args[0].connection = sqlite3.connect(args[0].fname)
        ret = f(*args)
        args[0].connection.commit()
        args[0].connection.close()
        return ret
    return wrapper


class DocumentsDB:
    @connect
    def __int__(self, db_filename='documents.db'):
        self.fname = db_filename
        self.connection = None