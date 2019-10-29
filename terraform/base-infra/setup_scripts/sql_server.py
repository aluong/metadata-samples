import pyodbc

#################### Insert Information ######################

SQL_SERVER = '<Insert SQL Server name>.database.windows.net'
SQL_DB_NAME = '<Insert SQL DB name>'
SQL_DW_NAME = '<Insert SQL DW name'
USERNAME = '<Insert SQL Server Username>'
PASSWORD = '<Insert SQL Server Password>'

##############################################################

def establish_connection(database):
    try:
        connection = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server}; Server=%s;Database=%s;uid=%s;pwd=%s;" % 
                    (
                        SQL_SERVER,
                        database,
                        USERNAME,
                        PASSWORD
                    ), autocommit=True)
        return connection

    except Exception as error:
        print("Could not connect:", error)
    

def execute(cursor, filename):
    command = ""

    for line in open(filename):
        if line.strip() == "GO":
            print("Command: ", command)
            cursor.execute(command)
            command = ""
        else:
            command += line

def setup_sql_db():
    connection = establish_connection(SQL_DB_NAME)
    cursor = connection.cursor()
    execute(cursor, "./sql_files/setup_sql_db.sql")

def setup_sql_dw():
    connection = establish_connection(SQL_DW_NAME)
    execute(connection, "./sql_files/setup_sql_dw.sql")

setup_sql_db()
setup_sql_dw()