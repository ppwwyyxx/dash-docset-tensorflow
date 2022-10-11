#!/usr/bin/env python
import sys
import os
import pathlib
import multiprocessing as mp
import json

import bs4
import tqdm
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import misaka


LEXER = pygments.lexers.get_lexer_by_name('python', stripall=True)
FORMATTER = pygments.formatters.HtmlFormatter()
TEMPLATE = open(os.path.dirname(__file__) + "/template.html").read()
TF_VERSION = json.loads(open(os.path.dirname(__file__) + "/meta.json").read())["version"]

# Reference: https://github.com/reuben/gen_tf_docset/blob/main/gen.py
class HighlighterRenderer(misaka.HtmlRenderer):
    def blockcode(self, text, lang):
        if not lang:
            lang = 'python'
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except:
            lexer = get_lexer_by_name('text', stripall=True)
        formatter = HtmlFormatter()
        return pygments.highlight(text, lexer, formatter)

    def table(self, content):
        return '<table class="table">\n' + content + '\n</table>'

RENDERER = misaka.Markdown(HighlighterRenderer(),
    extensions=('fenced-code', 'no-intra-emphasis', 'tables', 'autolink', 'space-headers', 'strikethrough', 'superscript'))

def _get_level(fname):
    # tf.md -> 0
    # tf/xx.md -> 1
    dirname = os.path.dirname(fname)
    cnt = 0
    while not os.path.isfile(os.path.join(dirname, 'tf.md')):
        dirname = os.path.join(dirname, '..')
        cnt += 1
    return cnt

def process(fname):
    if not fname.endswith('.md'):
        return
    outfile = fname[:-2] + "html"
    level = _get_level(fname)

    with open(fname) as f:
        markdown = f.readlines()
        if markdown[0].startswith("description:"):
            # Remove the useless top description.
            markdown = markdown[1:]
        html = RENDERER("".join(markdown))
    assert 'page_type' not in html[:30], fname

    is_class = '<meta itemprop="property"' in html

    html = TEMPLATE.replace("REPLACE_ME", html)
    soup = bs4.BeautifulSoup(html, 'lxml')

    # Highlight code
    for pycode in soup.findAll('pre', attrs={"class": "lang-py"}):
        code = pycode.code.text
        code = pygments.highlight(code, LEXER, FORMATTER)
        pycode.replaceWith(bs4.BeautifulSoup(code, 'lxml'))

    # Identify methods/functions
    h1 = soup.findAll('h1')[0]
    h1.attrs["class"] = "dash-class" if is_class else "dash-function"
    if is_class:
        h3s = soup.findAll('h3')
        for h3 in h3s:
            h3.attrs["class"] = "dash-method"
            # Set correct method name.
            list(h3.children)[0].replace_with(h1.text + "." + h3.text)

    style_link = '<link rel="stylesheet" href="' + ('../' * level) + 'style.css"/>\n'
    title = f'<title>{h1.text} | TensorFlow {TF_VERSION}</title>'
    HEAD = style_link + title
    head = soup.findAll('head')[0]
    head.extend(list(bs4.BeautifulSoup(HEAD, 'lxml').html.head.children))

    html = str(soup)
    with open(outfile, 'w') as f:
        f.write(html)


if __name__ == '__main__':
    path = os.path.abspath(sys.argv[1])
    if os.path.isfile(path):
        process(path)
    elif os.path.isdir(path):
        files = pathlib.Path(path).glob("**/*.md")
        files = [os.fspath(x) for x in files]
        pool = mp.Pool(int(os.cpu_count() * 1.5))
        for _ in tqdm.tqdm(
                pool.imap_unordered(process, files, chunksize=20),
                total=len(files)):
            pass
        pool.close()

