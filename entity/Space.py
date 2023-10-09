from entity.Entity import Entity


class Space(Entity):
    def __init__(self, id=None, space_name=None, space_schema=None, s3_file_path=None, vds_path=None,
                 created_date=None, updated_date=None, is_deleted=None,status=None):
        self.id = id
        self.space_name = space_name
        self.space_schema = space_schema
        self.s3_file_path = s3_file_path
        self.vds_path = vds_path
        self.created_date = created_date
        self.updated_date = updated_date
        self.is_deleted = is_deleted
        self.status = status
