import os
import logging
import concurrent.futures
import datetime

import psycopg2

from lib.postgresql import create_table, truncate_table, insert_first_line, increment_inplace_update


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

    conn = psycopg2.connect(f"dbname={DB_NAME} user={USER} password={PASSWORD} host={HOST} port={PORT}")
    cur = conn.cursor()

    try:
        create_table(cur, conn)
        truncate_table(cur, conn)
        insert_first_line(cur, conn)

        start_datetime = datetime.datetime.now()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            [executor.submit(increment_inplace_update, cur, conn) for _ in range(1, 10000)]

        end_datetime = datetime.datetime.now()
        difference = end_datetime - start_datetime

        logging.info(f"Duration of in-place update method - {difference.total_seconds()} seconds")
    finally:
        conn.close()
        cur.close()
