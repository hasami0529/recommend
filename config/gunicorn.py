# -*- coding: utf-8 -*-

bind = '0.0.0.0:8000'
accesslog = '-'
timeout = 100
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %({Header}i)s in %(D)sµs'
works = 5