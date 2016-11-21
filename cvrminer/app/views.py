"""Views for cvrminer app."""

from flask import render_template

from . import app


@app.route("/")
def index():
    """Return index page of for app."""
    return render_template('base.html')


@app.route("/smiley/")
def smiley():
    """Return smiley page of for app."""
    table = app.smiley.db.tables.smiley.head(n=10000).to_html()
    return render_template('smiley.html', table=table)


@app.route("/cvr/<int:cvr>")
def show_cvr(cvr):
    """Return smiley page of for app."""
    return render_template('cvr.html', cvr=cvr)
