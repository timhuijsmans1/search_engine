def add_row(id, title, url, date, cursor, connection):
    values = f"'{id}', '{title}', '{url}', '{date}'"
    insert = f'INSERT INTO retrieval_article (document_id, title, url, publication_date) VALUES ({values});'
    cursor.execute(insert)
    connection.commit()
    return