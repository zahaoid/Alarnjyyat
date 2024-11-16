from psycopg2.sql import SQL, Identifier, Composed
from database.consumer import Consumer

# this class assumes that all string inputs are not sanitized
#each row returned from a query is a dictionary, muliple rows are returned as an array of dictionaries like this: [{}, {}, {}]
#inputs are preprocessed, raw, primitive types, un-nested data that inserts naturally into database tables with minimum processing
#lists and tuples of primitive type elements are allowed but dictionaries are not
class Querier(Consumer):


    ############################ DATA RETRIVAL ###########################


    # this returns a boolean to ensure security
    def doesValueExist(self, table: str, column:str, value) -> bool:
        query = "SELECT %s FROM {} WHERE %s = %s;"
        with self.connection as con, con.cursor() as cur:
            cur.execute(SQL(query).format(Identifier(table)), (column, column, value))
            result = cur.fetchone()
        return True if result else False
        
    def getEntry(self, entryid: int) -> dict:
        query = "SELECT * FROM entries WHERE id = %s"
        with self.connection as con, con.cursor() as cur:
            cur.execute(query, (entryid, ))
            entry = cur.fetchone()

        if entry:
            self.appendPropertiesToBaseEntry(baseEntry=entry)
            return entry

    def getAllEntries(self, desc = True, limit=None, isapproved = True) -> list[dict]:
        approvalArg = 'NOT' if isapproved else ''
        orderingArg = 'DESC' if desc else 'ASC'

        #this way of formatting is safe from injections because we are not passing inputs to the query directly
        query = "SELECT * FROM entries WHERE approvedby IS {} NULL ORDER BY timestamp {} ".format(approvalArg, orderingArg)
        subquery = 'LIMIT %s;'
        args = (query + subquery, (limit, )) if limit else query
        with self.connection as con, con.cursor() as cur:
            cur.execute(args)
            entries = cur.fetchall()
        for entry in entries:
            self.appendPropertiesToBaseEntry(baseEntry=entry)
        return entries
    
    def getListOfCorrections(self, entryid) -> list[dict]:
        with self.connection as con, con.cursor() as cur:
            query = "SELECT correction FROM corrections WHERE entryid = %s;"
            cur.execute(query, (entryid, ))
            corrections = cur.fetchall()
        return corrections
        
    def getListOfContexts(self, entryid) -> list[dict]:
        with self.connection as con, con.cursor() as cur:
            query = "SELECT trcontext, arcontext FROM contexts WHERE entryid = %s;"
            cur.execute(query, (entryid, ))
            contexts = cur.fetchall()
        return contexts


    
    def getUser(self, username: str) -> dict:
        query = "SELECT * FROM users WHERE username = %s"
        with self.connection as con, con.cursor() as cur:
            cur.execute(query, (username, ))
            result = cur.fetchall()
            assert len(result) <= 1 #checks for injections and inconsistency
            return result[0] if result else None



    ######################## DATA MANIPULATION ##########################


    def acceptEntry(self, entryid: int, approvedby: str):
        query = "UPDATE entries SET approvedby = %s WHERE id = %s;"
        with self.connection as con, con.cursor() as cur:
            cur.execute(query, (approvedby, entryid))



    ##################### DATA CREATION ##################################

    def addUser(self, username: str, passwordhash: str, email: str):
         query = "INSERT INTO users (username, email, passwordhash) VALUES (%s, %s, %s);"
         values = (username, email, passwordhash)
         with self.connection as con, con.cursor() as cur:
            cur.execute(query, values)
       
    
    def addEntry(self, origin: str, original: str, translationese: str, submitter: str, corrections: list[str], contexts: list[tuple[str, str]], category: str, elaboration: str ):
        query = "INSERT INTO entries (origin, original, translationese, submitter, category, elaboration) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"
        values = (origin, original, translationese, submitter, category, elaboration)
        with self.connection as con, con.cursor() as cur:
            cur.execute(query, values)
            entryid = cur.fetchone()['id']

        for correction in corrections:
            self.addCorrection(entryid=entryid, correction=correction)

        # TRCONTEXT FIRST THEN ARCONTEXT!!
        for context in contexts:
            trcontext = context[0]
            arcontext = context[1]
            if trcontext and arcontext:
                self.addContext(entryid=entryid, arcontext=arcontext, trcontext=trcontext)


    #inputs are raw non-nested data
    def addContext(self, entryid: int, trcontext: str, arcontext: str):
        with self.connection as con, con.cursor() as cur:
            query = "insert into contexts (entryid, trcontext, arcontext) values(%s, %s, %s)"
            values = (entryid, trcontext, arcontext)
            cur.execute(query, values)

    #inputs are raw data
    def addCorrection(self, entryid: int, correction: list[str]):
        with self.connection as con, con.cursor() as cur:
            query = "INSERT INTO corrections (entryid, correction) VALUES (%s, %s);"
            values = (entryid, correction)
            cur.execute(query, values)


    ######################## HELPER FUNCTIONS ###########################

    #mutates entry's dictionary
    def appendPropertiesToBaseEntry(self, baseEntry):
        entryid = baseEntry['id']
        baseEntry['corrections'] = self.getListOfCorrections(entryid=entryid)
        baseEntry['contexts'] = self.getListOfContexts(entryid=entryid)