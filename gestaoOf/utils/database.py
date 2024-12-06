import pyodbc

def get_sql_server_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=192.168.120.9;'
        'DATABASE=PHCTRI;'
        'UID=estagio;'
        'PWD=3stAg10..;'
    )
    return conn
