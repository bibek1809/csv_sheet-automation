import json
import os
import traceback
import inspect
from utils import validator
from utils import constant


def handle_exception(e):
    try :
        message = str(e).split(":", 1)[1].lstrip() if ":" in str(e) else str(e)
    except:
        message = str(e)
    try:
        message = constant.message[type(e).__name__]
    except:
        message= message
    traceback_info = traceback.format_exc()
    # Extracting only the traceback message without surrounding information
    traceback_message = str(e)
    try:
        code = constant.errorType[type(e).__name__]
    except:
        code = 500
    response = {
        "success": False,
        "code": code,
        # "error": message(e).__name__,
        "message":message,
        "traceback": traceback_message,
        "description": traceback_info

    }
    print(traceback.print_exc())
    return json.dumps(response), code


def validate_request(data, condition_scenario=None):
    code = 400
    frame = inspect.currentframe().f_back
    calling_function_name = frame.f_code.co_name
    calling_file_name = frame.f_globals['__file__']
    file_name = os.path.basename(calling_file_name).split('.')[0]
    if condition_scenario == None:
        required_fields = validator.data[file_name][calling_function_name]
        missing_fields = [
            field for field in required_fields if field not in data]

    else:
        required_fields = validator.data[file_name][calling_function_name][condition_scenario]
        missing_fields = [
            field for field in required_fields if field not in data]

    response =   {  "success":False,
        "code": code,
        "error": 'BAD_REQUEST',
        "message":f'missing fields are {missing_fields}',
        "traceback": "Missing Fields",
        "description": "Field are missing"
    }
    if missing_fields:
        return json.dumps(response)
    else:
        response = validate_datatypes(data)
        try:
            if response == True:
                return True
            else:
                return response
        except Exception as e:
            return handle_exception(e)

def handle_exception_message(message):
    try :
        message = message.split(":", 1)[1].lstrip() if ":" in message else message
    except:
        message = message
    try:
        message = constant.message['FileNotFoundError']
    except:
        message= message
    # Extracting only the traceback message without surrounding information
    traceback_message = message
    traceback_info = message
    try : 
        code = constant.errorType['FileNotFoundError']
    except:
        code = 500
    response = {
        "success": False,
        "code": code,
        "error": 'FileNotFoundError',
        "message":message,
        "traceback": traceback_message,
        "description": traceback_info

    }
    print(response)
    return json.dumps(response), code


def validate_datatypes(data):
    for key in data.keys():
        if not key in validator.allowed_null_value:
            if data[key] is None:
                    response = {
                            "success": False,
                            "code": 412,
                            "error": 'BAD_REQUEST',
                            "message": 'NULL Values Integrated',
                            "traceback": f"NULL Data input for {key} ",
                            "description": "Field are missing"
                        }
                    return json.dumps(response)

            if key == 'link':
                import re
                url_pattern = re.compile(r"https?://\S+")
                if  re.fullmatch(url_pattern, data[key]):
                    response = {
                        "success": False,
                        "code": 412,
                        "error": 'BAD_REQUEST',
                        "message": 'Invalid Datatypes',
                        "traceback": f"Invalid Datatype for {key} instead of {validator.data_type_names[validator.data_types[key].__name__]}",
                        "description": "Field are missing"
                    }
                    return json.dumps(response)
            elif not isinstance(data[key], validator.data_types[key]):
                response = {
                    "success": False,
                    "code": 412,
                    "error": 'BAD_REQUEST',
                    "message": 'Invalid Datatypes',
                    "traceback": f"Invalid Datatype for {key} instead of {validator.data_type_names[validator.data_types[key].__name__]}",
                    "description": "Field are missing"
                }
                return json.dumps(response)

    return True
