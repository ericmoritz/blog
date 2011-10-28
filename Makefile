
build:
	pelican -s settings.py -o output content/
	cp -R static/* output/
