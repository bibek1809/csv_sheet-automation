import json

from database.JdbcDataSource import JdbcDataSource


class JDBCRepository:
    def __init__(self, entity_name: str, id: str, jdbcDataSource: JdbcDataSource):
        self.entity_name = entity_name
        self.id = id
        self.jdbcDataSource = jdbcDataSource
        pass

    def find_last_added(self):
        return self.jdbcDataSource.execute(f"SELECT * FROM {self.entity_name} order by 1 desc limit 1")

    def find_all(self):
        return self.jdbcDataSource.execute(f"SELECT * FROM {self.entity_name} where is_deleted = 0")

    def find(self, entity):
        where_conditions = dict(filter(lambda i: i[1] is not None, entity.to_json().items()))
        if len(where_conditions) > 0:
            where_clause = " AND ".join([k + "=" + self.convert(v) for k, v in where_conditions.items()])
            return self.jdbcDataSource.execute(f"SELECT * FROM {self.entity_name} WHERE {where_clause}")
        else:
            return self.jdbcDataSource.execute(f"SELECT * FROM {self.entity_name} ")

    def find_by_id(self, id):
        query = f"SELECT * FROM {self.entity_name} WHERE {self.id} = {id} and is_deleted = 0"
        return self.jdbcDataSource.execute(query)
    
    def find_by_id_all_status(self, id):
        query = f"SELECT * FROM {self.entity_name} WHERE {self.id} = {id}"
        return self.jdbcDataSource.execute(query)

    def save(self, entity):
        insert_pairs = dict(filter(lambda i: i[1] is not None, entity.to_json().items()))
        columns = ",".join(insert_pairs.keys())
        values = ",".join(map(lambda v: self.convert(v), insert_pairs.values()))
        sql_insert = f"INSERT INTO {self.entity_name}({columns}) VALUES({values})"

        print(sql_insert)
        #self.jdbcDataSource.cud_execute(sql_insert)
        #return self.find(entity)
        #return self.find_last_added()
        return self.find_by_id(self.jdbcDataSource.insert_query(sql_insert))


    def update(self, entity):
        update_values = dict(filter(lambda i: i[1] is not None and i[0] is not self.id, entity.to_json().items()))
        update_clause = ",".join([k + "=" + self.convert(v) for k, v in update_values.items()])
        where_clause = f"{self.id} = {self.convert(entity.to_json()[self.id])}"
        update_sql = f"UPDATE {self.entity_name} SET {update_clause} WHERE {where_clause}"
        self.jdbcDataSource.cud_execute(update_sql)
        return self.find_by_id(entity.to_json()[self.id])

    def delete_by_id(self, id):
        self.jdbcDataSource.cud_execute(f"DELETE FROM {self.entity_name} WHERE {self.id}={id}")

    def delete(self, entity):
        delete_condition = dict(filter(lambda i: i[1] is not None and i[0] is not self.id, entity.to_json().items()))
        delete_clause = " AND ".join([k + "=" + self.convert(v) for k, v in delete_condition.items()])
        delete_query = f"DELETE FROM {self.entity_name} WHERE {delete_clause}"
        self.jdbcDataSource.cud_execute(delete_query)


    def convert(self, val):
        if isinstance(val, str):
            return "'" + val.replace("'", "''") + "'"
        elif isinstance(val, int):
            return str(val)
        elif isinstance(val, dict):
            return "'" + json.dumps(val) + "'"
        elif isinstance(val,list):
            return "'" + json.dumps(val)+ "'"

        else:
            return "'" + val.replace("'", "''") + "'"

    def find_by_values(self, json_data, table_name):
        column_names = list(json_data.keys())
        column_values = list(json_data.values())
        if not column_names:
            raise ValueError("No column names provided in the query_data")

        # Create a list of conditions for each column-value pair
        conditions = [f"{col} IS NULL" if val == "Null" else f"{col} = '{val}'" for col, val in zip(column_names, column_values)]
        #conditions = [f"{col} = '{val}'" for col, val in zip(column_names, column_values)]

        # Join the conditions with 'AND' to create the WHERE clause
        where_clause = " AND ".join(conditions)

        # Construct the SQL query with column names and values
        sql_query = f"SELECT * FROM {table_name} WHERE {where_clause}"
        print(sql_query)
        # Execute the query with the provided values
        result = self.jdbcDataSource.execute(sql_query)

        return result