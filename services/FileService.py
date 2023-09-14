from database.JdbcDataSource import JdbcDataSource
from services.JDBCRepository import JDBCRepository


class FileService(JDBCRepository):

    def __init__(self, jdbcDataSource: JdbcDataSource) -> None:
        super().__init__(entity_name="csv_file", id="id", jdbcDataSource=jdbcDataSource)

    def upload_file(self, file):
        # save file in database with provided file properties
        # perform mapping transformation necessary and save to mapping storage
        # create the schema for mapped files
        # return the all file properties with schema
        pass
