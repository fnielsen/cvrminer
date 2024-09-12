"""cvrminer app."""


from __future__ import absolute_import, division, print_function

from flask import Flask
from flask_bootstrap import Bootstrap, StaticCDN


def create_app(smiley=False):
    """Create app.

    Factory for app.

    Parameters
    ----------
    smiley : bool, optional
        Determines whether the smiley functionality should be setup.

    """
    app = Flask(__name__)
    Bootstrap(app)

    # Serve assets from wmflabs for privacy reasons
    app.extensions['bootstrap']['cdns']['jquery'] = StaticCDN()
    app.extensions['bootstrap']['cdns']['bootstrap'] = StaticCDN()

    if smiley:
        from ..smiley import Smiley

        app.smiley = Smiley()
    else:
        app.smiley = None

    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
