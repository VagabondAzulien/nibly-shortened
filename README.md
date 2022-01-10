# Nibly URL Shortner

A Python Bottle application for shortening URLs.

## Objectives

- Shorten a URL!
  - POST `/api/v1/shorten/<url_to_shorten>`
  - Responds with a shortened URL, `domain.tld/<identifier>`, and a "200 OK"
      status code

- Lookup a URL!
  - GET `/api/v1/lookup/<identifier>`
  - Responds with the original URL, and a "200 OK" status code

## Extra
- Run it in Docker
- Make a simple Web-UI
- Implement a redirect, such that accessing `domain.tld/<identifier>` directs the
    user to the corresponding URL

# Post-Mortem: One-Hour of Work

### Design Decisions

I decided on the Bottle Python web-framework. It is simple and easy to get
started with, and is performant enough for my use-cases.

To allow for persistent data, I decided on SQLite3. The DB is a single table
with an auto-incremented ID, an ORIGINAL column representing the originally
provided URL, and a SHORTENED column representing an md5-hash of the URL.

Build all of the above into a Docker image based on Alpine for a small
footprint.

The name of the project is a portmanteau of my last name, Niblock, and Bitly.

### Original Idea

When hitting the POST endpoint, hash the URL to shorten, store it in the DB with
the original URL, and return the ID of the row. When hitting the GET endpoint to
lookup the URL, search the DB for the hash of the URL, and return the results.
Similarly, when hitting the redirect GET endpoint (ie., domain.tld/id), redirect
accordingly.

### Results

I created much less than I had expected to, honestly. The concept is relatively
straight-forward, but the implementation took me far longer than I anticipated.
There is no need to hash the URL if the ID of the row will be used. Figuring out
how to hash the URL took me too long. The endpoints return a template, and thus
are not necessarily appropriate for an API. Instead, the API endpoints should
probably return a JSON payload (or similar structure), whereas more appropriate
"web" endpoints, such as "domain.tld/shorten" would allow for a form that users
can interact with.

I don't like having the DB "initialize" in the app.py file. This would more
appropriately live in a migration. Also, instead of relying on SQLite3 (as
wonderful as it is), I'd prefer using an ORM to work with any of several
databases.

Overall, while I'm no stranger to Python, I'm not as familiar with it as I
thought I was. Though I do work regularly with the language, I tend to rely on
documentation and examples. For this exercise, I tried to refrain from
explicitly looking up examples or suggestions, and relied only on the official
Python documentation.

# Post-Post-Mortem: More Work

After the above write-up, and a bit of food, I returned to this project to see
what I could finish in another 4 hours, for 5 hours total. Here's where it
stands:

- It works! That's a step up from the previous iteration.
- Can be built into a Docker imag, or run from the Pipenv virtual environment
- The routes, while not perfect, better capture the intention:
  - The root route loads a web page with an HTTP form, the functionality of
      which leverages the api routes
  - The `/api/v1/shorten/<url>` endpoint will return a URL using the row ID in 
      the DB. It will also check if the provided URL already exists based on 
      MD5 hash
  - Both `/api` endpoints will return JSON when applicable, and otherwise will
      return plain text. XML is also planned, but not implemented.
  - The `/to/<id>` endpoint redirects accordingly.

There are still several things missing, or otherwise lacking:

- There is no logging
- There is no error handling (no _real_ error handling)
- The routes could deal with being better serialized
- I would still prefer an ORM to using SQL statements in-line (perhaps Peewee?)
- A better identifier than the DB row ID seems ideal
- This README needs to be properly formatted

Given the above, I would say this application is another 3-4 hours away from
completion. With better error handling and a better identifier for the shortened
URL, I would feel comfortable deploying this to my personal VPS. 

# Licenses / Copyrights / Contact

All code is [Unlicensed](https://unlicense.org), unless otherwise noted for the
individual files.

The easiest way to contact me is via Matrix, I'm
[Vagabond](https://matrix.to/#/@vagabondazulien:exp.farm).
