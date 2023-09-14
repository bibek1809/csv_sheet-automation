import json
from flask import Blueprint, jsonify, request

from database import DataSourceConfiguration
from entity.File import File
from entity.FileSpaceRegister import FileSpaceRegistry
from entity.ObjectMapper import ObjectMapper
from entity.Space import Space
from services.FileService import FileService
from services.FileSpaceRegistryService import FileSpaceRegistryService
from services.SpaceService import SpaceService
from services.TransformationService import TransformationService
from utils import AwsHelper, Configuration, json_converter, exception_handler, constant
from utils.DremioHelper import DremioHelper

space_blueprint = Blueprint(
    "Space controller", __name__, url_prefix="/api/v1/space")
space_service = SpaceService(DataSourceConfiguration.mysql_datasource)
file_service = FileService(DataSourceConfiguration.mysql_datasource)
file_space_registry_service = FileSpaceRegistryService(
    DataSourceConfiguration.mysql_datasource)
transformation_service = TransformationService()
object_mapper = ObjectMapper()

dremio_helper = DremioHelper(url=Configuration.DREMIO_URL, username=Configuration.DREMIO_USERNAME,
                             password=Configuration.DREMIO_PASSWORD)


@space_blueprint.app_errorhandler(Exception)
def handle_exception(e):
    return exception_handler.handle_exception(e)


@space_blueprint.route("/", methods=['GET'])
def get_all_spaces():
    spaces = space_service.find_all()
    # space  = json.loads(spaces[0]["space_schema"])
    for index, space in enumerate(spaces):
        spaces[index]["space_schema"] = json.loads(space["space_schema"])

    return jsonify({"spaces": spaces})


@space_blueprint.route("/<space_id>/", methods=['GET'])
def get_space_by_id(space_id):
    spaces = space_service.find_by_id(space_id)
    if len(spaces):
        space = spaces[0]
        if space["space_schema"]:
            space["space_schema"] = json.loads(space["space_schema"])
        return jsonify({"space": spaces[0]})
    else:
        return jsonify(constant.space_missing_response), 406
    # return jsonify({"spaces": spaces})


@space_blueprint.route("/", methods=['POST'])
def save_space():
    data = request.json
    validation = exception_handler.validate_request(data)
    if validation == True:
        rows_to_keep = ['is_deleted',
                        's3_file_path',
                        'space_name',
                        'space_schema',
                        'vds_path']
        value = json_converter.filter_rows(data, rows_to_keep)
        space = object_mapper.map_to(value, Space)
        data = {"bi_data_source_id":data['bi_data_source_id'],"account_id":data["account_id"],"data_source_config_id":"Null"}
        result = space_service.find_by_values(data, 'account_bi_data_source')
        if len(result) == 0:
            return jsonify(constant.missing_response), 406
        inserted_space = space_service.save(space)[0]
        space_service.update_data_source(
            space_id=inserted_space["id"], bi_data_source_id=data["bi_data_source_id"], account_id=data["account_id"])

        inserted_space["space_schema"] = json.loads(
            inserted_space["space_schema"])
        return jsonify({"space": inserted_space})
    else:
        return validation, 400


@space_blueprint.route("/<space_id>/", methods=['PUT'])
def update_space(space_id):
    data = request.json
    validation = exception_handler.validate_request(data)
    if validation == True:
        spaces = space_service.find_by_id(space_id)
        if len(spaces) == 0:
            return jsonify(constant.space_missing_response), 406
        space = object_mapper.map_to(data, Space)
        space.id = space_id
        space = space_service.update(space)[0]
        dict_value = json.loads(space["space_schema"])
        space["space_schema"] = dict_value
        return jsonify({"space": space})
    else:
        return validation, 400


@space_blueprint.route("/<space_id>/", methods=['DELETE'])
def delete_space(space_id):
    file_space_registry = ObjectMapper().map_to(
        {"space_id": space_id}, FileSpaceRegistry)
    file_space_registry_service.delete(file_space_registry)
    spaces = space_service.find_by_id(space_id)
    space = ObjectMapper().map_to(spaces[0], Space)
    space.id = space_id
    space.is_deleted = True
    space_service.update(space)
    return jsonify({"msg": f"space with id={space_id} deleted successfully!!!"})


