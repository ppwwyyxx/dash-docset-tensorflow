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

    # use a faster parser for first-step fitering, then bs4
    tree = HTMLParser(html)
    tree.strip_tags(IGNORE)
    for node in tree.css("div.devsite-article-meta"):
        node.decompose()
    soup = bs4.BeautifulSoup(tree.html, 'lxml')

    # remove the TF2 button
    try:
        buttons = soup.findAll('table', attrs={'class':'tfo-notebook-buttons'})
        tds = buttons[0].findAll('td')
        for td in tds:
            if "TensorFlow 2" in td.text:
                td.extract()
                break
    except IndexError:
        pass

    # point to the new css
    allcss = soup.findAll('link', attrs={'rel': 'stylesheet'})
    if allcss:
        css = allcss[0]
        css['href'] = ''.join(['../'] * level) + 'main.css'
        for k in allcss[1:]:
            k.extract()

    # add method/class declarations
    try:
        title_node = soup.findAll('h1', attrs={'class': 'devsite-page-title'})
        if title_node:
            title_node = title_node[0]

            # mark method
            method_node = soup.findAll('h2', attrs={'id': 'methods'})
            if method_node:
                title_node.attrs['class'] = 'dash-class'
                title = title_node.getText().strip()
                # print("Find class:", title)
                body = method_node[0].parent
                children = list(body.children)
                children = [x for x in children if x != '\n']
                for method_idx, node in enumerate(children):
                    try:
                        if node.attrs.get('id') == 'methods':
                            break
                    except AttributeError:
                        pass
                for k in range(method_idx, len(children) - 2):
                    if children[k].name == 'h3' and children[k + 2].name == 'pre':
                        # is a method:
                        children[k].attrs['class'] = 'dash-method'
                        code = next(children[k].children)
                        code.string = title + '.' + code.text
                        # print("Find method ", children[k].getText())
            else:
                title_node.attrs['class'] = 'dash-function'
    except Exception:
        print("Error parsing {}".format(fname))
        raise


    for pycode in soup.findAll('pre', attrs={"class": "lang-python"}):
        code = pycode.code.text
        code = pygments.highlight(code, LEXER, FORMATTER)
        pycode.replaceWith(bs4.BeautifulSoup(code, 'lxml'))

    # mathjax doesn't work currently
    # jss = soup.findAll('script')
    # for js in jss:
                # if 'MathJax' in js.get('src'):
                    # js['src'] = '/'.join(['..'] * level) + js['src']
                    # break

    ROOT = './www.tensorflow.org/versions/r1.15/'  # change it when version is changed
    for link in soup.findAll('a'):
        href = link.attrs.get('href', '')
        href = urlparse(href).path
        # change all self-referential links to relative
        anchor = '/api_docs/python'
        if anchor in href:
            prefix_url = href.find(anchor)
            link_fname = os.path.join(ROOT, href[prefix_url + 1:])
            if not os.path.isfile(link_fname):
                link_fname += ".html"
            if os.path.isfile(link_fname):
                relpath = os.path.relpath(link_fname, start=os.path.dirname(fname))
                link.attrs['href'] = relpath

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
            pool.imap_unordered(process, files, chunksize=100),
            total=len(files)):
            pass
        pool.close()

