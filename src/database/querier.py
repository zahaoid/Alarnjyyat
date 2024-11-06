from psycopg2.sql import SQL, Identifier, Composed
from database.consumer import Consumer

# this class assumes that all string inputs are not sanitized
class Querier(Consumer):


    def doesValueExist(self, table: str, column:str, value):
        query = "SELECT %s FROM {} WHERE %s = %s;"
        with self.connection as con, con.cursor() as cur:
            cur.execute(SQL(query).format(Identifier(table)), (column, column, value))
            result = cur.fetchall()
            return result
    
    def getAllEntries(self, desc = True, limit=None, isapproved = True):
        base = "SELECT * FROM entries WHERE approvedby IS {} NULL ".format('NOT' if isapproved else '')
        osubquery = 'ORDER BY timestamp {} '.format ('DESC' if desc else 'ASC')
        lsubquery = 'LIMIT {};'.format(limit)
        query = base + osubquery + (lsubquery if limit else '')
        with self.connection as con, con.cursor() as cur:
            cur.execute(query)
            entries = cur.fetchall()
        
            for entry in entries:
                query = "SELECT correction FROM corrections WHERE entryid = %s;"
                cur.execute(query, (entry['id'], ))
                corrections = list(map(lambda c: c['correction'], cur.fetchall()))
                entry['corrections'] = corrections
            return entries
    
    def getEntry(self, entryid: int):
        query = "SELECT * FROM entries WHERE id = %s"
        with self.connection as con, con.cursor() as cur:
            cur.execute(query, (entryid, ))
            entry = cur.fetchone()

            if entry:
                query = "SELECT correction FROM corrections WHERE entryid = %s;"
                cur.execute(query, (entry['id'], ))
                corrections = list(map(lambda c: c['correction'], cur.fetchall()))
                entry['corrections'] = corrections
                return entry
        
    def acceptEntry(self, entryid: int, approvedby: str):
        query = "UPDATE entries SET approvedby = %s WHERE id = %s;"
        with self.connection as con, con.cursor() as cur:
            cur.execute(query, (approvedby, entryid))


    
    def getUser(self, username: str):
        query = "SELECT * FROM users WHERE username = %s"
        with self.connection as con, con.cursor() as cur:
            cur.execute(query, (username, ))
            result = cur.fetchall()
            assert len(result) <= 1 #checks for injections and inconsistency
            return result[0] if result else None


    def addUser(self, user_info: dict):
         query = "INSERT INTO users (username, email, passwordhash) VALUES (%s, %s, %s);"
         values = (user_info['username'], user_info['email'], user_info['passwordhash'])
         with self.connection as con, con.cursor() as cur:
            cur.execute(query, values)
       
    def addEntry(self, entry_info : dict):
        query = "INSERT INTO entries (origin, original, translationese, submitter) VALUES (%s, %s, %s, %s) RETURNING id;"
        values = (entry_info['origin'], entry_info['original'], entry_info['translationese'], entry_info['submitter'])
        with self.connection as con, con.cursor() as cur:
            cur.execute(query, values)
            entryid = cur.fetchone()['id']

            for correction in entry_info['corrections']:
                query = "INSERT INTO corrections (entryid, correction) VALUES (%s, %s);"
                values = (entryid, correction)
                cur.execute(query, values)
