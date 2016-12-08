import sys
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class Database:

    def __init__(self, db_config, table_raw=None, max_connections=10):
        from psycopg2.pool import ThreadedConnectionPool

        self.table_raw = table_raw
        try:
            self.pool = ThreadedConnectionPool(minconn=1,
                                               maxconn=max_connections,
                                               dsn="dbname={db_name} user={db_user} host={db_host} password={db_pass}"
                                                   .format(**db_config))
        except Exception:
            logger.exception("Error in db connection")
            sys.exit(1)

        logger.debug("Connected to database: {host}".format(host=db_config['db_host']))

    @contextmanager
    def getcursor(self):
        conn = self.pool.getconn()
        try:
            yield conn.cursor()
            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e.with_traceback(sys.exc_info()[2])

        finally:
            self.pool.putconn(conn)

    def insert(self, table, data_list, id_col='id'):
        """
        TODO: rename `id_col` -> `return_col`
        Create a bulk insert statement which is much faster (~2x in tests with 10k & 100k rows and 4 cols)
        for inserting data then executemany()

        TODO: Is there a limit of length the query can be? If so handle it.
        """
        # Make sure that `data_list` is a list
        if not isinstance(data_list, list):
            data_list = [data_list]

        if len(data_list) == 0:
            # No need to continue
            return []

        # Data in the list must be dicts (just check the first one)
        if not isinstance(data_list[0], dict):
            logger.critical("Data must be a list of dicts")
            # Do not return here, let the exception handle the error that will be thrown when the query runs

        try:
            with self.getcursor() as cur:
                query = "INSERT INTO {table} ({fields}) VALUES {values} RETURNING {id_col}"\
                        .format(table=table,
                                fields='{0}{1}{0}'.format('"', '", "'.join(data_list[0].keys())),
                                values=','.join(['%s'] * len(data_list)),
                                id_col=id_col
                                )
                query = cur.mogrify(query, [tuple(v.values()) for v in data_list])
                cur.execute(query)

                return [t[0] for t in cur.fetchall()]

        except Exception as e:
            logger.exception("Error inserting data")
            logger.debug("Error inserting data: {data}".format(data=data_list))
            raise e.with_traceback(sys.exc_info()[2])

    def update(self, table, data_list, matched_field=None, return_col='id'):
        """
        Create a bulk insert statement which is much faster (~2x in tests with 10k & 100k rows and 4 cols)
        for inserting data then executemany()

        TODO: Is there a limit of length the query can be? If so handle it.
        """
        if matched_field is None:
            # Assume the id field
            logger.info("Matched field not defined, assuming the `id` field")
            matched_field = 'id'

        # Make sure that `data_list` is a list
        if not isinstance(data_list, list):
            data_list = [data_list]

        if len(data_list) == 0:
            # No need to continue
            return []

        # Data in the list must be dicts (just check the first one)
        if not isinstance(data_list[0], dict):
            logger.critical("Data must be a list of dicts")
            # Do not return here, let the exception handle the error that will be thrown when the query runs

        try:
            with self.getcursor() as cur:
                query_list = []
                # TODO: change to return data from the database, not just what you passed in
                return_list = []
                for row in data_list:
                    if row.get(matched_field) is None:
                        logger.debug("Cannot update row. Missing field {field} in data {data}"
                                     .format(field=matched_field, data=row))
                        logger.error("Cannot update row. Missing field {field} in data".format(field=matched_field))
                        continue

                    # Pull matched_value from data to be updated and remove that key
                    matched_value = row.get(matched_field)
                    del row[matched_field]

                    query = "UPDATE {table} SET {data} WHERE {matched_field}=%s RETURNING {return_col}"\
                            .format(table=table,
                                    data=','.join("%s=%%s" % u for u in row.keys()),
                                    matched_field=matched_field,
                                    return_col=return_col
                                    )
                    values = list(row.values())
                    values.append(matched_value)

                    query = cur.mogrify(query, values)
                    query_list.append(query)
                    return_list.append(matched_value)

                finial_query = b';'.join(query_list)
                cur.execute(finial_query)

                return return_list

        except Exception as e:
            logger.exception("Error updating data")
            logger.debug("Error updating data: {data}".format(data=data_list))
            raise e.with_traceback(sys.exc_info()[2])
