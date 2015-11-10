#!/usr/bin/python
#''''which python2 >/dev/null && exec python2 "$0" "$@" # '''
#''''which python  >/dev/null && exec python  "$0" "$@" # '''

# Copyright (C) 2014-2015 Nginx, Inc.

# Example of an application working on port 9000
# To interact with nginx-ldap-auth-daemon this application
# 1) accepts GET  requests on /login and responds with a login form
# 2) accepts POST requests on /login, sets a cookie, and responds with redirect

import sys, os, signal, base64, Cookie, cgi, urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

Listen = ('localhost', 9000)

import threading
from SocketServer import ThreadingMixIn
class AuthHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class AppHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.log_message('Accepted request in application')

        name = self.headers.get('X-Auth-Name')
        email = self.headers.get('X-Auth-email')

        html="""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <meta http-equiv=Content-Type content="text/html;charset=UTF-8">
    <title>Example application</title>
  </head>
  <body>
    Welcome, """
        html = html + name + " with email " + email;

        html = html + """
  </body>
</html>"""

        self.send_response(200)
        self.end_headers()
        self.wfile.write(html)

    def log_message(self, format, *args):
        if len(self.client_address) > 0:
            addr = BaseHTTPRequestHandler.address_string(self)
        else:
            addr = "-"

        sys.stdout.write("%s - - [%s] %s\n" % (addr,
                         self.log_date_time_string(), format % args))

    def log_error(self, format, *args):
        self.log_message(format, *args)


def exit_handler(signal, frame):
    sys.exit(0)

if __name__ == '__main__':
    server = AuthHTTPServer(Listen, AppHandler)
    signal.signal(signal.SIGINT, exit_handler)
    server.serve_forever()
