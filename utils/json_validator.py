data = {
    "FileController": {
        "upload": {"first": ['seperator', 'category', 'column_mapping'],
                   "second": ['link', 'seperator', 'category', 'column_mapping', 'filename']},
        "column_mapping": ['column_mappings', 'transformation'],
        "transform": ['transformations']
    },
    "SchemaController": {
        "upload": ['0']
    },
    "SpaceController": {
        "save_space": ['is_deleted', 's3_file_path', 'space_name', 'space_schema', 'vds_path', 'account_id', 'bi_data_source_id'],
        "update_space": ['created_date', 'id', 'is_deleted', 's3_file_path', 'space_name', 'space_schema', 'updated_date', 'vds_path'],
        "create_vds": ['vds_name'],
        "add_file_to_space": ['space_schema', 'file_id']
    }
}
