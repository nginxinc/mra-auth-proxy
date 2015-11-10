#!/usr/bin/python
#''''which python2 >/dev/null && exec python2 "$0" "$@" # '''
#''''which python  >/dev/null && exec python  "$0" "$@" # '''

# Copyright (C) 2015 Nginx, Inc.
# Orignally created by Liam Crilly, updated by Chris Stetson

import threading, sys, os, signal, base64, Cookie, urllib2, json, pydevd
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

pydevd.settrace('ngra.ps.nginxlab.com', port=8889, stdoutToServer=True, stderrToServer=True)

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

        try:

            # Step 1: get configuration from headers set in nginx.conf
            ctx['action'] = 'verifying configuration parameters'

            params = {
                'auth_service': ('X-OAuth-Service', None),
                'fields' : ('X-OAuth-Result', 'profile, email')
            }

            self.log_message('Iterating Over Params')

            for k, v in params.items():
                ctx[k] = self.headers.get(v[0], v[1])
                if ctx[k] == None:
                    self.auth_failed(ctx, 'required "%s" header was not passed' % k)
                    return

            # Step 2: check 'Authorisation' header and extract bearer token
            ctx['action'] = 'performing authorisation'

            auth_header = self.headers.get('Authorization')
            if auth_header is None:
                self.log_message('no "Authorization" header, return 401')
                self.send_response(401)
                self.end_headers()
                return

            self.log_message('Parsing Header')

            if not auth_header.lower().startswith('bearer '):
                self.auth_failed(ctx, '"Bearer" token not found')
                return

            ctx['token'] = auth_header[7:]

            # Step 3: send request to service using token
            ctx['action'] = 'authorising with openauth service'
            self.log_message('authorising with token "%s" at service "%s"'
                                         % (ctx['token'], ctx['auth_service']))

            req = urllib2.Request(ctx['auth_service'])

            req.add_header('Authorization', 'Bearer ' + ctx['token'])
            # required by some services, for example github
            req.add_header('User-Agent', 'auth-daemon')

            r = urllib2.urlopen(req)

            response = json.loads(r.read())

            if ctx['verbose']:
                response_dump = json.dumps(response, indent = 4)
                self.log_message(response_dump)

            # Step 4: extract specified data from response
            ctx['action'] = 'extracting data from service response'

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

            body = json.dumps(json.loads(obj.read()), indent=4)
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


def exit_handler(signal, frame):
    sys.exit(0)

if __name__ == '__main__':
    server = AuthHTTPServer(Listen, AuthHandler)
    signal.signal(signal.SIGINT, exit_handler)
    server.serve_forever()
