

build: clean
	pelican -s settings.py -o output content/

clean:
	rm -rf output/*
