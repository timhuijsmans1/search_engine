# search_engine

### indexing
To run the indexing script, the database config files and certificates need to be added. These have been removed for security purpose.

The certificates need to be added in a folder called ```certs```. The folder needs to be in the following path:

```indexing/database_population/certs```

The database configuration needs to be added as a file called ```db.ini```. The file needs to be in the following path:

```indexing/database_population/db.ini```

The database only works with ssl certificates, ad the layour of the db.ini file is the following:

```
[postgres]
host = [server public IP]
port = [sever port]
user = postgres
password = [instance password]
database = postgres
sslmode = verify-ca
sslrootcert = server-ca.pem
sslcert = client-cert.pem
sslkey = client-key.pem
```

The current data input file is the file in ```indexing/data/article_data```. This needs to be replaced by a file in the exact same format for the code to work (tsv with all strings and date in format yyyy-mm-dd).

In order to write the output to disk, an output folder needs to be added in the following location:

```indexing/output/index_and_index_hash```
