rm -rf code/env
cd code/
virtualenv --no-site-packages env
. env/bin/activate

pip install markdown
pip install git+https://github.com/ametaireau/pelican.git#egg=pelican
git clone https://github.com/ericmoritz/blog/
