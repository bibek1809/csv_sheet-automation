import base64
import traceback

class TokenEncryptor:
    @staticmethod
    def encrypt_token(token: str) -> str:
        try:
            if not len(token):
                return token
            token_length = len(token)
            # partition token into two halves
            first_half, second_half = token[:token_length //
                                            2], token[token_length//2:]
            # encode two halves and join with !!&!!
            encoding = base64.b64encode(first_half.encode('ascii')) + "!!&!!".encode('ascii') \
                + base64.b64encode(second_half.encode('ascii'))
            # encode again
            encoding = base64.b64encode(encoding).decode('ascii')
            return encoding
        except Exception as e:
            traceback.print_exc()
            raise Exception("Error in encrypt token(): " + str(e))

    @staticmethod
    def decrypt_token(cipher: str) -> str:
        try:
            if not len(cipher):
                return cipher
            # decode
            decoding = base64.b64decode(cipher.encode('ascii'))
            # split
            first_half, second_half = decoding.split(b"!!&!!")
            # decode
            decoding = base64.b64decode(
                first_half)+base64.b64decode(second_half)
            # convert to str
            decoding = decoding.decode('ascii')
            return decoding
        except:
            return ''
