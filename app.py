"""Entrypoint to start app."""


from cvrminer.app import app


if __name__ == '__main__':
    app.run(debug=True)
