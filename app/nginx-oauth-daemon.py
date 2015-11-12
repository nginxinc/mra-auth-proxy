#!/usr/bin/python
#''''which python2 >/dev/null && exec python2 "$0" "$@" # '''
#''''which python  >/dev/null && exec python  "$0" "$@" # '''

# Copyright (C) 2015 Nginx, Inc.
# Updated by Chris Stetson

import threading, sys, os, signal, base64, Cookie, urllib2, json, re, urllib
from urlparse import urlparse, parse_qs
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

#sys.path.append("pycharm-debug.egg")
#import pydevd
#pydevd.settrace('192.168.99.1', port=8889, stdoutToServer=True, stderrToServer=True)

Listen = ('localhost', 8888)

class AuthHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class AuthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.log_message('Starting Script')
        ctx = dict()
        # set to True to see all response bodies
        ctx['verbose'] = True
        self.ctx = ctx
        CLIENT_ID='108432233305-b54d09r3l39vbkoj4gkjd7lar67habo7.apps.googleusercontent.com'
        CLIENT_SECRET='loAdwBqjulSEBh6k1c_ybozb'
        RURI='http://ngra.ps.nginxlab.com/login'

        try:

            # Step 1: get configuration from headers set in nginx.conf
            ctx['action'] = 'verifying configuration parameters'

            params = {
                'auth_token_service': ('X-Oauth-Token-Service', None),
                'auth_service': ('X-Oauth-Service', None),
                'fields' : ('X-OAuth-Result', 'profile, email')
            }

            self.log_message('Iterating Over Params')

            for k, v in params.items():
                ctx[k] = self.headers.get(v[0], v[1])
                if ctx[k] == None:
                    self.auth_failed(ctx, 'required "%s" header was not passed' % k)
                    #return
                else:
                    self.log_message('Header Params ' + k + ': ' + ctx[k])

            # Step 2: check 'Authorisation' header and extract bearer token
            ctx['action'] = 'performing authorisation'

            auth_header = self.headers.get('Authorization')

            self.log_message('URL is: ' + self.path)


            query_components = parse_qs(urlparse(self.path).query)
            ctx['token'] = self.headers.get('OAuth-Args')
            if ctx['token'] is not None: self.log_message('OAuth Args: ' + ctx['token'])
            p = re.compile('code=(.*?)&')
            ctx['token'] = p.search(ctx['token']).group(1)
            if ctx['token'] is not None: self.log_message('Found OAuth code: ' + ctx['token'])
            else: self.log_message('REG-EX got nothing')

            if auth_header is None and ctx['token'] is None:
                self.log_message('no "Authorization" header, return 401')
                self.send_response(401)
                self.end_headers()
                return
            elif auth_header is None:
                self.log_message('JWOT Code: ' + ctx['token'])


            # Step 3: send request to service using code
            ctx['action'] = 'authorizing with openauth service'
            self.log_message('authorizing with User Code "%s" at service "%s"'
                                         % (ctx['token'], ctx['auth_service']))

            values = {  'client_id' : CLIENT_ID,
                        'client_secret' : CLIENT_SECRET,
                        'code' : ctx['token'],
                        'grant_type' : 'authorization_code',
                        'redirect_uri' : RURI}

            postData = urllib.urlencode(values)

            req = urllib2.Request(ctx['auth_token_service'],postData)
            self.log_message('PostData Encoded, Request Set: ')
            #content = urllib2.urlopen(url=ctx['auth_service'], data=postData).read()

            #req.add_header('Authorization', 'Bearer ' + ctx['token'])
            # required by some services, for example github
            req.add_header('User-Agent', 'auth-daemon')
            req.add_header('Content-Type','application/x-www-form-urlencoded')

            self.log_message('Headers Set: URL Connection being opened')

            connection = urllib2.urlopen(req)
            #r = urllib2.urlopen(req)
            self.log_message('Connection created:')

            content = connection.read()
            self.log_message('Content read:')

            response = json.loads(content)
            self.log_message('Content parsed into JSON:')

            if ctx['verbose']:
                response_dump = json.dumps(response, indent = 4)
                self.log_message(response_dump)

            # Step 4: send request to service using auth token
            ctx['action'] = 'authorising with openauth service'
            self.log_message('Sending request to service using token')

            ctx['token'] = response['access_token']


            self.log_message('authorizing with access_token "%s" at service "%s"'
                             % (ctx['token'], ctx['auth_service']))

            req = urllib2.Request(ctx['auth_service'])

            req.add_header('Authorization', 'Bearer ' + ctx['token'])
            # required by some services, for example github
            req.add_header('User-Agent', 'auth-daemon')
            self.log_message('Authorization Header: ' + req.headers['Authorization'])

            self.log_message('Opening request to ' + ctx['auth_service'])
            r = urllib2.urlopen(req)

            self.log_message('Reading JSON Response')
            response = json.loads(r.read())

            if ctx['verbose']:
                response_dump = json.dumps(response, indent = 4)
                self.log_message(response_dump)

            # Step 5: extract specified data from response
            ctx['action'] = 'extracting data from service response'
            self.log_message('Extracting data from service response to send to backend app')

            fields = [field.strip() for field in ctx['fields'].split(',')]

            results = { }
            for field in fields:
                v = response[field]
                if v is None or v == '':
                    response_dump = json.dumps(response, indent = 4)
                    self.auth_failed('Failed to obtain field "%s" from "%s" '
                                     % (field, response_dump))
                    return
                self.log_message('Extracted "%s" = "%s"' % (field, v))
                results[field] = v

            self.log_message('Auth OK: all fields found')
            self.send_response(200)

            # pass extracted data in response headers
            for key, value in results.items():
                hname = 'X-OAuth-%s' % (key)
                self.send_header(hname, value)

            self.end_headers()

            return

        except urllib2.HTTPError as obj:

            body = obj.read()
            self.log_message('HTTPError: ' + body)
            self.auth_failed(ctx, 'HTTP Error: %s %s, response body: %s'
                                           % (obj.code, obj.reason, body))


        except:
            self.auth_failed(ctx, 'got exception during auth')


    # Log the error and complete the request with appropriate status
    def auth_failed(self, ctx, errmsg = None):

        msg = 'Error while ' + ctx['action']
        if errmsg:
            msg += ': ' + errmsg

        ex, value, trace = sys.exc_info()

        if ex != None:
            msg += ": " + str(value)

        self.log_error(msg)
        self.send_response(403)
        self.end_headers()

        return True

    def log_message(self, format, *args):
        if len(self.client_address) > 0:
            addr = BaseHTTPRequestHandler.address_string(self)
        else:
            addr = "-"

        sys.stdout.write("%s - [%s] %s\n" % (addr, self.log_date_time_string(),
                                             format % args))

    def log_error(self, format, *args):
        self.log_message(format, *args)


class URL:
    def __init__(self, host, port=None, path=None, params=None):
        self.host = host
        self.port = port
        self.path = path
        self.params = params

    def __str__(self):
        url = "http://" + self.host
        if self.port is not None:
            url += ":" + self.port
        url += "/"
        if self.path is not None:
            url += self.path
        if self.params is not None:
            url += "?"
            url += urllib.urlencode(self.params)
        return url

def exit_handler(signal, frame):
    sys.exit(0)

if __name__ == '__main__':
    server = AuthHTTPServer(Listen, AuthHandler)
    signal.signal(signal.SIGINT, exit_handler)
    server.serve_forever()
