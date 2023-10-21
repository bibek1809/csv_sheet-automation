import json
import time
import pandas as pd
from flask import Blueprint, jsonify, request, send_file
from services.FileSpaceRegistryService import FileSpaceRegistryService
from entity.FileSpaceRegister import FileSpaceRegistry
from database import DataSourceConfiguration
from entity.File import File
from entity.ObjectMapper import ObjectMapper
from services.FileService import FileService
from services.SchemaService import SchemaService
from services.TransformationService import TransformationService
from utils import Configuration, exception_handler, constant,AwsHelper
import os
import requests
import io
from urllib.parse import urlparse

file_blueprint = Blueprint(
    "file controller", __name__, url_prefix="/api/v1/file")

file_service = FileService(DataSourceConfiguration.mysql_datasource)
schema_service = SchemaService(fileService=file_service)
file_space_registry_service = FileSpaceRegistryService(
    DataSourceConfiguration.mysql_datasource)

transformation_service = TransformationService()

raw_file_path = Configuration.RAW_FILE_PATH


@file_blueprint.app_errorhandler(Exception)
def handle_exception(e):
    return exception_handler.handle_exception(e)


@file_blueprint.get("/")
def get_all_files():
    files = file_service.find_all()
    for file in files:
        file["file_schema"] = json.loads(
            file["file_schema"]) if file["file_schema"] else {}
        file["column_mapping"] = json.loads(
            file["column_mapping"]) if file["column_mapping"] else {}
    return jsonify({"files": files})


@file_blueprint.get("/<file_id>/")
def get_file_by_id(file_id):
    files = file_service.find_by_id(file_id)
    for file in files:
        file["file_schema"] = json.loads(
            file["file_schema"]) if file["file_schema"] else {}
        file["column_mapping"] = json.loads(
            file["column_mapping"]) if file["column_mapping"] else {}
    return jsonify({"file": files})


@file_blueprint.get("/<file_id>/view/")
def view_file(file_id):
    limit = request.args.get("limit")
    if limit is None:
        limit = 5
    else:
        limit = int(limit)
    files = file_service.find_by_id(file_id)
    filename = files[0]["file_name"]
    df = pd.read_csv(Configuration.TRANSFORM_FILE_PATH +
                     filename, on_bad_lines='skip')
    result = df.head(limit).to_json(orient='records')
    row_length, df_columns = len(df), len(df.columns)
    return jsonify({
        "data": {
            "result": json.loads(result),
            "rows_length": row_length,
            "column_length": df_columns
        }
    })


@file_blueprint.delete("/<file_id>/")
def delete_file(file_id):
    files = file_service.find_by_id(file_id)
    file = ObjectMapper().map_to(files[0], File)
    file.id = file_id
    file.is_deleted = True
    try:
        paths = json.loads(file.s3_file_path)
        path = paths["paths"][0]
        delete_status = AwsHelper.delete_object_from_s3(s3_paths= path,s3_access_key=Configuration.S3_ACCESS_KEY,
                                                    s3_secret_key=Configuration.S3_ACCESS_SECRET_KEY)
        file.s3_file_path = None
    except:
        pass  
    file_service.update(file)
    file_space_registry = ObjectMapper().map_to(
        {"file_id": file_id}, FileSpaceRegistry)
    file_space_registry_service.delete(file_space_registry)
    return jsonify({"file": f"file deleted sucessfully",
                    "delete_status":delete_status})


@file_blueprint.post("/")
def upload():
    condition_scenario = None
    gsheet_link = None
    data = request.form.to_dict()
    if data['category'] == constant.file_category['CSV']:
        condition_scenario = constant.file_condition['CSV']
    elif data['category'] == constant.file_category['GOOGLESHEET']:
        condition_scenario = constant.file_condition['GOOGLESHEET']
    else:
        return jsonify(constant.invalid_category_response), 410
    validation = exception_handler.validate_request(
        data, condition_scenario=condition_scenario)
    if validation == True:
        try:
            if data['category'] == constant.file_category['CSV']:
                csv_file = request.files['csv_file']
                filename = str(time.time()).split(".")[0] + '_'+csv_file.filename
                allowed_extension = ['tsv','csv']
                if filename.rsplit('.', 1)[1].lower() not in allowed_extension:
                    return jsonify(constant.invalid_file_response), 410
                csv_file.save(raw_file_path + filename)
                file = ObjectMapper().map_to(data, File)
            elif data['category'] == constant.file_category['GOOGLESHEET']:
                gsheet_link = data.pop('link')
                #print(link)
                link = f"""https://docs.google.com/spreadsheets/d/{gsheet_link}/edit#gid=0"""
                filename = str(time.time()).split(
                    ".")[0]+ '_' + data.pop('filename')+'.csv'
                # print(data)
                domain = urlparse(link).netloc
                segments = link.rpartition('/')
                link = segments[0] + "/export?format=csv"
                file = requests.get(link)
                if file.status_code == 200:
                    fileContent = file.content
                    file_path = os.path.join(raw_file_path + filename)
                    with io.open(file_path, 'wb') as f:
                        f.write(fileContent)
                    print(f"File '{filename}' saved successfully at {file_path}.")
                else:
                    return jsonify(constant.invalid_file_response), 410
                file = ObjectMapper().map_to(data, File)
        except:
            return jsonify(constant.invalid_file_response), 410

        file.file_name = filename
        if gsheet_link:
            file.link = gsheet_link
        file.column_mapping = transformation_service.default_column_mapping_generator(
            file)
        transformation_service.transform_columns(file)
        #schema = schema_service.generate_schema(file)
        if transformation_service.find_date(file):
            pass
        else:
            return jsonify(constant.date_missing_response), 412
        schema = schema_service.generate_schema(file)
        file.file_schema = json.dumps(schema)
        file_service.save(file)
        file.file_schema = None
        file.column_mapping = None
        inserted_file = file_service.find(file)[0]
        inserted_file["file_schema"] = json.loads(
            inserted_file["file_schema"]) if inserted_file["file_schema"] else {}
        inserted_file["column_mapping"] = json.loads(inserted_file["column_mapping"]) if inserted_file[
            "column_mapping"] else {}
        return jsonify({"file": inserted_file})
    else:
        return validation, 400


