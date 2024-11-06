from database.consumer import Consumer
import os
import pathlib
from psycopg2.sql import SQL
from datetime import datetime

class Migrator(Consumer):

    versioncontroltable = 'schema_change_log'
    vctschema = '(version int primary key, comment varchar, dateapplied timestamp not null, sql varchar not null)'
    migrationsfolderpath = pathlib.Path(__file__).parent.resolve() / 'sql' / 'migrations'

    def getDatabaseVersion(self):
        with self.connection as con, con.cursor() as cur:
            query = 'select max(version) as currentversion from {}'.format(self.versioncontroltable)
            cur.execute(query)
            result = cur.fetchone()['currentversion']
            return result if result else 0

    def isVersionControlled(self):
        query = "select * from information_schema.tables where table_name = %s"
        with self.connection as con, con.cursor() as cur:
            cur.execute(query, (self.versioncontroltable, ))
            result = cur.fetchall()
            return result

    def initializeDatabase(self):

        def crateVersionControlTable():
            query = "create table {} {} ;".format(self.versioncontroltable, self.vctschema)
            with self.connection as con, con.cursor() as cur:
                cur.execute(query)

        def nukeSchema():
            query = "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
            with self.connection as con, con.cursor() as cur:
                cur.execute(query)

        if not self.isVersionControlled():
            nukeSchema()
            crateVersionControlTable()

        #migrates database if migration scripts are supplied
        self.migrate()

    def migrate(self):

        def parseVersion(filename: str):
            version = int(filename.split('.sql')[0])
            return version
        
        databaseversion = self.getDatabaseVersion()

        files = os.listdir(self.migrationsfolderpath)
        newMigrations = filter(lambda n:  parseVersion(n) > databaseversion, files)
        newMigrations = sorted(newMigrations, key=lambda n: parseVersion(n))
        migrationSuccesful = True
        for file in newMigrations:
            with self.connection as con, con.cursor() as cur:
                try:
                    with open(self.migrationsfolderpath / file, 'r') as migrationfile:
                        migrationsql = migrationfile.read()
                        version = parseVersion(file)
                        loggingsql = "insert into {} (version, sql, dateapplied) values(%s, %s, %s);".format(self.versioncontroltable)
                        cur.execute(migrationsql + ' ' + loggingsql, (version, migrationsql, datetime.now()))
                except Exception as e:
                    migrationSuccesful = False
                    print('Migration not successful for {}'.format(file))
                    raise(e)
                
        if newMigrations and migrationSuccesful: print("Migration successful!")