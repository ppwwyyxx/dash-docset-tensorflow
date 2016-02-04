#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# File: transform.py
# Author: Yuxin Wu <ppwwyyxx@gmail.com>


import sys
import os
import BeautifulSoup as bs4

fname = sys.argv[1]
if not fname.endswith('.html'):
    sys.exit(0)

def get_level():
    dirname = os.path.dirname(fname)
    cnt = 0
    while not os.path.isfile(os.path.join(dirname, 'main.css')):
        dirname = os.path.join(dirname, '..')
        cnt += 1
    return cnt

print "Processing {} ...".format(fname)
level = get_level()
html = open(fname).read()
soup = bs4.BeautifulSoup(html)

def remove(*args, **kwargs):
    rs = soup.findAll(*args, **kwargs)
    for r in rs:
        r.extract()

remove('div', attrs={'class': 'content-nav'})
remove('a', attrs={'class': 'github-ribbon'})
remove('header')

#css = soup.findAll('link', attrs={'href': '/main.css'})
#if css:
    #css = css[0]
    #css['href'] = ''.join(['../'] * level) + 'main.css'

# mathjax doesn't work currently
# jss = soup.findAll('script')
# for js in jss:
    # if 'MathJax' in js.get('src'):
        # js['src'] = '/'.join(['..'] * level) + js['src']
        # break

with open(fname, 'w') as f:
    print >> f, str(soup)
