
build:
	rm -rf output/*
	pelican -s settings.py -o output content/
	cp -R static/* output/
