import psycopg2
from psycopg2 import extras
from psycopg2.sql import SQL, Identifier, Composed

# this class assumes that all string inputs are not sanitized
class Querier():

    def __init__(self, database: str, user :str, password, port: int, host:str) -> None:
        self.connection = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        self.cursor = self.connection.cursor(cursor_factory=extras.RealDictCursor)
    
    def doesValueExist(self, table: str, column:str, value):
        query = "SELECT %s FROM {} WHERE %s = %s;"
        self.cursor.execute(SQL(query).format(Identifier(table)), (column, column, value))
        result = self.cursor.fetchall()
        return result
    
    def getAllEntries(self, desc = True, limit=None, isapproved = True):
        base = "SELECT * FROM entries WHERE approvedby IS {} NULL ".format('NOT' if isapproved else '')
        osubquery = 'ORDER BY timestamp {} '.format ('DESC' if desc else 'ASC')
        lsubquery = 'LIMIT {};'.format(limit)
        query = base + osubquery + (lsubquery if limit else '')
        self.cursor.execute(query)
        entries = self.cursor.fetchall()
        
        for entry in entries:
            query = "SELECT correction FROM corrections WHERE entryid = %s;"
            self.cursor.execute(query, (entry['id'], ))
            corrections = list(map(lambda c: c['correction'], self.cursor.fetchall()))
            entry['corrections'] = corrections
        return entries
    
    def getEntry(self, entryid: int):
        query = "SELECT * FROM entries WHERE id = %s"
        self.cursor.execute(query, (entryid, ))
        entry = self.cursor.fetchone()

        if entry:
            query = "SELECT correction FROM corrections WHERE entryid = %s;"
            self.cursor.execute(query, (entry['id'], ))
            corrections = list(map(lambda c: c['correction'], self.cursor.fetchall()))
            entry['corrections'] = corrections
            return entry
        
    def acceptEntry(self, entryid: int, approvedby: str):
        query = "UPDATE entries SET approvedby = %s WHERE id = %s;"
        self.cursor.execute(query, (approvedby, entryid))
        self.connection.commit()

    
    def getUser(self, username: str):
        query = "SELECT * FROM users WHERE username = %s"
        self.cursor.execute(query, (username, ))
        result = self.cursor.fetchall()
        assert len(result) <= 1 #checks for injections and inconsistency
        return result[0] if result else None


    def addUser(self, user_info: dict):
         query = "INSERT INTO users (username, email, passwordhash) VALUES (%s, %s, %s);"
         values = (user_info['username'], user_info['email'], user_info['passwordhash'])
         self.cursor.execute(query, values)
         self.connection.commit()
       
    def addEntry(self, entry_info : dict):
        query = "INSERT INTO entries (origin, original, translationese, submitter) VALUES (%s, %s, %s, %s) RETURNING id;"
        values = (entry_info['origin'], entry_info['original'], entry_info['translationese'], entry_info['submitter'])
        self.cursor.execute(query, values)
        entryid = self.cursor.fetchone()['id']

        for correction in entry_info['corrections']:
            query = "INSERT INTO corrections (entryid, correction) VALUES (%s, %s);"
            values = (entryid, correction)
            self.cursor.execute(query, values)

        self.connection.commit()