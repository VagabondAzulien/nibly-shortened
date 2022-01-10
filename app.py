import hashlib
import json
import random
import sqlite3
import string

from bottle import get, post, request, response, route, run, template, view

"""
Establish a DB connection, and setup the necessary table if not already created.
This belongs in a migration, or at least a different file.
"""
con = sqlite3.connect('shortened.db')
initial_cursor = con.cursor()
initial_cursor.execute("CREATE TABLE IF NOT EXISTS URLS(ID INTEGER PRIMARY KEY AUTOINCREMENT, ORIGINAL TEXT NOT NULL, SHORTENED TEXT NOT NULL);")
con.commit

def generate_error_message(headers, **kwargs):
    """
    Generates an error message to be displayed

    Arguments:
      headers::WSGIHeaderDict
        A dictionary of the request headers
      message::String
        An optional message to use instead of the default message

    Returns:
      An error message in an appropriate format
    """
    request_content_type = headers.get("content-type")
    ctype, csubtype = request_content_type.split("/")
    message = "An error has occurred :("

    if 'message' in kwargs:
        message = kwargs.get("message")

    if ctype in ["application", "text"]:
        if "json" in csubtype:
            response_message = json.dumps({"status_code": response.status, "error": message})
        elif "xml" in csubtype:
            response_message = "XML? Really?"
        else:
            response_message = "Unsupported Content-Type. Please set an " \
                               "acceptable value for the Content-Type header " \
                               "and try again."
    else:
        response_message = "Unsupported Content-Type. Please set an " \
                           "acceptable value for the Content-Type header " \
                           "and try again."

    return response_message


def generate_new_url(urlparts, shortened):
    """
    Generate the new shortened URL from the parts provided

    Arguments:
      urlparts::tuple
        A tuple of the URL parts from the request headers
      shortened::string
        A string representation of a shortened URL

    Returns:
      A string of the new URL
    """

    new_url = urlparts[0] + "://"
    new_url += urlparts[1] + "/"
    new_url += "to/" + shortened

    return new_url


def check_for_existing_url(md5hash):
    """
    Check if a URL is already in the DB

    Arguments:
      md5hash::str A String representation of the md5-hash of the URL
    Returns:
      The original URL, as a String
    """

    cursor = con.cursor()
    cursor.execute("SELECT * FROM URLS WHERE SHORTENED=:md5hash",
                   {"md5hash": str(md5hash)})
    results = cursor.fetchone()

    return results


def lookup_url(row_id):
    """
    Look-up a URL in the DB based on the ID

    Arguments:
      row_id::int An Integer of the row ID
    Returns:
      The original URL, as a String
    """

    cursor = con.cursor()
    cursor.execute("SELECT * FROM URLS WHERE ID=:row_id",
                   {"row_id": str(row_id)})
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

    url_encoded = bytes(url, 'UTF-8')
    shortened = hashlib.md5(url_encoded).hexdigest()
    existing_value = check_for_existing_url(shortened)

    if existing_value:
        results = existing_value[0]
    else:
        cursor = con.cursor()
        cursor.execute("INSERT INTO URLS(ORIGINAL, SHORTENED) VALUES (?, ?)",
                    (url, shortened))
        results = cursor.lastrowid
        con.commit

    return str(results)


@post('/api/v1/shorten/<url:path>')
def api_shorten(url):
    """
    Shorten a provided URL

    Arguments:
      url::str The URL to work with, as provided in the full route
    Returns:
      A templated-view showing the original URL, and the shortened counterpart
    """

    request_content_type = request.headers.get("content-type")
    ctype, csubtype = request_content_type.split("/")
    response_message = generate_error_message(request.headers)


    if ctype in ["application", "text"]:

        shortened = store_url(url)
        shortened = generate_new_url(request.urlparts, shortened)

        if csubtype in ['json', 'ld+json', 'cbor', 'vnd.api+json']:
            response_message = json.dumps({"status_code": response.status,
                                           "original": url,
                                           "shortened": shortened})
        elif "xml" in csubtype:
            response_message = "don't use xml what is wrong with you"
        else:
            response_message = shortened

    return response_message


@get('/api/v1/lookup/<shortened>')
def api_lookup(shortened):
    """
    Lookup a URL based on the shortened ID

    Arguments:
      shortened::str The shortened ID to search for
    Returns:
      A templated-view showing the original URL, and the shortened counterpart
    """

    request_content_type = request.headers.get("content-type")
    ctype, csubtype = request_content_type.split("/")
    response_message = generate_error_message(request.headers)


    if ctype in ["application", "text"]:

        row_id, original, md5hash = lookup_url(shortened)

        if csubtype in ['json', 'ld+json', 'cbor', 'vnd.api+json']:
            response_message = json.dumps({"status_code": response.status,
                                           "original": original,
                                           "shortened": md5hash})
        elif "xml" in csubtype:
            response_message = "don't use xml what is wrong with you"
        else:
            response_message = original

    return response_message


@get('/to/<shortened>')
def send_to(shortened):
    """
    Redirect from a shortened ID to the original URL

    Arguments:
      id::str The ID to use for the redirect
    """

    original = api_lookup(shortened)
    response.status = 303
    response.set_header('Location', original)


@get('/')
@view('view/shorten_form.html')
def shorten():
    """
    Web-UI for the URL shortener. This is the GET response.

    Returns:
      The shorten_form.html template, which includes an HTML form
    """

    return


@post('/')
@view('view/shorten_view.html')
def do_shorten():
    """
    Web-UI for the URL shortener. This is the POST response.

    Returns:
      The shorten_view.html template, which includes the details of the
      shortened URL.
    """

    url = request.forms.get('url')
    shortened = api_shorten(url)

    return dict(url=url, shortened=shortened)

@route('/test')
def test_return_type():
    url_encoded = bytes('https://www.google.com', 'UTF-8')
    shortened = hashlib.md5(url_encoded).hexdigest()
    val = check_for_existing_url(shortened)

    row_id = "Didn't even try"

    if val:
        row_id = val[0]
    else:
        row_id = "NOPE"

    return print(row_id)

"""
Run the server
"""
run(host='0.0.0.0', port=8080)
