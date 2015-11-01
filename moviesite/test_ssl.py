#!/usr/bin/python

import httplib2
h = httplib2.Http()
h = httplib2.Http(ca_certs='/Library/Python/2.7/site-packages/httplib2-0.9.2-py2.7.egg/httplib2/cacerts.txt')
h.request('https://api.github.com/gists')

