# dash-docset-tensorflow
This is a [dashing](https://github.com/technosophos/dashing#readme)
configuration file with some scripts to help generate dash/zeal docset for [tensorflow](https://www.tensorflow.org/).

You can download the latest release [here](https://github.com/ppwwyyxx/dash-docset-tensorflow/releases).

# Steps to generate the docset
+ Install [dashing](https://github.com/technosophos/dashing#readme)
+ `cd THIS_REPO`
+ `wget --exclude-domains=github.com -r "https://www.tensorflow.org/versions/master/api_docs/python/index.html"`
+ `./preprocess.sh www.tensorflow.org`
+ `cd www.tensorflow.org/`
+ `yes | cp ../{dashing.json,icon*.png,main.css} .`
+ `dashing build` will give you a `tensorflow.docset` folder.

Right now this json only roughly parses function names (which is enough for me to use).
Feel free to add more features and contribute!

![screenshot](/screenshot.png)
