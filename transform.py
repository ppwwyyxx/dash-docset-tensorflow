#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: transform.py
# Author: Yuxin Wu


from __future__ import print_function
import sys
import os
import bs4
import magic

fname = sys.argv[1]
if not fname.endswith('.html'):
    sys.exit(0)

if 'gzip compressed' in magic.from_file(fname):
    import gzip
    f = gzip.open(fname)
else:
    f = open(fname, 'rb')
html = f.read().decode('utf-8')


def get_level():
    dirname = os.path.dirname(fname)
    cnt = 0
    while not os.path.isfile(os.path.join(dirname, 'main.css')):
        dirname = os.path.join(dirname, '..')
        cnt += 1
    return cnt


print("Processing {} ...".format(fname))
level = get_level()
soup = bs4.BeautifulSoup(html, 'lxml')


def remove(*args, **kwargs):
    rs = soup.findAll(*args, **kwargs)
    for r in rs:
        r.extract()


remove('header')
remove('footer')
remove('div', attrs={'class': 'devsite-nav-responsive-sidebar-panel'})
remove('div', attrs={'class': 'devsite-content-footer nocontent'})
remove('div', attrs={'id': 'gc-wrapper'})
# remove('nav', attrs={'class': 'devsite-section-nav devsite-nav nocontent'})
remove('nav')
remove('script')

# point to the new css
allcss = soup.findAll('link', attrs={'rel': 'stylesheet'})
if allcss:
    css = allcss[0]
    css['href'] = ''.join(['../'] * level) + 'main.css'
    for k in allcss[1:]:
        k.extract()

# mathjax doesn't work currently
# jss = soup.findAll('script')
# for js in jss:
    # if 'MathJax' in js.get('src'):
        # js['src'] = '/'.join(['..'] * level) + js['src']
        # break
with open(fname, 'w') as f:
    f.write(str(soup))
