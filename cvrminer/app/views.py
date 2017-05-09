"""Views for cvrminer app."""

from flask import (Blueprint, current_app, redirect, render_template, url_for)

from werkzeug.routing import BaseConverter

from ..xbrler import search_for_regnskaber
from ..wikidata import cvr_to_q


class RegexConverter(BaseConverter):
    """Converter for regular expression routes.

    References
    ----------
    https://stackoverflow.com/questions/5870188

    """

    def __init__(self, url_map, *items):
        """Setup regular expression matcher."""
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def add_app_url_map_converter(self, func, name=None):
    """Register a custom URL map converters, available application wide.

    References
    ----------
    https://coderwall.com/p/gnafxa/adding-custom-url-map-converters-to-flask-blueprint-objects

    """
    def register_converter(state):
        state.app.url_map.converters[name or func.__name__] = func

    self.record_once(register_converter)


Blueprint.add_app_url_map_converter = add_app_url_map_converter
main = Blueprint('app', __name__)
main.add_app_url_map_converter(RegexConverter, 'regex')


# Wikidata item identifier matcher
q_pattern = '<regex("Q[1-9]\d*"):q>'


@main.route("/")
def index():
    """Return index page of for app."""
    return render_template('index.html')


@main.route("/" + q_pattern)
def redirect_q(q):
    """Detect and redirect to CVRminer class page.

    Parameters
    ----------
    q : str
        Wikidata item identifier

    """
    class_ = 'company'
    method = 'app.show_' + class_
    return redirect(url_for(method, q=q), code=302)


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


@main.route('/branch/' + q_pattern)
def show_branche(q):
    """Return HTML rendering for specific branch.

    Parameters
    ----------
    q : str
        Wikidata item identifier.

    Returns
    -------
    html : str
        Rendered HTML.

    """
    return render_template('branch.html', q=q)


@main.route('/branch/')
def show_branch_empty():
    """Return rendered index page for branch.

    Returns
    -------
    html : str
        Rendered HTML page for branch index page.

    """
    return render_template('branch_empty.html')


@main.route('/company/')
def show_company_empty():
    """Return rendered index page for company.

    Returns
    -------
    html : str
        Rendered HTML page for branch index page.

    """
    return render_template('company_empty.html')


@main.route('/company/' + q_pattern)
def show_company(q):
    """Return HTML rendering for specific company.

    Parameters
    ----------
    q : str
        Wikidata item identifier.

    Returns
    -------
    html : str
        Rendered HTML.

    """
    return render_template('company.html', q=q)


@main.route('/exchange/')
def show_exchange_empty():
    """Return rendered index page for branch.

    Returns
    -------
    html : str
        Rendered HTML page for branch index page.

    """
    return render_template('exchange_empty.html')


@main.route('/exchange/' + q_pattern)
def show_exchange(q):
    """Return HTML rendering for specific exchange.

    Parameters
    ----------
    q : str
        Wikidata item identifier.

    Returns
    -------
    html : str
        Rendered HTML.

    """
    return render_template('exchange.html', q=q)
