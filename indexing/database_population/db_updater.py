import datetime
import time

def add_row(id, title, url, date, content, cursor, connection):
    try:
        values = f"'{id}', '{title}', '{url}', '{date}', '{content}'"
        insert = f'INSERT INTO retrieval_testArticle (document_id, title, url, publication_date, content) VALUES ({values});'
        cursor.execute(insert)
        connection.commit()
        return True
    except Exception:
        print("could not write to the database, sleeping 15 minutes")
        time.sleep(900) 
        return False