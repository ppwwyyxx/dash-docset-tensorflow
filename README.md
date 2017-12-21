# dash-docset-tensorflow
Build [dash](https://kapeli.com/dash)/[zeal](https://github.com/zealdocs/zeal) docset for [TensorFlow](https://www.tensorflow.org/).

To use, you can add this feed in Dash/Zeal:
```
https://raw.githubusercontent.com/ppwwyyxx/dash-docset-tensorflow/master/TensorFlow.xml
```
Or download the latest release [here](https://github.com/ppwwyyxx/dash-docset-tensorflow/releases).

## Steps to generate the docset
+ Install [dashing](https://github.com/technosophos/dashing): `go get -u github.com/technosophos/dashing`
+ `pip install --user python-magic beautifulsoup`
+ `cd THIS_REPO`
+ `wget -nc -np -N --compression=gzip --domains=www.tensorflow.org -e robots=off --adjust-extension -r 'https://www.tensorflow.org/versions/master/api_docs/'`
+ `cp dashing.json icon*.png main.css www.tensorflow.org`
+ `./preprocess.sh www.tensorflow.org`
+ `cd www.tensorflow.org/`
+ (optional) `find | sort -f | uniq -di | xargs rm -r` to list and remove case-insensitive duplicated files, to avoid problems on case-insensitive filesystems
+ `dashing build` will give you a `TensorFlow.docset` folder.

Right now this `dashing.json` only roughly parses function names (which is enough for me to use).
Feel free to add more features and contribute!

![screenshot](/screenshot.png)
