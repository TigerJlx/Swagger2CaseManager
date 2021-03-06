from flask import make_response, jsonify
from flask_restful import Resource, reqparse
from backend.models.curd import StepCURD

curd = StepCURD()
parser = reqparse.RequestParser()
parser.add_argument('id', type=str)
parser.add_argument('step_id', type=str)
parser.add_argument('step_name', type=str)
parser.add_argument('name', type=str)
parser.add_argument('case_id', type=int)
parser.add_argument('api_name', type=str)
parser.add_argument('step_pos', type=int)


class StepItem(Resource):
    def get(self):
        pass

    def delete(self):
        args = parser.parse_args()
        status, msg = curd.delete_setp(args["step_id"])
        rst = make_response(jsonify({"success": status, "msg": msg}))
        return rst

    def patch(self):
        args = parser.parse_args()
        status, msg = curd.update_step(args)
        rst = make_response(jsonify({"success": status, "msg": msg}))
        return rst

    def post(self):
        args = parser.parse_args()
        status, msg = curd.add_step(args)
        rst = make_response(jsonify({"success": status, "msg": msg}))
        return rst
