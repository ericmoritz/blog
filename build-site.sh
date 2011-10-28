rm -rf code/
virtualenv --no-site-packages code/env
cd code/
. env/bin/activate

pip install markdown
pip install git+https://github.com/ametaireau/pelican.git#egg=pelican
git clone https://github.com/ericmoritz/blog/
