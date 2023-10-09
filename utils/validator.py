data ={
    "FileController":{
        "upload":{"first":['file_separator','category','column_mapping'],
                  "second":['link','file_separator','category','column_mapping','filename']},
        "column_mapping":['column_mappings','transformation'],
        "transform":['transformations'],
        "download_file_s3":['path']
    },
    "SchemaController":{
        "upload":['0']
    },
    "SpaceController":{
        "save_space":['is_deleted','s3_file_path','space_name','space_schema','vds_path','account_id','bi_data_source_id','status'],
        "update_space":['created_date','id','is_deleted','s3_file_path','space_name','space_schema','updated_date','vds_path','status'],
        "create_vds":['vds_name'],
        "add_file_to_space":['space_schema','file_id'],
        "get_all_spaces_by_account_id":['account_id','bi_data_source_id']


    }
}

data_types= {
    "file_separator": str,
    "category": str,
    "column_mapping": dict,
    "column_mappings":dict,
    "link": str,
    "filename": str,
    "transformation": list,
    "transformations":list,
    "is_deleted": int,
    "status": int,
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
    "id":int,
    "path":str
}

allowed_null_value = ['column_mapping','vds_path','s3_file_path','column_mappings','transformation','transformations']

data_type_names = {
    "int": "integer",
    "float": "float",
    "str": "string",
    "dict":"Dictionary",
    "list":"list"
}