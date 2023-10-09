import jaydebeapi

from utils.LoggerFactory import LoggerFactory

logger = LoggerFactory.get_logger("JdbcDatabase")


class JdbcDatabase:
    def __init__(self, connection_properties: dict):
        self.connection_properties = connection_properties
        self.connection_pool = None
        self.connection = None

    def clear_connection(self):
        self.connection_pool = None
        self.connection = None

    def get_connection(self):
        # if self.connection is None:
        #     # print(self.connection_properties)
        #     try:
        self.connection = jaydebeapi.connect(
            **self.connection_properties)
            # except Exception as e:
            #     logger.error(e)
            #     self.clear_connection()
            #     raise BaseException(str(e))
        return self.connection


class Jdbc:
    def __init__(self, jdbcDatabase: JdbcDatabase):
        self.jdbcDatabase: JdbcDatabase = jdbcDatabase
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = self.jdbcDatabase.get_connection()
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        # if exc_val is not None:
        #     self.connection.rollback()
        self.cursor.close()


class DatabaseConnectionException(Exception):
    pass


class JdbcDataSource:
    def __init__(self, jdbcDatabase: JdbcDatabase):
        self.jdbcDatabase = jdbcDatabase

    def cud_execute(self, query: str):
        logger.info(query)
        with Jdbc(self.jdbcDatabase) as cursor:
            cursor.execute(query)

    def insert_query(self, query: str, insert_query: bool = False):
        logger.info(query)
        with Jdbc(self.jdbcDatabase) as cursor:
            cursor.execute(query)
            cursor.execute("SELECT LAST_INSERT_ID()")
            result = cursor.fetchone()
            if result:
                return result[0]  # The auto-incremented ID
            else:
                logger.warning("No auto-incremented ID returned after insert.")

    def _execute(self, query: str, retry=0):
        logger.info(query)
        try:
            with Jdbc(self.jdbcDatabase) as cursor:
                cursor.execute(query)
                result_set = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                return columns, result_set
        except jaydebeapi.DatabaseError as e:
            logger.error(str(e))
            exception_type = str(e).split(":", 2)[0].strip()
            if exception_type == "java.sql.SQLSyntaxErrorException":
                raise DatabaseConnectionException(str(e))
            else:
                self.jdbcDatabase.clear_connection()
                if retry == 0:
                    return self._execute(query=query, retry=retry + 1)
                else:
                    raise DatabaseConnectionException(str(e))

    def execute(self, query: str):
        columns, result_set = self._execute(query)
        records = []
        for row in result_set:
            records.append(dict(zip(columns, row)))
        return records

    def execute_and_return_list(self, query: str):
        with Jdbc(self.jdbcDatabase) as cursor:
            logger.info(query)
            cursor.execute(query)
            result_set = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            records = [r for r in result_set]
            return columns, records

