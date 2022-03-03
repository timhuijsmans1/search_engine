def add_row(id, title, url, date, content, cursor, connection):
    values = f"'{id}', '{title}', '{url}', '{date}', '{content}'"
    insert = f'INSERT INTO retrieval_testArticle (document_id, title, url, publication_date, content) VALUES ({values});'
    cursor.execute(insert)
    connection.commit()
    return