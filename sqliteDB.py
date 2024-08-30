from util import logConfig, logger, lumos

# logConfig("logs/download.log", rotation="10 MB", level="DEBUG", lite=True)


def init_db_race(conn):
    cursor = conn.cursor()

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS race (
        checkpoint DATETIME PRIMARY KEY UNIQUE,
        status INTEGER,
        uuid TEXT,
        consume REAL,
        roi REAL,
        sales REAL,
        refunds REAL
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()

    logger.debug("Table created successfully.")

# def init_db_anchor(conn):
#     cursor = conn.cursor()

#     create_table_sql = """
#         CREATE TABLE IF NOT EXISTS anchor (
#         uuid TEXT PRIMARY KEY UNIQUE,
#         status INTEGER,
#         name TEXT,
#         scores TEXT,
#         holiday TEXT
#     );
#     """
#     cursor.execute(create_table_sql)
#     conn.commit()

#     logger.debug("Table created successfully.")



def insert_db(conn, data_dict, table="master"):
    cursor = conn.cursor()
    columns = ", ".join(data_dict.keys())
    placeholders = ", ".join(["?"] * len(data_dict))
    insert_sql = "INSERT INTO {} ({}) VALUES ({})".format(table, columns, placeholders)
    cursor.execute(insert_sql, tuple(data_dict.values()))
    conn.commit()
    logger.debug(f"Data inserted with ID: {data_dict['id']}")


def fetch_db_by_id(conn, id, table="master"):
    cursor = conn.cursor()
    fetch_sql = "SELECT * FROM {} WHERE id=?".format(table)
    cursor.execute(fetch_sql, (id,))
    result = cursor.fetchone()
    if result:
        return tuple_to_dict(cursor, result)
    else:
        return None


def fetch_db_all(conn, table="master"):
    cursor = conn.cursor()
    fetch_all_sql = "SELECT * FROM {}".format(table)
    cursor.execute(fetch_all_sql)
    results = cursor.fetchall()
    if results:
        return [tuple_to_dict(cursor, row) for row in results]
    else:
        return []


def update_db_by_id(conn, id, new_values, table="master"):
    cursor = conn.cursor()
    update_sql = (
        "UPDATE {} SET ".format(table)
        + ", ".join(["{}=?".format(k) for k in new_values])
        + " WHERE id=?"
    )
    values = list(new_values.values()) + [id]
    cursor.execute(update_sql, values)
    conn.commit()
    logger.debug(f"Data updated with ID: {id}")


def delete_db_by_id(conn, id, table="master"):
    cursor = conn.cursor()
    delete_sql = "DELETE FROM {} WHERE id=?".format(table)
    cursor.execute(delete_sql, (id,))
    conn.commit()
    logger.debug(f"Data deleted with ID: {id}")


def tuple_to_dict(cursor, row):
    return {column[0]: row[idx] for idx, column in enumerate(cursor.description)}

# for live
def init_mq(conn, table="queue"):
    cursor = conn.cursor()

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS {} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uname TEXT,
        act TEXT,
        msg TEXT,
        sec_uid TEXT,
        timestamp TEXT
    );
    """.format(
        table
    )
    cursor.execute(create_table_sql)
    conn.commit()

    logger.debug("Table created successfully.")

# for live
def insert_mq(conn, data_dict, table="queue"):
    cursor = conn.cursor()
    columns = ", ".join(data_dict.keys())
    placeholders = ", ".join(["?"] * len(data_dict))
    insert_sql = "INSERT INTO {} ({}) VALUES ({})".format(table, columns, placeholders)
    cursor.execute(insert_sql, tuple(data_dict.values()))
    conn.commit()
    logger.debug(f"Data inserted with ID: {data_dict['id']}")


def fetch_mq_by_id(conn, id, table="queue"):
    cursor = conn.cursor()
    fetch_sql = "SELECT * FROM {} WHERE id=?".format(table)
    cursor.execute(fetch_sql, (id,))
    result = cursor.fetchone()
    if result:
        return tuple_to_dict(cursor, result)
    else:
        return None

# for live
def fetch_mq_all(conn, star_id = None, table="queue"):
    cursor = conn.cursor()
    if star_id:
        fetch_all_sql = "SELECT * FROM {} WHERE id > {}".format(table, star_id)
    else:
        fetch_all_sql = "SELECT * FROM {}".format(table)
    cursor.execute(fetch_all_sql)
    results = cursor.fetchall()
    if results:
        return [tuple_to_dict(cursor, row) for row in results]
    else:
        return []


def fetch_mq(conn, table="queue"):
    cursor = conn.cursor()
    fetch_ids_sql = "SELECT id FROM {}".format(table)
    cursor.execute(fetch_ids_sql)
    ids = [row[0] for row in cursor.fetchall()]
    return ids


def update_mq_by_id(conn, id, new_values, table="queue"):
    cursor = conn.cursor()
    update_sql = (
        "UPDATE {} SET ".format(table)
        + ", ".join(["{}=?".format(k) for k in new_values])
        + " WHERE id=?"
    )
    values = list(new_values.values()) + [id]
    cursor.execute(update_sql, values)
    conn.commit()
    logger.debug(f"Data updated with ID: {id}")


def delete_mq_by_id(conn, id, table="queue"):
    cursor = conn.cursor()
    delete_sql = "DELETE FROM {} WHERE id=?".format(table)
    cursor.execute(delete_sql, (id,))
    conn.commit()
    logger.debug(f"Data deleted with ID: {id}")




def rebuild_init(conn):
    cursor = conn.cursor()

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS core (
        uid TEXT,
        uname TEXT,
        pid TEXT,
        pname TEXT,
        status INTEGER,
        checkpoint TEXT
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()

    logger.debug("Table core created successfully.")

def rebuild_insert(conn, table, data_dict):
    cursor = conn.cursor()
    columns = ", ".join(data_dict.keys())
    placeholders = ", ".join(["?"] * len(data_dict))
    insert_sql = "INSERT INTO {} ({}) VALUES ({})".format(table, columns, placeholders)
    cursor.execute(insert_sql, tuple(data_dict.values()))
    conn.commit()
    logger.debug(f"Data inserted {table} with {data_dict['uid']} - {data_dict['uname']}")

def rebuild_update_by_pid(conn, table, pid, new_values):
    cursor = conn.cursor()
    update_sql = (
        "UPDATE {} SET ".format(table)
        + ", ".join(["{}=?".format(k) for k in new_values])
        + " WHERE pid=?"
    )
    values = list(new_values.values()) + [pid]
    cursor.execute(update_sql, values)
    conn.commit()
    logger.debug(f"Data updated with ID: {pid} \ndict => {new_values}")