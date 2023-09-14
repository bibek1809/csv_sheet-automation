from database.JdbcDataSource import JdbcDataSource
from services.JDBCRepository import JDBCRepository


class SpaceService(JDBCRepository):

    def __init__(self, jdbcDataSource: JdbcDataSource) -> None:
        super().__init__(entity_name="csv_space", id="id", jdbcDataSource=jdbcDataSource)
    

    
    def update_data_source(self,space_id,account_id,bi_data_source_id):
        return self.jdbcDataSource.cud_execute(f"""update account_bi_data_source 
                                           set data_source_config_id = {space_id}
                                     WHERE account_id = '{account_id}'
                                            and bi_data_source_id = {bi_data_source_id}""")

    def find_spaces_by_account_id(self, account_id, bi_data_source_id):
        return self.jdbcDataSource.execute(f"""SELECT s.* FROM csv_space as s 
                                           join file_space_register as fs
                                           on fs.space_id = s.id
                                           join account_bi_data_source as a
                                           on a.data_source_config_id = fs.space_id
                                           WHERE a.account_id = '{account_id}'
                                            and a.bi_data_source_id = {bi_data_source_id}
                                            group by s.id""")
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

