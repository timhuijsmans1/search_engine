import psycopg2
import configparser
import os

def connect(config_path, cert_path):
    config = configparser.ConfigParser()
    config.read(config_path)

    config = config['postgres']
    connection = psycopg2.connect(
        host = config['host'],
        port = config['port'],
        user = config['user'],
        password = config['password'],
        database = config['database'],
        sslmode = config['sslmode'],
        sslrootcert = os.path.join(cert_path, config['sslrootcert']),
        sslcert = os.path.join(cert_path, config['sslcert']),
        sslkey = os.path.join(cert_path, config['sslkey']))

    cursor = connection.cursor()

    return connection, cursor