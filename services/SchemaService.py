from entity.File import File
from entity.ObjectMapper import ObjectMapper
from services.FileService import FileService
from utils import Configuration
from utils.csv_schema_infererence import CsvSchemaInference, SchemaInference

class SchemaService:

    def __init__(self, fileService: FileService):
        self.fileService = fileService
        self.object_mapper = ObjectMapper()
        self.schema_inference = SchemaInference()
        self.transform_storage_path = Configuration.TRANSFORM_FILE_PATH

    def generate_schema(self, file):
        csv_infer = CsvSchemaInference(portion=2, max_length=100000, batch_size=20000, acc=8, seed=10, header=True,
                                       sep=file.file_separator, conditions={})
        return list(csv_infer.run_inference(self.transform_storage_path + file.file_name).values())

    def get_schema(self, file_id):
        files = self.fileService.find_by_id(file_id)
        if files is None or len(files) == 0:
            # throws file_id not found exception
            return None
        file = ObjectMapper().map_to(files[0], File)
        if not file._schema:
            file._schema = self.generate_schema(file)
        return file

    def save(self, file_id, schema):
        file = File(id=file_id, file_schema=schema)
        return self.fileService.update(file)[0]

    def merge_schema(self, schema_1, schema_2):
        return self.schema_inference.merge_schemas(schema_1, schema_2)
    
    def check_match(self, schema_1, schema_2):
        names_schema_1 = set(field["name"] for field in schema_1)
        names_schema_2 = set(field["name"] for field in schema_2)
        matching_names = names_schema_1.intersection(names_schema_2)
        percent_matching = (len(matching_names) / len(names_schema_1)) * 100
        return percent_matching



