from entity.Entity import Entity


class File(Entity):
    def __init__(self, id=None, file_name=None, s3_file_path=None, created_date=None, updated_date=None, file_schema=None,
                 column_mapping=None, category=None, is_deleted=None, seperator=None,is_transformed = None):
        self.id = id
        self.file_name: str = file_name
        self.s3_file_path: str = s3_file_path
        self.created_date = created_date
        self.updated_date = updated_date
        self.file_schema: str = file_schema
        self.column_mapping = column_mapping
        self.category = category
        self.is_deleted = is_deleted
        self.seperator: str = seperator
        self.is_transformed = is_transformed

