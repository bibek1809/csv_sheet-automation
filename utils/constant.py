# constant values
file_category = {'CSV': 'csv', 'GOOGLESHEET': 'googlesheet'}
file_condition = {'CSV': 'first', 'GOOGLESHEET': 'second'}


# Very poor way to so validation . It way more complex code hai dai . it should be avoided. Note: Code is written once but read multiple times.

allowed_chars = 'a-zA-Z()'
errorType = {
    'IndexError': 412,  # datanotfound
    'DatabaseError': 413,
    'UnsupportedMediaType': 414,
    'FileNotFoundError': 415,
    'EmptyDataError': 416,
    'InvalidPostRequest': 417,
    'BadRequestKeyError': 418,
    'Configuration Failed': 419
}
message = {
    'IndexError': 'No Data Found As Requested',
    'FileNotFoundError': 'File is Missing'

}
space_missing_response = {
"success": False,
"code": 406,
"error": 'BAD_REQUEST',
"message": 'Data Not found, SpaceID was not found',
"traceback": f"Data Not found SpaceID was not found",
"description": "Data Not found SpaceID was not found"
}
file_missing_response = {
"success": False,
"code": 406,
"error": 'BAD_REQUEST',
"message": 'Data Not found, FileID was not found',
"traceback": f"Data Not found FileID was not found",
"description": "Data Not found FileID was not found"
}
missing_response= {
"success": False,
"code": 406,
"error": 'BAD_REQUEST',
"message": 'Data Not found, Account Id/ BidataSource  was not found or Space Exist !',
"traceback": f"Data Not found Account Id/ BidataSource was not found or Space Exist !",
"description": "Data Not found Account Id/ BidataSource was not found or Space Exist !"
}
date_missing_response= {  
"success":False,
"code": 412,
"error": 'Missing Date Column',
"message":f'Date Field is Missing in files',
"traceback": "Missing Fields: Date",
"description": "Field are missing"
}