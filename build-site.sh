rm -rf code/env
cd code/
virtualenv --no-site-packages env
. env/bin/activate

pip install markdown
pip install git+https://github.com/ametaireau/pelican.git#egg=pelican
git clone https://github.com/ericmoritz/blog/

cd ..
mkdir -p etc/nginx.d
cp code/blog/etc/nginx.d/redirects.conf etc/nginx.d/
