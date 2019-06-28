import json
from rest_framework import status
from utils.app_static_variables import MSG_405, MSG_401


class IsAuthenticated:
  def __init__(self):
    pass


class IsAdmin:
  def __init__(self):
    pass


def api_action(**params):
    def taken(fn):
        def wrapper(*args, **kwargs):
            my_scope = args[0]
            request_body = args[1]
            allowed_methods = params['methods']
            permission_classes = params['permission_classes']

            if allowed_methods:
                flag = False
                for each in allowed_methods:
                    if my_scope['method'] == each:
                        flag = True
                        break
                if not flag:
                    data = json.dumps({'detail': MSG_405}).encode()
                    return my_scope.send_response(status.HTTP_405_METHOD_NOT_ALLOWED, data, headers=[("Content-Type", "application/json")])

            if permission_classes:
                user = my_scope['user']
                for each in permission_classes:
                    if each == IsAuthenticated:
                        if not user.is_authenticated:
                            data = json.dumps({'detail': MSG_401}).encode()
                            return my_scope.send_response(status.HTTP_401_UNAUTHORIZED, data, headers=[("Content-Type", "application/json")])
                    elif each == IsAdmin:
                        if not user.is_superuser:
                            data = json.dumps({'detail': MSG_401}).encode()
                            return my_scope.send_response(status.HTTP_401_UNAUTHORIZED, data, headers=[("Content-Type", "application/json")])
            return fn(*args, **kwargs)
        return wrapper
    return taken

'''

def decAny(**tag):
    def dec(fn):
        # @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            obj = tag['permission_classes'][0]
            my_scope = args[0]
            print(my_scope.count)
            if obj != IsAuthenticated:
                return {"message": "failed"}
            return fn(*args, **kwargs)

        return wrapper

    return dec

'''