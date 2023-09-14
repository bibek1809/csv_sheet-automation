data ={
    "FileController":{
        "upload":{"first":['seperator','category','column_mapping'],
                  "second":['link','seperator','category','column_mapping','filename']},
        "column_mapping":['column_mappings','transformation'],
        "transform":['transformations']
    },
    "SchemaController":{
        "upload":['0']
    },
    "SpaceController":{
        "save_space":['is_deleted','s3_file_path','space_name','space_schema','vds_path','account_id','bi_data_source_id'],
        "update_space":['created_date','id','is_deleted','s3_file_path','space_name','space_schema','updated_date','vds_path'],
        "create_vds":['vds_name'],
        "add_file_to_space":['space_schema','file_id']

    }
}

data_types= {
    "seperator": str,
    "category": str,
    "column_mapping": dict,
    "column_mappings":dict,
    "link": str,
    "filename": str,
    "transformation": list,
    "transformations":list,
    "is_deleted": int,
    "s3_file_path": str,
    "space_name": str,
    "space_schema": list,
    "vds_path": str,
    "vds_name":str,
    "account_id": str,
    "bi_data_source_id":int,
    "created_date":str,
    "updated_date":str,
    "file_id":int,
    "space_id":int,
    "id":int
}

allowed_null_value = ['column_mapping','vds_path','s3_file_path','column_mappings','transformation','transformations']

data_type_names = {
    "int": "integer",
    "float": "float",
    "str": "string",
    "dict":"Dictionary",
    "list":"list"
}