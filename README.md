# dash-docset-tensorflow
This is a [dashing](https://github.com/technosophos/dashing#readme)
configuration file with some scripts to help generate dash/zeal docset for [tensorflow](https://www.tensorflow.org/).

# Steps to generate the docset
+ Install [dashing](https://github.com/technosophos/dashing#readme)
+ cd THIS_REPO
+ wget -r "https://www.tensorflow.org"
+ ./preprocess.sh www.tensorflow.org
+ cd www.tensorflow.org/
+ `cp THIS_REPO/{dashing.json,icon.png,main.css} .`
+ `dashing build` will give you a `tensorflow.docset` folder.

Right now this json only roughly parses function names (which is enough for me to use).
Feel free to add more features and contribute!
