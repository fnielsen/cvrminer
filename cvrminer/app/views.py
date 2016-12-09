"""Views for cvrminer app."""

from flask import Blueprint, current_app, render_template

from ..xbrler import search_for_regnskaber
from ..wikidata import cvr_to_q


main = Blueprint('app', __name__)


@main.route("/")
def index():
    """Return index page of for app."""
    return render_template('index.html')


@main.route("/smiley/")
def smiley():
    """Return smiley page of for app."""
    if current_app.smiley:
        table = current_app.smiley.db.tables.smiley.head(n=10000).to_html()
    else:
        table = ''
    return render_template('smiley.html', table=table)


@main.route("/cvr/<int:cvr>")
def show_cvr(cvr):
    """Return CVR page of for app."""
    q = cvr_to_q(cvr)
    regnskaber = search_for_regnskaber(cvr=cvr)
    return render_template('cvr.html',
                           cvr=cvr, regnskaber=regnskaber, q=q)
