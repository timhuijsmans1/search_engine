create_table_command = "CREATE TABLE ArticleData (" \
                       "ID int NOT NULL PRIMARY KEY," \
                       "title TEXT," \
                       "body TEXT," \
                       "url TEXT," \
                       "date DATE" \
                       ");"

# Create our table (Only do once)
def create_table(table_schema, connection, cursor):
    cursor.execute(table_schema)
    connection.commit()
    cursor.close()