#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# File: transform.py
# Author: 
#   Yuxin Wu <ppwwyyxx@gmail.com>
#   Tianling Bian <bian_tianling@icloud.com>


import sys
import os
import bs4
import magic
# import ipdb

fname = sys.argv[1]
if not fname.endswith('.html'):
    sys.exit(0)

if 'gzip compressed' in magic.from_file(fname):
    import gzip
    f = gzip.open(fname)
else:
    f = open(fname)
html = f.read().decode('utf-8')

def get_level():
    dirname = os.path.dirname(fname)
    cnt = 0
    while not os.path.isfile(os.path.join(dirname, 'main.css')):
        dirname = os.path.join(dirname, '..')
        cnt += 1
    return cnt

print "Processing {} ...".format(fname)
level = get_level()
soup = bs4.BeautifulSoup(html, 'html.parser')

def remove(*args, **kwargs):
    rs = soup.findAll(*args, **kwargs)
    for r in rs:
        r.extract()

remove('header')
remove('footer')
remove('nav', attrs={'class': 'devsite-section-nav devsite-nav nocontent'})
remove('script')

# decide page type and modify page title id
title_id = None
if soup.findAll('h2', attrs={'id': 'classes'}):
    title_id = 'Module'
elif soup.findAll('h2', attrs={'id': 'modules'}):
    title_id = 'Module'
elif soup.findAll('h2', attrs={'id': 'functions'}):
    title_id = 'Module'
elif soup.findAll('h2', attrs={'id': 'properties'}):
    title_id = 'Class'
elif soup.findAll('h4', attrs={'id': 'returns'}):
    title_id = 'Function'
# embed title_id into page title
titles = soup.findAll('h1', attrs={'class': 'devsite-page-title'})
if titles:
    titles[0].attrs['id'] = title_id

# # point to the new css
# allcss = soup.findAll('link', attrs={'rel': 'stylesheet'})
# if allcss:
#     css = allcss[0]
#     css['href'] = ''.join(['../'] * level) + 'main.css'
#     for k in allcss[1:]:
#         k.extract()

# # filter buggy title
# h4s = soup.findAll('h4')
# if h4s:
#     for h4 in h4s:
#         if '{:#' in h4.text:
#             code = h4.findAll('code')[0]
#             h4.contents = [code]

# mathjax doesn't work currently
# jss = soup.findAll('script')
# for js in jss:
    # if 'MathJax' in js.get('src'):
        # js['src'] = '/'.join(['..'] * level) + js['src']
        # break
with open(fname, 'w') as f:
    print >> f, str(soup)
