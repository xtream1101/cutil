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

    def insert(self, table, data_list, return_cols='id'):
        """
        TODO: rename `id_col` -> `return_col`
        Create a bulk insert statement which is much faster (~2x in tests with 10k & 100k rows and n cols)
        for inserting data then executemany()

        TODO: Is there a limit of length the query can be? If so handle it.
        """
        # Make sure that `data_list` is a list
        if not isinstance(data_list, list):
            data_list = [data_list]
        # Make sure data_list has content
        if len(data_list) == 0:
            # No need to continue
            return []

        # Data in the list must be dicts (just check the first one)
        if not isinstance(data_list[0], dict):
            logger.critical("Data must be a list of dicts")
            # Do not return here, let the exception handle the error that will be thrown when the query runs

        # Make sure return_cols is a list
        if not isinstance(return_cols, list):
            return_cols = [return_cols]
        # Make sure on_conflict_fields has data
        if len(return_cols) == 0 or return_cols[0] is None:
            # No need to continue
            logger.critical("`return_cols` cannot be None/empty")
            # TODO: raise some error here rather then returning None
            return None

        try:
            with self.getcursor() as cur:
                query = "INSERT INTO {table} ({fields}) VALUES {values} RETURNING {return_cols}"\
                        .format(table=table,
                                fields='"{0}"'.format('", "'.join(data_list[0].keys())),
                                values=','.join(['%s'] * len(data_list)),
                                return_cols=', '.join(return_cols),
                                )
                query = cur.mogrify(query, [tuple(v.values()) for v in data_list])
                cur.execute(query)

                return [t for t in cur.fetchall()]

        except Exception as e:
            logger.exception("Error inserting data")
            logger.debug("Error inserting data: {data}".format(data=data_list))
            raise e.with_traceback(sys.exc_info()[2])

    def upsert(self, table, data_list, on_conflict_fields, on_conflict_action='update',
               update_fields=None, return_cols='id'):
        """
        WIP
        `on_conflict_action` [Not Implemented Yet]: Defaults to `update`, other option is `nothing`

        Create a bulk upsert statement which is much faster (~6x in tests with 10k & 100k rows and n cols)
        for upserting data then executemany()

        TODO: Support on conflict do nothing action
        TODO: Is there a limit of length the query can be? If so handle it.
        """
        # Make sure that `data_list` is a list
        if not isinstance(data_list, list):
            data_list = [data_list]
        # Make sure data_list has content
        if len(data_list) == 0:
            # No need to continue
            return []
        # Data in the list must be dicts (just check the first one)
        if not isinstance(data_list[0], dict):
            logger.critical("Data must be a list of dicts")
            # TODO: raise some error here rather then returning None
            return None

        # Make sure on_conflict_fields is a list
        if not isinstance(on_conflict_fields, list):
            on_conflict_fields = [on_conflict_fields]
        # Make sure on_conflict_fields has data
        if len(on_conflict_fields) == 0 or on_conflict_fields[0] is None:
            # No need to continue
            logger.critical("Must pass in `on_conflict_fields` argument")
            # TODO: raise some error here rather then returning None
            return None

        # Make sure return_cols is a list
        if not isinstance(return_cols, list):
            return_cols = [return_cols]
        # Make sure on_conflict_fields has data
        if len(return_cols) == 0 or return_cols[0] is None:
            # No need to continue
            logger.critical("`return_cols` cannot be None/empty")
            # TODO: raise some error here rather then returning None
            return None

        # Make sure update_fields is a list/valid
        if on_conflict_action == 'update':
            if not isinstance(update_fields, list):
                update_fields = [update_fields]
            # If noting is passed in, set `update_fields` to all (data_list-on_conflict_fields)
            if len(update_fields) == 0 or update_fields[0] is None:
                update_fields = list(set(data_list[0].keys()) - set(on_conflict_fields))
                # If update_fields is empty here that could only mean that all fields are set as conflict_fields
                if len(update_fields) == 0:
                    logger.critical("Not all the fields can be `on_conflict_fields` when doing an update")
                    # TODO: raise some error here rather then returning None
                    return None

            # If everything is good to go with the update fields
            fields_update_tmp = []
            for key in data_list[0].keys():
                fields_update_tmp.append('"{0}"="excluded"."{0}"'.format(key))
            conflict_action_sql = 'UPDATE SET {update_fields}'\
                                  .format(update_fields=', '.join(fields_update_tmp))
        else:
            # Do nothing on conflict
            conflict_action_sql = 'NOTHING'

        try:
            with self.getcursor() as cur:
                query = """INSERT INTO {table} ({insert_fields})
                           SELECT {values}
                           ON CONFLICT ({on_conflict_fields}) DO
                           {conflict_action_sql}
                           RETURNING {return_cols}
                        """.format(table=table,
                                   insert_fields='"{0}"'.format('", "'.join(data_list[0].keys())),
                                   values=','.join(['unnest(%s)'] * len(data_list[0])),
                                   on_conflict_fields=', '.join(on_conflict_fields),
                                   conflict_action_sql=conflict_action_sql,
                                   return_cols=', '.join(return_cols),
                                   )
                # Get all the values for each row and create a lists of lists
                values = [list(v.values()) for v in data_list]
                # Transpose list of lists
                values = list(map(list, zip(*values)))
                query = cur.mogrify(query, values)

                cur.execute(query)

                return [t for t in cur.fetchall()]

        except Exception as e:
            logger.exception("Error inserting data")
            logger.debug("Error inserting data: {data}".format(data=data_list))
            raise e.with_traceback(sys.exc_info()[2])

    def update(self, table, data_list, matched_field=None, returns_col='id'):
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
