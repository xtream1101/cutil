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

    def insert(self, table, data, id_col='id'):
        """
        Create a bulk insert statement which is much faster (~2x in tests with 10k & 100k rows and 4 cols)
        for inserting data then executemany()

        TODO: Is there a limit of length the query can be? If so handle it.
        """
        # Make sure that `data` is a list
        if not isinstance(data, list):
            data = [data]

        if len(data) == 0:
            # No need to continue
            return []

        # Data in the list must be dicts (just check the first one)
        if not isinstance(data[0], dict):
            logger.critical("Data must be a list of dicts")
            # Do not return here, let the exception handle the error that will be thrown when the query runs

        try:
            with self.getcursor() as cur:
                keys = data[0].keys()
                query = cur.mogrify("INSERT INTO {table} ({fields}) VALUES {values} RETURNING {id_col}"
                                    .format(table=table,
                                            fields=','.join(keys),
                                            values=','.join(['%s'] * len(data)),
                                            id_col=id_col
                                            ),
                                    [tuple(v.values()) for v in data])
                cur.execute(query)

                return [t[0] for t in cur.fetchall()]

        except Exception as e:
            logger.exception("Error inserting data")
            logger.debug("Error inserting data: {data}".format(data=data))
            raise e.with_traceback(sys.exc_info()[2])
