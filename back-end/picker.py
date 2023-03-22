from flask import Blueprint, render_template , request, redirect, url_for

bp = Blueprint("picker", __name__)


@bp.route("/pick", methods=['GET', 'POST'])
def pick_banner():
    if request.method == 'GET':
        return render_template('show_banner.html')
    else:
        username = request.values['username']
        return redirect(url_for('picker.show_banner', username=username))


@bp.route("/pick/<string:username>", methods=['GET'])
def show_banner(username):
    print(username)
    image_path = 'images/image_100.jpeg'
    return render_template('show_banner.html', image_path=image_path)
