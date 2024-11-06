from database.querier import Querier
from database.migrator import Migrator
from config import Config
from psycopg2 import extras, connect
from psycopg2.extras import RealDictConnection

conf = Config.DATABASE
connection = connect(database=conf['database'], user=conf['user'], password=conf['password'], host=conf['host'], port=conf['port'], connection_factory=RealDictConnection)

migrator = Migrator(connection=connection)
migrator.initializeDatabase()

qr = Querier(connection=connection)