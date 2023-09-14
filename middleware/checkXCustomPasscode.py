from flask import request
from utils import Configuration
from utils.token_encryption import TokenEncryptor


class PasscodeValidator:

    @staticmethod
    def validate(passcode):
        decrypted_passcode = TokenEncryptor.decrypt_token(passcode)
        if decrypted_passcode != Configuration.X_CUSTOM_PASSCODE:
            return False
        return True

        # return passcode == Configuration.X_CUSTOM_PASSCODE



# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         if "Authorization" in request.headers:
#             token = request.headers["Authorization"]
#         if not token:
#             return {
#                       "message": "Authentication Token is missing!",
#                        "data": None,
#                        "error": "Unauthorized"
#                    }, 401
#         try:
#             req = Request(MicroservicesURL.SSO_URL)
#             response = req.get(SSO_URL.check_expiration_url, headers={"Authorization": f"{token}"})
#             response.raise_for_status()
#             data= response.json()
            
#             current_user = data.get("data",{}).get("user")
#             return f(current_user, *args, **kwargs)
#         except HTTPError as e:
#             status_code = e.response.status_code
#             if status_code == 401:
#                 return {
#                            "message": "Authentication Token is invalid!",
#                            "data": None,
#                            "error": "Unauthorized"
#                        }, 401
            
#             else:
#                 return {
#                         "message": "Something went wrong",
#                         "data": None,
#                         # "error": str(e)
#                     }, 500
 

#     return decorated
