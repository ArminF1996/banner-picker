from flask import Flask, render_template

app = Flask(__name__)
app.url_map.strict_slashes = False
import uploader, picker
app.register_blueprint(uploader.bp, url_prefix="/upload")
app.register_blueprint(picker.bp, url_prefix="/picker")
app.secret_key = '8419084901274feF9797Q39VB3q5910120B99'


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
