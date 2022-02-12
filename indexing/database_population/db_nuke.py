import psycopg2
import configparser
import os

answer = input("WARNING---this will delete the entire table---WARNING\ntype the table name to continue: ")
try:
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

    cursor.execute(f'DELETE FROM {answer};')
    cursor.execute(f"SELECT * FROM {answer}")
    output = cursor.fetchall()
    connection.commit()
    cursor.close()

    if len(output) == 0:
        print('Truncation successful')
    else:
        print('Truncation failed, try again')
except:
    print(f'Table {answer} does not exist. Re-run the script and try again.')

