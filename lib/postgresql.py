import logging

import psycopg2


def create_table(cursor: psycopg2.extensions.cursor,
                 connection: psycopg2.extensions.connection):
    query = '''
    CREATE TABLE IF NOT EXISTS user_counter (user_id integer PRIMARY KEY, counter integer, version integer);
    '''
    cursor.execute(query)
    connection.commit()
    logging.info("Successfully created a table user_counter")


def truncate_table(cursor: psycopg2.extensions.cursor,
                   connection: psycopg2.extensions.connection):
    query = '''
    TRUNCATE TABLE user_counter;
    '''
    cursor.execute(query)
    connection.commit()
    logging.info("Successfully delete all rows in the table user_counter")


def insert_first_line(cursor: psycopg2.extensions.cursor,
                      connection: psycopg2.extensions.connection):
    query = '''
    INSERT INTO user_counter VALUES (1, 1, 0) 
    '''
    cursor.execute(query)
    connection.commit()
    logging.info("Successfully added user_id 1 in the table user_counter")


def increment_lost_update(cursor: psycopg2.extensions.cursor,
                          connection: psycopg2.extensions.connection):
    cursor.execute("SELECT counter FROM user_counter WHERE user_id = 1")
    counter = cursor.fetchone()[0]
    counter += 1
    cursor.execute("update user_counter set counter = %s where user_id = %s", (counter, 1))
    connection.commit()


def increment_inplace_update(cursor: psycopg2.extensions.cursor,
                             connection: psycopg2.extensions.connection):
    cursor.execute("update user_counter set counter = counter + 1 where user_id = %s", (1, ))
    connection.commit()


def increment_row_level_locking(dsn: str):
    connection = psycopg2.connect(dsn)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT counter FROM user_counter WHERE user_id = 1 FOR UPDATE")
        counter = cursor.fetchone()[0]
        counter += 1
        cursor.execute("update user_counter set counter = %s where user_id = %s", (counter, 1))
        connection.commit()
    finally:
        connection.close()
        cursor.close()


def increment_optimistic_concurrency_control(cursor: psycopg2.extensions.cursor,
                                             connection: psycopg2.extensions.connection):
    while True:
        cursor.execute("SELECT counter, version FROM user_counter WHERE user_id = 1")
        result = cursor.fetchone()

        counter = result[0]
        counter += 1
        version = result[1]

        cursor.execute(
            "update user_counter set counter = %s, version = %s where user_id = %s and version = %s",
            (counter, version + 1, 1, version)
        )
        connection.commit()
        count = cursor.rowcount

        if count > 0:
            break
