# search_engine

### indexing
To run the indexing script, the database config files and certificates need to be added. These have been removed for security purpose. The steps to do so are explained below. Once this is done, you can run the script through ```main.py```.

### Warning!
#### Before you can start the indexing, make sure the database is empty. This can be done by running db_nuke.py from ```indexing/database_population```. It will prompt a warning, which can be cleared by typing the table name (ArticleData) and pressing enter. 

1. The certificates need to be added in a folder called ```certs```. The folder needs to be in the following path:

```indexing/database_population/certs```

2. The database configuration needs to be added as a file called ```db.ini```. The file needs to be in the following path:

```indexing/database_population/db.ini```

3. The database only works with ssl certificates, ad the layour of the db.ini file is the following (fill of the parts within the {}-brackets, and remove the brackets.):

```
[postgres]
host = {server public IP}
port = {sever port}
user = postgres
password = {instance password}
database = postgres
sslmode = verify-ca
sslrootcert = server-ca.pem
sslcert = client-cert.pem
sslkey = client-key.pem
```

4. The current data input file is the file in ```indexing/data/article_data```. This needs to be replaced by a file in the exact same format for the code to work (tsv with all strings and date in format yyyy-mm-dd).

5. In order to write the output to disk, an output folder needs to be added in the following location:

```indexing/output/index_and_index_hash```
