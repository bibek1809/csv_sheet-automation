from database.JdbcDataSource import JdbcDataSource
from services.JDBCRepository import JDBCRepository


class SpaceService(JDBCRepository):

    def __init__(self, jdbcDataSource: JdbcDataSource) -> None:
        super().__init__(entity_name="csv_space", id="id", jdbcDataSource=jdbcDataSource)
    
    def mapp_space(self,space_id,account_id,bi_data_source_id):
        return self.jdbcDataSource.cud_execute(f"""INSERT INTO csv_space_mapper_table
                                            (SELECT id,{space_id} FROM `account_bi_data_source`
                                            WHERE account_id = '{account_id}'
                                            AND bi_data_source_id = {bi_data_source_id})""")
    
    def update_data_source(self,account_id,bi_data_source_id):
        return self.jdbcDataSource.cud_execute(f"""update account_bi_data_source 
                                           set data_source_config_id = id
                                     WHERE account_id = '{account_id}'
                                            and bi_data_source_id = {bi_data_source_id}""")

    def find_spaces_by_account_id(self, account_id, bi_data_source_id,status = None,space = None):
        statusQuery = ''
        spaceQuery = ''
        if status:
            statusQuery = f"""and s.status = {status}"""
        if space:
            spaceQuery = f"""and s.space_name = '{space}'"""
        
        return self.jdbcDataSource.execute(f"""SELECT s.* FROM csv_space as s 
                            join csv_space_mapper_table as map
                            on map.space_id = s.id
                            join account_bi_data_source as a
                            on a.id = map.id
                            WHERE a.account_id = '{account_id}'
                                and a.bi_data_source_id = {bi_data_source_id}
                            AND s.is_deleted IS FALSE
                            {statusQuery}{spaceQuery}
                            and s.space_name NOT REGEXP '_[0-9]{10}$'
                                group by s.id""")



