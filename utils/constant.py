# constant values
file_category = {'CSV': 'csv', 'GOOGLESHEET': 'googlesheet'}
file_condition = {'CSV': 'first', 'GOOGLESHEET': 'second'}


# Very poor way to so validation . It way more complex code hai dai . it should be avoided. Note: Code is written once but read multiple times.

allowed_chars = 'a-zA-Z0-9_'
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

duplicate_entry_response={
"success": False,
"code": 406,
"error": 'BAD_REQUEST',
"message": "Duplicate entry  for key 'space_name'",
"traceback": f"Duplicate entry for key 'space_name'",
"description": "Duplicate entry  for key 'space_name'"
}
date_missing_response= {  
"success":False,
"code": 412,
"error": 'Missing Date Column Or Date Pattern',
"message":f'Either Date or Date Pattern is Missing in files',
"traceback": "Missing Fields: Date",
"description": "Field are missing"
}

invalid_file_response= {  
"success":False,
"code": 410,
"error": 'Invalid Request Initiated',
"message":f'Invalid File Upload or Invalid Seprator Used',
"traceback": "Issue during File Upload or Invalid Seprator Used",
"description": "Issue during File Upload or Invalid Seprator Used"
}
invalid_category_response= {  
"success":False,
"code": 410,
"error": 'Invalid Request Initiated',
"message":f'Invalid Category Used',
"traceback": "Invalid Category Used",
"description": "Invalid Category Used"
}

Schema_not_match_response= {  
"success":False,
"code": 418,
"error": 'Invalid Schema Merge Request',
"message":f'Invalid Schema Merge Request :- Files Mismatched',
"traceback": "Invalid Schema Merge Request",
"description": "Invalid Schema Merge Request"
}
