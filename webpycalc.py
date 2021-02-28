#!/usr/bin/env python3

import web
import webbrowser


def main():
    url = 'http://127.0.0.1:5000'
    webbrowser.open(url)
    app = web.create_app()
    app.run()


if __name__ == "__main__":
    main()
