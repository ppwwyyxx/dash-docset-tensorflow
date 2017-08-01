# dash-docset-tensorflow
Build [dash](https://kapeli.com/dash)/[zeal](https://github.com/zealdocs/zeal) docset for [TensorFlow](https://www.tensorflow.org/).

You can download the latest release [here](https://github.com/ppwwyyxx/dash-docset-tensorflow/releases). Or add this feed `dash-feed://https%3A//raw.githubusercontent.com/kho/dash-docset-tensorflow/master/TensorFlow.xml` directly in Dash/Zeal.

## Steps to generate the docset
+ Install [dashing](https://github.com/technosophos/dashing): `go get -u github.com/technosophos/dashing`
+ `pip install --user python-magic beautifulsoup`
+ `cd THIS_REPO`
+ `wget --header 'Accept-Encoding: deflate' --domains=www.tensorflow.org -e robots=off --no-parent --adjust-extension -r 'https://www.tensorflow.org/versions/master/api_docs/'`
+ `cp dashing.json icon*.png main.css www.tensorflow.org`
+ `./preprocess.sh www.tensorflow.org`
+ `cd www.tensorflow.org/`
+ `dashing build` will give you a `TensorFlow.docset` folder.

Right now this `dashing.json` only roughly parses function names (which is enough for me to use).
Feel free to add more features and contribute!

![screenshot](/screenshot.png)
