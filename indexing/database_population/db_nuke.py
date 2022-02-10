import psycopg2
import configparser
import os

answer = input("WARNING---this will delete the entire table---WARNING\ntype the table name to continue: ")
table_name = 'ArticleData'

if answer == table_name:

    config = configparser.ConfigParser()
    config.read('db.ini')

    config = config['postgres']
    connection = psycopg2.connect(
        host = config['host'],
        port = config['port'],
        user = config['user'],
        password = config['password'],
        database = config['database'],
        sslmode = config['sslmode'],
        sslrootcert = os.path.join('certs', config['sslrootcert']),
        sslcert = os.path.join('certs', config['sslcert']),
        sslkey = os.path.join('certs', config['sslkey']))

    cursor = connection.cursor()

    cursor.execute(f'DELETE FROM {table_name};')
    connection.commit()
    cursor.close()

    print('Truncation successful')
else:
    pass

