import copy
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def _check_values(in_values):
    """ Check if values need to be converted before they get mogrify'd
    """
    out_values = []
    for value in in_values:
        # if isinstance(value, (dict, list)):
        #     out_values.append(json.dumps(value))
        # else:
        out_values.append(value)

    return tuple(out_values)


class Database:

    def __init__(self, db_config, table_raw=None, max_connections=10):
        from psycopg2.pool import ThreadedConnectionPool

        self.table_raw = table_raw
        # Set default port is port is not set
        if not db_config.get('db_port'):
            db_config['db_port'] = 5432

        self.pool = ThreadedConnectionPool(minconn=1,
                                           maxconn=max_connections,
                                           dsn="dbname={db_name} user={db_user} host={db_host} password={db_pass} port={db_port}"  # noqa: E501
                                               .format(**db_config))

    @contextmanager
    def getcursor(self, **kwargs):
        conn = self.pool.getconn()
        try:
            yield conn.cursor(**kwargs)
            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            self.pool.putconn(conn)

    def close(self):
        self.pool.closeall()

    def insert(self, table, data_list, return_cols='id'):
        """
        Create a bulk insert statement which is much faster (~2x in tests with 10k & 100k rows and n cols)
        for inserting data then executemany()

        TODO: Is there a limit of length the query can be? If so handle it.
        """
        data_list = copy.deepcopy(data_list)  # Create deepcopy so the original list does not get modified
        # Make sure that `data_list` is a list
        if not isinstance(data_list, list):
            data_list = [data_list]
        # Make sure data_list has content
        if len(data_list) == 0:
            # No need to continue
            return []

        # Data in the list must be dicts (just check the first one)
        if not isinstance(data_list[0], dict):
            raise ValueError("Data must be a list of dicts")

        # Make sure return_cols is a list
        if return_cols is None or len(return_cols) == 0 or return_cols[0] is None:
            return_cols = ''
        elif not isinstance(return_cols, list):
            return_cols = [return_cols]

        if len(return_cols) > 0:
            return_cols = 'RETURNING ' + ','.join(return_cols)

        try:
            with self.getcursor() as cur:
                query = "INSERT INTO {table} ({fields}) VALUES {values} {return_cols}"\
                        .format(table=table,
                                fields='"{0}"'.format('", "'.join(data_list[0].keys())),
                                values=','.join(['%s'] * len(data_list)),
                                return_cols=return_cols,
                                )
                values = []
                for row in [tuple(v.values()) for v in data_list]:
                    values.append(_check_values(row))

                query = cur.mogrify(query, values)
                cur.execute(query)

                try:
                    return cur.fetchall()
                except Exception:
                    return None

        except Exception:
            logger.debug("Error inserting data: {data}".format(data=data_list))
            raise

    def upsert(self, table, data_list, on_conflict_fields, on_conflict_action='update',
               on_conflict_where=None, update_fields=None, return_cols='id'):
        """
        Create a bulk upsert statement which is much faster (~6x in tests with 10k & 100k rows and n cols)
        for upserting data then executemany()

        TODO: Is there a limit of length the query can be? If so handle it.
        """
        data_list = copy.deepcopy(data_list)  # Create deepcopy so the original list does not get modified
        # Make sure that `data_list` is a list
        if not isinstance(data_list, list):
            data_list = [data_list]
        # Make sure data_list has content
        if len(data_list) == 0:
            # No need to continue
            return []
        # Data in the list must be dicts (just check the first one)
        if not isinstance(data_list[0], dict):
            raise ValueError("Data must be a list of dicts")

        # Make sure on_conflict_fields is a list
        if not isinstance(on_conflict_fields, list):
            on_conflict_fields = [on_conflict_fields]
        # Make sure on_conflict_fields has data
        if len(on_conflict_fields) == 0 or on_conflict_fields[0] is None:
            # No need to continue
            raise ValueError("Must pass in `on_conflict_fields` argument")

        # Support for partial index on table
        if on_conflict_where:
            on_conflict_where = f'WHERE {on_conflict_where}'
        else:
            on_conflict_where = ''

        # Make sure return_cols is a list
        if return_cols is None or len(return_cols) == 0 or return_cols[0] is None:
            return_cols = ''
        elif not isinstance(return_cols, list):
            return_cols = [return_cols]

        if len(return_cols) > 0:
            return_cols = 'RETURNING ' + ','.join(return_cols)

        # Make sure update_fields is a list/valid
        if on_conflict_action == 'update':
            if not isinstance(update_fields, list):
                update_fields = [update_fields]
            # If noting is passed in, set `update_fields` to all (data_list-on_conflict_fields)
            if len(update_fields) == 0 or update_fields[0] is None:
                update_fields = list(set(data_list[0].keys()) - set(on_conflict_fields))
                # If update_fields is empty here that could only mean that all fields are set as conflict_fields
                if len(update_fields) == 0:
                    raise ValueError("Not all the fields can be `on_conflict_fields` when doing an update")

            # If everything is good to go with the update fields
            fields_update_tmp = []
            for key in update_fields:
                fields_update_tmp.append('"{0}"="excluded"."{0}"'.format(key))
            conflict_action_sql = 'UPDATE SET {update_fields}'\
                                  .format(update_fields=', '.join(fields_update_tmp))
        else:
            # Do nothing on conflict
            conflict_action_sql = 'NOTHING'

        try:
            with self.getcursor() as cur:
                query = """INSERT INTO {table} ({insert_fields})
                           VALUES {values}
                           ON CONFLICT ({on_conflict_fields}) {on_conflict_where} DO
                           {conflict_action_sql}
                           {return_cols}
                        """.format(table=table,
                                   insert_fields='"{0}"'.format('","'.join(data_list[0].keys())),
                                   values=','.join(['%s'] * len(data_list)),
                                   on_conflict_fields=','.join(on_conflict_fields),
                                   on_conflict_where=on_conflict_where,
                                   conflict_action_sql=conflict_action_sql,
                                   return_cols=return_cols,
                                   )
                # Get all the values for each row and create a lists of lists
                values = []
                for row in [list(v.values()) for v in data_list]:
                    values.append(_check_values(row))

                query = cur.mogrify(query, values)

                cur.execute(query)

                try:
                    return cur.fetchall()
                except Exception:
                    return None

        except Exception:
            logger.debug("Error upserting data: {data}".format(data=data_list))
            raise

    def update(self, table, data_list, matched_field=None, return_cols='id'):
        """
        Create a bulk insert statement which is much faster (~2x in tests with 10k & 100k rows and 4 cols)
        for inserting data then executemany()

        TODO: Is there a limit of length the query can be? If so handle it.
        """
        data_list = copy.deepcopy(data_list)  # Create deepcopy so the original list does not get modified
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

        # Make sure return_cols is a list
        if return_cols is None or len(return_cols) == 0 or return_cols[0] is None:
            return_cols = ''
        elif not isinstance(return_cols, list):
            return_cols = [return_cols]

        if len(return_cols) > 0:
            return_cols = 'RETURNING ' + ','.join(return_cols)

        # Data in the list must be dicts (just check the first one)
        if not isinstance(data_list[0], dict):
            raise ValueError("Data must be a list of dicts")

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

                    query = "UPDATE {table} SET {data} WHERE {matched_field}=%s {return_cols}"\
                            .format(table=table,
                                    data=','.join("%s=%%s" % u for u in row.keys()),
                                    matched_field=matched_field,
                                    return_cols=return_cols
                                    )
                    values = list(row.values())
                    values.append(matched_value)
                    values = _check_values(values)

                    query = cur.mogrify(query, values)
                    query_list.append(query)
                    return_list.append(matched_value)

                finial_query = b';'.join(query_list)
                cur.execute(finial_query)

                try:
                    return cur.fetchall()
                except Exception:
                    return None

        except Exception:
            logger.debug("Error updating data: {data}".format(data=data_list))
            raise
