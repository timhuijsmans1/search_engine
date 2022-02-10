def add_row(id, title, url, body, date, cursor, connection):
    values = f"'{id}', '{title}', '{body}', '{url}', '{date}'"
    insert = f'INSERT INTO ArticleData (ID, title, body, url, date) VALUES ({values});'
    cursor.execute(insert)
    connection.commit()
    return