import json

from flask import Blueprint, jsonify, request

from database import DataSourceConfiguration
from entity.ObjectMapper import ObjectMapper
from services.FileService import FileService
from services.SchemaService import SchemaService
from utils import exception_handler, constant
schema_blueprint = Blueprint(
    "Schema controller", __name__, url_prefix="/api/v1/schema")

file_service = FileService(DataSourceConfiguration.mysql_datasource)
schema_service = SchemaService(fileService=file_service)
object_mapper = ObjectMapper()


@schema_blueprint.app_errorhandler(Exception)
def handle_exception(e):
    """_summary_

    Args:
        e (_type_): _description_

    Returns:
        _type_: _description_
    """
    return exception_handler.handle_exception(e)


@schema_blueprint.get("/")
def get_all_files():
    return "files"


@schema_blueprint.get("/<file_id>")
def get_file_by_id(file_id):
    """_summary_

    Args:
        file_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    files = file_service.find_by_id(file_id)
    if len(files) == 0:
        return json.dumps(constant.file_missing_response), 406
    file = schema_service.get_schema(file_id=file_id)
    return jsonify({"file": file.to_json()})


@schema_blueprint.post("/<file_id>")
def upload(file_id):
    """_summary_

    Args:
        file_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    files = file_service.find_by_id(file_id)
    if len(files) == 0:
        return json.dumps(constant.file_missing_response), 406
    schema = json.dumps(request.json)
    file = schema_service.save(file_id, schema)
    return jsonify({"file": file})


@schema_blueprint.put("/<file_id>")
def put(file_id):
    pass


@schema_blueprint.post("/merge/")
def merge():
    """_summary_

    Returns:
        _type_: _description_
    """
    data = request.json
    merged_schema = schema_service.merge_schema(
        data["schema_1"], data["schema_2"])
    listed_merge_schema = list(merged_schema.values())
    return jsonify({"merged_schema": listed_merge_schema})