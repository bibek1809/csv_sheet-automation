from entity.Entity import Entity


class FileSpaceRegistry(Entity):
    def __init__(self, id=None, file_id=None, space_id=None, created_date=None, updated_date=None,is_deleted=1):
        self.id = id
        self.file_id = file_id
        self.space_id = space_id
        self.created_date = created_date
        self.updated_date = updated_date
        self.is_deleted = is_deleted
