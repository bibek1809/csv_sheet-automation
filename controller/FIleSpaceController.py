import json

from flask import Blueprint, jsonify, request

from database import DataSourceConfiguration
from entity.ObjectMapper import ObjectMapper
from services.FileService import FileService
from services.SchemaService import SchemaService

schema_blueprint = Blueprint("Schema controller", __name__, url_prefix="/api/v1/schema")

file_service = FileService(DataSourceConfiguration.mysql_datasource)
schema_service = SchemaService(fileService=file_service)
object_mapper = ObjectMapper()
