.PHONY: all deps build

all: deps build

deps:
	pip install -r requirements.txt

build:
	rm -rf output/*
	pelican -s settings.py -o output content/
	cp -R static/* output/

deploy:
	rsync -r -av output/ eric@themoritzfamily.com:/var/www/servers/eric.themoritzfamily.com/static
	s3put --p $(pwd)/output/ --bucket eric.themoritzfamily.com -g public-read output
