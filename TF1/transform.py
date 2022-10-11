#!/usr/bin/env python
# File: transform.py


import sys
import os
import pathlib
import magic
import multiprocessing as mp
import time
from urllib.parse import urlparse

import bs4
import tqdm
import pygments
import pygments.lexers
import pygments.formatters
from selectolax.parser import HTMLParser

LEXER = pygments.lexers.get_lexer_by_name('python', stripall=True)
FORMATTER = pygments.formatters.HtmlFormatter()


def _read(fname):
    if 'gzip compressed' in magic.from_file(fname):
        import gzip
        f = gzip.open(fname)
    else:
        f = open(fname, 'rb')
    html = f.read().decode('utf-8')
    f.close()
    return html


def _get_level(fname):
    dirname = os.path.dirname(fname)
    cnt = 0
    while not os.path.isfile(os.path.join(dirname, 'main.css')):
        dirname = os.path.join(dirname, '..')
        cnt += 1
    return cnt


def process(fname):
    if not fname.endswith('.html'):
        return

    html = _read(fname)

    level = _get_level(fname)

    IGNORE = [
        'header', 'footer', 'devsite-book-nav', 'nav',
        'devsite-header', 'devsite-toc', 'devsite-content-footer',
        'devsite-page-rating', 'script'
    ]

    tree = HTMLParser(html)
    tree.strip_tags(IGNORE)
    for node in tree.css("div.devsite-article-meta"):
        node.decompose()

    # remove the TF2 button
    buttons = tree.css_first("table.tfo-notebook-buttons")
    if buttons:
        for node in buttons.css("td"):
            if "TensorFlow 2" in node.text():
                node.decompose()
                break

    # point to the new css
    allcss = tree.css("link[rel='stylesheet']")
    if allcss:
        css = allcss[0]
        css.attrs['href'] = ''.join(['../'] * level) + 'main.css'
        for k in allcss[1:]:
            k.decompose()

    # add method/class declarations
    title_node = tree.css_first("h1.devsite-page-title")
    if title_node:
        # mark method
        method_node = tree.css_first('h2#methods')
        if method_node:
            # print("Find class:", title)
            title_node.attrs['class'] = 'dash-class'
            title = title_node.text().strip()
            children = list(method_node.parent.iter())
            for method_idx, node in enumerate(children):
                if node.attrs.get('id') == 'methods':
                    break
            for k in range(method_idx, len(children) - 2):
                if children[k].tag == 'h3' and children[k + 2].tag == 'pre':
                    # is a method:
                    children[k].attrs['class'] = 'dash-method'
                    # print("Find method ", children[k].text())
                    name_node = children[k].child.child
                    name_node.replace_with(title + "." + name_node.text())
        else:
            title_node.attrs['class'] = 'dash-function'

    # Change all self-referential links to relative
    ROOT = './www.tensorflow.org/versions/r1.15/'  # change it when version is changed
    ANCHOR = '/api_docs/python'
    for link in tree.css('a'):
        href = link.attrs.get('href', '')
        href = urlparse(href).path
        if ANCHOR in href:
            prefix_url = href.find(ANCHOR)
            link_fname = os.path.join(ROOT, href[prefix_url + 1:])
            if not os.path.isfile(link_fname):
                link_fname += ".html"
            if os.path.isfile(link_fname):
                relpath = os.path.relpath(link_fname, start=os.path.dirname(fname))
                link.attrs['href'] = relpath

    soup = bs4.BeautifulSoup(tree.html, 'lxml')

    for pycode in soup.findAll('pre', attrs={"class": "lang-python"}):
        code = pycode.code.text
        code = pygments.highlight(code, LEXER, FORMATTER)
        # https://github.com/rushter/selectolax/issues/26
        pycode.replaceWith(bs4.BeautifulSoup(code, 'lxml'))

    MATHJAX = """
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
"""
    # mathjax only works with internet
    head = soup.findAll('head')[0]
    mathjax = bs4.BeautifulSoup(MATHJAX, 'lxml').findAll('script')
    head.extend(mathjax)

    with open(fname, 'w') as f:
        f.write(str(soup))

if __name__ == '__main__':
    path = os.path.abspath(sys.argv[1])
    if os.path.isfile(path):
        process(path)
    elif os.path.isdir(path):
        files = pathlib.Path(path).glob("**/*.html")
        files = [os.fspath(x) for x in files]
        pool = mp.Pool(int(os.cpu_count() * 1.5))
        for _ in tqdm.tqdm(
            pool.imap_unordered(process, files, chunksize=20),
            total=len(files)):
            pass
        pool.close()

