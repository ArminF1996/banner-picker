from flask import Flask, render_template

configs = {}


def create_app(config):
    """Create and configure an instance of the Flask application."""
    global configs
    configs = config
    app = Flask(__name__, instance_relative_config=True, template_folder=configs.TEMPLATE_FOLDER,
                static_folder=configs.STATIC_FOLDER)
    app.url_map.strict_slashes = False
    app.config.update(configs.__dict__)

    # apply the blueprints to the app
    from backend import uploader, picker
    app.register_blueprint(uploader.bp, url_prefix=configs.UPLOADER_URL_PREFIX)
    app.register_blueprint(picker.bp, url_prefix=configs.PICKER_URL_PREFIX)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
