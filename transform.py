#!/usr/bin/env python
# File: transform.py


import sys
import os
import bs4
import magic
import pygments
import pygments.lexers
import pygments.formatters

fname = os.path.abspath(sys.argv[1])
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


print("Processing {} ...".format(os.path.relpath(fname)))
level = get_level()
soup = bs4.BeautifulSoup(html, 'lxml')


def remove(*args, **kwargs):
    rs = soup.findAll(*args, **kwargs)
    for r in rs:
        r.extract()


remove('header')
remove('footer')
remove('devsite-book-nav')
remove('nav')
remove('devsite-header')
remove('devsite-toc')
remove('devsite-content-footer')
remove('devsite-page-rating')
remove('div', attrs={'class': 'devsite-article-meta'})
remove('script')
# remove the TF2 button
try:
    buttons = soup.findAll('table', attrs={'class':'tfo-notebook-buttons'})
    tds = buttons[0].findAll('td')
    if len(tds) == 2:
        tds[0].extract()
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


lexer = pygments.lexers.get_lexer_by_name('python', stripall=True)
formatter = pygments.formatters.HtmlFormatter()
for pycode in soup.findAll('pre', attrs={"class": "lang-python"}):
    code = pycode.code.text
    code = pygments.highlight(code, lexer, formatter)
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


to_write = str(soup).encode('utf-8')
with open(fname, 'wb') as f:
    f.write(to_write)
