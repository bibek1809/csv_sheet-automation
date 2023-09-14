class SchemaInference:
    DATATYPE_RANK = {
        "INTEGER": 1,
        "FLOAT": 2,
        "DOUBLE": 3,
        "STRING": 4
    }

    def __datatype_merger(self, datatype_1, datatype_2):
        return datatype_1 if SchemaInference.DATATYPE_RANK[datatype_1] >= SchemaInference.DATATYPE_RANK[
            datatype_2] else datatype_2

    def __merge_schema(self, schema_1, schema_2):
        if schema_1 is None:
            return schema_2
        else:
            types_found = {}
            for k, v in schema_1['types_found'].items():
                types_found[k] = v * schema_1['total']

            for k, v in schema_2['types_found'].items():
                types_found[k] = v * schema_2['total'] + types_found[k] if k in types_found else 0

            total_records = schema_1['total'] + schema_2['total']

            for k, v in types_found.items():
                types_found[k] = v / total_records

            return {
                'name': schema_1['name'],
                'type': self.__datatype_merger(schema_1['type'], schema_2['type']),
                'nullable': schema_1['nullable'] and schema_2['nullable'],
                'total': total_records,
                'types_found': types_found
            }

    def merge_schemas(self, schemas_1, schemas_2):
        merged_schemas = {}
        for schema in schemas_1:
            merged_schemas[schema['name']] = schema

        for schema in schemas_2:
            merged_schema = self.__merge_schema(
                merged_schemas[schema['name']] if schema['name'] in merged_schemas else None, schema)
            merged_schemas[merged_schema['name']] = merged_schema

        return merged_schemas
