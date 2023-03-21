from flask import Blueprint, render_template

bp = Blueprint("picker", __name__)


@bp.route("/pick", methods=['GET'])
def pick_banner():
    return render_template('show_banner.html')
