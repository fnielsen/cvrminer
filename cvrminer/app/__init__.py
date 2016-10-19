"""cvrminer app."""


from __future__ import absolute_import, division, print_function

from flask import Flask
from flask_bootstrap import Bootstrap

from ..smiley import Smiley


app = Flask(__name__)
Bootstrap(app)

app.smiley = Smiley()

from . import views
