from flask import Blueprint

api_blueprint = Blueprint("api_blueprint", __name__, url_prefix="/api")


# @api_blueprint.route('/weed/next', methods=['GET'])
# def index():
#     return ""