@space_blueprint.route("/<space_id>/file/", methods=['POST'])
def add_file_to_space(space_id):
    data = request.json
    validation = exception_handler.validate_request(data)
    if validation == True:
        file_id = data['file_id']
        spaces = space_service.find_by_id(space_id)
        if len(spaces) == 0:
            return jsonify(constant.space_missing_response), 406
        files = file_service.find_by_id(file_id)
        if len(files) == 0:
            return jsonify(constant.file_missing_response), 406
        space_schema = json.dumps(data['space_schema'])
        space = Space(id=space_id, space_schema=space_schema)

        # upload file to S3 space bucket
        file = object_mapper.map_to(file_service.find_by_id(file_id)[0], File)
        s3_paths = AwsHelper.upload_parquet_to_s3(s3_path=Configuration.S3_PATH + str(space_id),
                                                  dataframe=transformation_service.get_transformed_dataframe(
                                                      file),
                                                  s3_access_key=Configuration.S3_ACCESS_KEY,
                                                  s3_secret_key=Configuration.S3_ACCESS_SECRET_KEY)
        file.s3_file_path = json.dumps(s3_paths)
        # updating the S3 path in file
        updated_file = file_service.update(file)
        # updating the space schema
        space = space_service.update(space)
        # registering the file in file_space_mapping
        file_space_register = FileSpaceRegistry(
            file_id=file_id, space_id=space_id)
        file_space_register = file_space_registry_service.save(
            file_space_register)

        return jsonify({
            "file": updated_file,
            "space": space,
            "file_space_register": file_space_register
        })
    else:
        return validation, 400


@space_blueprint.route("/<space_id>/file/", methods=['GET'])
def get_all_files_in_space(space_id):
    spaces = space_service.find_by_id(space_id)
    if len(spaces) == 0:
        return jsonify(constant.space_missing_response), 406
    return jsonify({
        "file_space_registry": file_space_registry_service.find_files_by_space_id(space_id)
    })


@space_blueprint.route("account/<account_id>/file/", methods=['POST'])
def get_all_files_by_account_id(account_id):
    data = request.json
    bi_data_source_id = data['bi_data_source_id']
    data = {"bi_data_source_id":bi_data_source_id,"account_id":account_id}
    result = space_service.find_by_values(data, 'account_bi_data_source')
    if len(result) == 0:
        return jsonify(constant.missing_response), 406
    # return jsonify({
    #     "file_space_registry": file_spaces,
    #     "regitry": file_space_registry
    # })
    return jsonify({
        "file_space_registry": file_space_registry_service.find_files_by_account_id(account_id,bi_data_source_id)
    })



@space_blueprint.route("account/<account_id>/space", methods=['POST'])
def get_all_spaces_by_account_id(account_id):
    data = request.json
    bi_data_source_id = data['bi_data_source_id']
    data = {"bi_data_source_id":bi_data_source_id,"account_id":account_id}
    result = space_service.find_by_values(data, 'account_bi_data_source')
    if len(result) == 0:
        return jsonify(constant.missing_response), 406
    spaces = space_service.find_spaces_by_account_id(
        account_id, bi_data_source_id)
    valid_spaces = []
    # for space in spaces:
    #     valid_spaces.append({
    #         "file_name": space["file_name"],
    #         "id": space["id"],
    #     })

    return jsonify({
        "spaces": spaces
    })


@space_blueprint.route("/<space_id>/format/", methods=['POST'])
def format_space(space_id):
    spaces = space_service.find_by_id(space_id)
    if len(spaces) == 0:
        return jsonify(constant.space_missing_response), 406
    # try:
    # Format the folder if not formatted already else alter table
    space_catalog_path = Configuration.DREMIO_CATALOG_PATH + str(space_id)
    folder_format_response = dremio_helper.format_folder(
        space_catalog_path)

    # create VDS for the particular folder if not created or else alter vds
    return folder_format_response
    # except Exception as e:
    #     handle_exception(e)

@space_blueprint.route("/<space_id>/format/update", methods=['POST'])
def update_format_space(space_id):
    # Format the folder if not formatted already else alter table
    space_catalog_path = Configuration.DREMIO_CATALOG_PATH + str(space_id)
    folder_format_response = dremio_helper.alter_dataset(space_catalog_path)

    # create VDS for the particular folder if not created or else alter vds
    return folder_format_response


@space_blueprint.route("/<space_id>/vds/", methods=['POST'])
def create_vds(space_id):
    data = request.json
    validation = exception_handler.validate_request(data)
    if validation == True:
        vds_name = data['vds_name']
        space_catalog_path = Configuration.DREMIO_CATALOG_PATH + str(space_id)
        folder_format_response = dremio_helper.create_vds(
            vds_name, space_catalog_path)

        # create VDS for the particular folder if not created or else alter vds
        return folder_format_response, 201

    else:
        return validation, 400
