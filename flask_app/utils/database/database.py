import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import datetime
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'

         # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT CURDATE()", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def about(self, nested=False):    
        query = """select concat(col.table_schema, '.', col.table_name) as 'table',
                          col.column_name                               as column_name,
                          col.column_key                                as is_key,
                          col.column_comment                            as column_comment,
                          kcu.referenced_column_name                    as fk_column_name,
                          kcu.referenced_table_name                     as fk_table_name
                    from information_schema.columns col
                    join information_schema.tables tab on col.table_schema = tab.table_schema and col.table_name = tab.table_name
                    left join information_schema.key_column_usage kcu on col.table_schema = kcu.table_schema
                                                                     and col.table_name = kcu.table_name
                                                                     and col.column_name = kcu.column_name
                                                                     and kcu.referenced_table_schema is not null
                    where col.table_schema not in('information_schema','sys', 'mysql', 'performance_schema')
                                              and tab.table_type = 'BASE TABLE'
                    order by col.table_schema, col.table_name, col.ordinal_position;"""
        results = self.query(query)
        if nested == False:
            return results

        table_info = {}
        for row in results:
            table_info[row['table']] = {} if table_info.get(row['table']) is None else table_info[row['table']]
            table_info[row['table']][row['column_name']] = {} if table_info.get(row['table']).get(row['column_name']) is None else table_info[row['table']][row['column_name']]
            table_info[row['table']][row['column_name']]['column_comment']     = row['column_comment']
            table_info[row['table']][row['column_name']]['fk_column_name']     = row['fk_column_name']
            table_info[row['table']][row['column_name']]['fk_table_name']      = row['fk_table_name']
            table_info[row['table']][row['column_name']]['is_key']             = row['is_key']
            table_info[row['table']][row['column_name']]['table']              = row['table']
        return table_info



    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        # Delete old tables if purge is true
        if purge:
            self.query('DROP TABLE IF EXISTS cards')
            self.query('DROP TABLE IF EXISTS columns')
            self.query('DROP TABLE IF EXISTS boardusers')
            self.query('DROP TABLE IF EXISTS boards')
            self.query('DROP TABLE IF EXISTS users')

        with open(data_path + 'create_tables/users.sql', 'r') as file:
            sql_query = file.read()
            self.query(sql_query)

        # Execute each .sql file in the database/create_tables
        with open(data_path + 'create_tables/boards.sql', 'r') as file:
            # read sql file
            sql_query = file.read()
            # use read file as query
            self.query(sql_query)

        # Execute each .sql file in the database/create_tables
        with open(data_path + 'create_tables/boardusers.sql', 'r') as file:
            # read sql file
            sql_query = file.read()
            # use read file as query
            self.query(sql_query)

        # Execute each .sql file in the database/create_tables
        with open(data_path + 'create_tables/columns.sql', 'r') as file:
            # read sql file
            sql_query = file.read()
            # use read file as query
            self.query(sql_query)

        # Execute each .sql file in the database/create_tables
        with open(data_path + 'create_tables/cards.sql', 'r') as file:
            # read sql file
            sql_query = file.read()
            # use read file as query
            self.query(sql_query)


    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):

        # Construct the column part of the INSERT statement
        cols = ', '.join(columns)
        
        # Construct the values part of the INSERT statement with placeholders for parameters
        vals = ', '.join(['%s'] * len(columns))
        
        # Create INSERT statement
        insert_statement = f'INSERT IGNORE INTO {table} ({cols}) VALUES ({vals})'
        
        # Execute the INSERT statement for each row of parameters
        for i in parameters:
            self.query(insert_statement, i)


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user'):
        existing_user = self.query("SELECT email FROM users WHERE email = %s", (email,))
        if existing_user:
            return {'success': 0, 'message': 'User already exists.'}

        # Encrypt the password
        encrypted = self.onewayEncrypt(password)

        # Insert the new user
        self.insertRows('users', ['email', 'password', 'role'], [[email, encrypted, role]])
        
        return {'success': 1, 'message': 'User created successfully.'}


    def authenticate(self, email='me@email.com', password='password'):
        encrypted = self.onewayEncrypt(password)

        auth = self.query("SELECT password FROM users WHERE email = %s", (email, ))

        if auth:
            if encrypted == auth[0]['password']:
                return {'success': 1, 'message': 'User authenticated successfully'}
            return {'success': 0, 'message': 'Failed to successfully authenticate user'}

        return {'success': 0, 'message': 'Failed to successfully authenticate user'}

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message
    

#######################################################################################
# BOARD RELATED
#######################################################################################
    def create_board(self, project_name, member_emails):
        insert_query = "INSERT INTO boards (name) VALUES (%s)"
        self.query(insert_query, [project_name])
        

        # Get the last inserted board_id
        board_id = self.query("SELECT board_id FROM boards WHERE name= %s",[project_name])[0]['board_id']

        # Insert default columns
        columns = ["To Do", "Doing", "Completed"]
        for column_name in columns:
            column_query = "INSERT INTO columns (board_id, column_name) VALUES (%s, %s)"
            print(board_id)
            print(column_name)
            self.query(column_query, [board_id, column_name])


        # Inserting into 'boardusers'
        for email in member_emails:
            insert_user_query = "INSERT INTO boardusers (board_id, email) VALUES (%s, %s)"
            self.query(insert_user_query, (board_id, email))

        return board_id 
    
    def get_user_boards(self, user_email):
        query = """
        SELECT b.name, b.board_id
        FROM boards b
        JOIN boardusers bu ON b.board_id = bu.board_id
        WHERE bu.email = %s;
        """
        # Execute the query with the user_email as a parameter
        results = self.query(query, [user_email]) 

        return results
    
    def get_columns_by_board(self, board_id):
        # This method retrieves all columns associated with a specific board
        query = "SELECT * FROM columns WHERE board_id = %s"
        columns = self.query(query, [board_id])

        return columns
    def get_cards_by_column(self, column_id):
        query = "SELECT * FROM cards WHERE column_id = %s"
        return self.query(query, (column_id))
    
    def insert_card(self, column_id, content):
        query = "INSERT INTO cards (column_id, card_content) VALUES (%s, %s)"
        x = self.query(query, [column_id, content])

    def insert_column(self, board_id,name):
        query = "INSERT INTO columns (board_id,column_name) VALUES (%s, %s)"
        self.query(query, [board_id,name])

    def update_card_position(self, card_id, new_column_id):
        print(card_id)
        print(new_column_id)
        try:
            query = "UPDATE cards SET column_id = %s WHERE card_id = %s"
            parameters = (new_column_id, card_id)
            self.query(query, parameters)
            return True
        except Exception as e:
            print("Error updating card position:", e)
            return False
