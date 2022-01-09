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
