AUTHOR = "Eric Moritz"
SITENAME = "Eric Moritz"
CATEGORY_FEED_RSS = "feeds/category/%s.rss.xml"

DEFAULT_CATEGORY = "blog"

FEED = "feeds/index.atom.xml"
FEED_RSS = "feeds/index.rss.xml"

TAG_FEED = "feeds/tags/%s.atom.xml"
TAG_FEED_RSS = "feeds/tags/%s.rss.xml"

GOOGLE_ANALYTICS = "UA-75939-1"
TWITTER_USERNAME = "ericmoritz"

MENUITEMS =[ 
    ("github", "https://github.com/ericmoritz/"),
    ("gist.github", "https://gist.github.com/ericmoritz/"),
    ("Google+", "https://plus.google.com/111783618530459182533/"),

]

WITH_PAGINATION = True
DEFAULT_PAGINATION = 20

THEME = "themes/crisp"

DEFAULT_METADATA = [
    ("author", "Eric Moritz")
    ]

GRAVATAR_HASH = "4839d0678248e68eaeed5084e788210b"