@file_blueprint.post("/<file_id>/mapping/")
def column_mapping(file_id):
    data = request.json
    validation = exception_handler.validate_request(data)
    if validation == True:
        files = file_service.find_by_id(file_id)
        if len(files) == 0:
            return jsonify(constant.file_missing_response), 406
        file = ObjectMapper().map_to(files[0], File)
        file.id = file_id
        file.column_mapping = data["column_mappings"]
        transformation_service.transform_columns_(file)
        schema = schema_service.generate_schema(file)
        file.file_schema = schema
        file.is_transformed = None
        file = file_service.update(file)
        if file and len(file):
            file = file[0]
            file["column_mapping"] = json.loads(file["column_mapping"])
            file["file_schema"] = json.loads(file["file_schema"])
        return jsonify({"file": file})
    else:
        return validation, 400


@file_blueprint.put("/<file_id>/")
def put(file_id):
    data = request.json
    file = ObjectMapper().map_to(data, File)
    file.id = file_id
    updated_file = file_service.upload_file(file)
    return jsonify({"file": updated_file})


@file_blueprint.post("/<file_id>/transform/")
def transform(file_id):
    data = request.json
    validation = exception_handler.validate_request(data)
    if validation == True:
        files = file_service.find_by_id(file_id)
        if len(files) == 0:
            return jsonify(constant.file_missing_response), 406
        file = ObjectMapper().map_to(files[0], File)
        try:
            try:
                dataframe = transformation_service.apply_transformations(
                    file, data["transformations"])
            except Exception as e:
                return handle_exception(e)
            if type(dataframe) != tuple:
                file.id = file_id
                try:
                    schema = schema_service.generate_schema(file)
                    file.file_schema = schema
                except Exception as e:
                    return handle_exception(e)

                # file.column_mapping = set(dataframe.columns)
                file.is_transformed = '1'
                file = file_service.update(file)
                if file and len(file):
                    file = file[0]
                    file["column_mapping"] = json.loads(file["column_mapping"])
                    file["file_schema"] = json.loads(file["file_schema"])
                else:
                    file = {}

                transform_detail = transformation_service.get_transformations_details(
                    data["transformations"])

                columns = json.loads(dataframe.to_json(orient="records"))
                return jsonify({"transform_detail":transform_detail,
                    "file": file})
            else:
                return jsonify(dataframe[0]), 412

        except Exception as e:
            return handle_exception(e)

    else:
        return validation, 400


@file_blueprint.get("/<file_id>/download/")
def download_file(file_id):
    files = file_service.find_by_id(file_id)
    if len(files) == 0:
        return jsonify(constant.file_missing_response), 406
    return send_file(Configuration.TRANSFORM_FILE_PATH+files[0]["file_name"], as_attachment=True)

@file_blueprint.post("/download/s3")
def download_file_s3():
    data = request.json
    validation = exception_handler.validate_request(data)
    if validation == True:
        path = data["path"]
        file_name = path.split('/')[-1]
        try:
            AwsHelper.download_object_from_s3(s3_paths=path,local_file=Configuration.RAW_FILE_PATH+file_name,
                                        s3_access_key=Configuration.S3_ACCESS_KEY,
                                                        s3_secret_key=Configuration.S3_ACCESS_SECRET_KEY )
            # return {"success":True,
            #         "file_path":Configuration.RAW_FILE_PATH+file_name}
            return send_file(Configuration.RAW_FILE_PATH+file_name, as_attachment=True)
        except:
            return {"success":False,
                    "message":"Invalid File Path"}
    else:
        return validation, 400