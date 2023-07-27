from functools import wraps
from flask import jsonify, request

def required_variables(schema: dict, pass_on = True, extra = False):
    def decor(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if request.method == "POST":
                content = request.json
            elif request.method == "GET":
                content = request.values.to_dict()
            else:
                content = request.args.to_dict()

            if len(set(schema.keys()) - set(content.keys())) != 0:
                return jsonify(
                    message="Bad request, laking: {}".format(", ".join(set(schema.keys()) - set(content.keys()))),
                    code=400
                ), 400
            elif (set(schema.keys()) != set(content.keys())) and not extra:
                return jsonify(
                    message="Bad request, provided: {}, expected: {}".format(set(content.keys()), set(schema.keys())),
                    code=400
                ), 400
            else:
                if pass_on:
                    parsed = {}

                    for n in schema:
                        try:
                            parsed[n] = schema[n](content[n])

                        except ValueError:
                            return jsonify(
                                message=f"Bad request, provided wrong var type, expected: {n}:{schema[n].__name__}",
                                code=400
                            ), 400

                    return func(*args, **parsed, **kwargs)
                else: return func(*args, **kwargs)

        return inner

    return decor