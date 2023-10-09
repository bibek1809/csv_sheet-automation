from database.JdbcDataSource import JdbcDataSource
from services.JDBCRepository import JDBCRepository


class FileSpaceRegistryService(JDBCRepository):
    def __init__(self, jdbcDataSource: JdbcDataSource) -> None:
        super().__init__(entity_name="file_space_register", id="id", jdbcDataSource=jdbcDataSource)

    def find_files_by_space_id(self, space_id):
            return self.jdbcDataSource.execute(f"""SELECT f.*,fs.space_id FROM csv_file as f 
                                            join {self.entity_name} as fs
                                            on fs.file_id = f.id
                                            join csv_space AS s 
                                           on s.id = fs.space_id
                                            and  fs.space_id = {space_id}
                                            AND s.is_deleted IS FALSE
                                            and s.space_name NOT REGEXP '_[0-9]{10}$';
                                            """)

    def find_files_by_account_id(self, account_id,bi_data_source_id):
        query = f"""SELECT f.*,fs.space_id,a.account_id FROM csv_file as f 
                                           join {self.entity_name} as fs
                                           on fs.file_id = f.id
                                           join csv_space_mapper_table as map
                                           on map.space_id = fs.space_id
                                           join csv_space AS s 
                                           on s.id = fs.space_id
                                           join account_bi_data_source as a
                                            on a.id = map.id
                                           WHERE a.account_id = '{account_id}'
                                            AND s.is_deleted IS FALSE
                                            and s.space_name !~ '_\\d{10}$'
                                            and a.bi_data_source_id = {bi_data_source_id} group by f.id"""
        return self.jdbcDataSource.execute(query)
                      