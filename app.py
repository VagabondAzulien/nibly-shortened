import hashlib
import random
import sqlite3
import string

from bottle import route, run, template, view

"""
Establish a DB connection, and setup the necessary table if not already created.
This belongs in a migration, or at least a different file.
"""
con = sqlite3.connect('shortened.db')
initial_cursor = con.cursor()
initial_cursor.execute("CREATE TABLE IF NOT EXISTS URLS(ID INTEGER PRIMARY KEY AUTOINCREMENT, ORIGINAL TEXT NOT NULL, SHORTENED TEXT NOT NULL);")
con.commit


def lookup_url(shortened):
    """
    Look-up a URL in the DB based on the md5-hash

    Arguments:
      shortened::str A String representation of the md5-hash of the URL
    Returns:
      The original URL, as a String
    """

    cursor = con.cursor()
    cursor.execute("SELECT * FROM URLS WHERE SHORTENED=:shortened",
                   {"shortened": shortened})
    results = cursor.fetchone()

    return results


def store_url(url):
    """
    Saves a URL and a corresponding md5-hash into the DB

    Arguments:
      url::str A String representation of the URL
    Returns:
      The md5-hash of the URL
    """

    cursor = con.cursor()
    url_encoded = bytes(url, 'UTF-8')
    shortened = hashlib.md5(url_encoded).hexdigest()
    cursor.execute("INSERT INTO URLS(ORIGINAL, SHORTENED) VALUES (?, ?)",
                (url, shortened))
    con.commit

    return shortened


@route('/api/v1/shorten/<url:path>')
def shorten(url):
    """
    Shorten a provided URL

    Arguments:
      url::str The URL to work with, as provided in the full route
    Returns:
      A templated-view showing the original URL, and the shortened counterpart
    """

    shortened = store_url(url)
    return template("shortened_view.html",
                    url=url,
                    shortened=shortened)


@route('/api/v1/lookup/<shortened>')
def lookup(shortened):
    """
    Lookup a URL based on the shortened ID

    Arguments:
      shortened::str The shortened ID to search for
    Returns:
      A templated-view showing the original URL, and the shortened counterpart
    """

    original = lookup_url(shortened)
    return template("shortened_view.html",
                    shortened=shortened,
                    url=original)


@route('/<id>')
def redirect(id):
    """
    Redirect from a shortened ID to the original URL

    Arguments:
      id::str The ID to use for the redirect
    """

    original = lookup_url(id)
    reditect(original)


"""
Run the server
"""
run(host='localhost', port=8080)
