from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import InternalServerError
from collections import OrderedDict
from flask import jsonify, Response
import logging
from functools import wraps


def format_response(f):
    """decortor for formatting response with HTTPException
    and overide the description attribute of HTTPException f
    or the costomized error message
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        res = OrderedDict(code=200, message='ok')

        try:
            result, status_code = f(*args, **kwargs)
            if isinstance(result, Response):
                return result, status_code

        except HTTPException as e:
            res['code'] = e.code
            res['message'] = e.description
        except Exception as unknownError:
            logging.exception(unknownError)
            res['code'] = InternalServerError.code
            res['message'] = InternalServerError.description
        else:
            if status_code == 200:
                res['payLoad'] = result
                code = 200
            else:
                res['message'] = result
                res['code'] = status_code

        return jsonify(res), res['code']

    return wrapper
