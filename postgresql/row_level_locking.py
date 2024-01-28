import os
import logging
import threading
import datetime

import psycopg2

from lib.postgresql import create_table, truncate_table, insert_first_line, increment_row_level_locking


DB_NAME = 'postgres'
USER = 'admin'
PASSWORD = os.getenv('PASSWORD')
HOST = 'localhost'
PORT = '5432'


if __name__ == '__main__':

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s\n'
    )

    dsn = f"dbname={DB_NAME} user={USER} password={PASSWORD} host={HOST} port={PORT}"
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()

    try:
        create_table(cur, conn)
        truncate_table(cur, conn)
        insert_first_line(cur, conn)


        start_datetime = datetime.datetime.now()

        threads = []
        for _ in range(10):
            t = threading.Thread(target=increment_row_level_locking, args=(dsn,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        end_datetime = datetime.datetime.now()
        difference = end_datetime - start_datetime

        logging.info(f"Duration of row level locking method - {difference.total_seconds()} seconds")

    finally:
        conn.close()
        cur.close()
