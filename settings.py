VERSION = "1"
AUTHOR = "Eric Moritz"
SITENAME = "Eric Moritz"
CATEGORY_FEED_RSS = "feeds/category/%s.rss.xml"

DEFAULT_CATEGORY = "blog"

FEED_ATOM = "feeds/index.atom.xml"
FEED_RSS = "feeds/index.rss.xml"

TAG_FEED_ATOM = "feeds/tags/%s.atom.xml"
TAG_FEED_RSS = "feeds/tags/%s.rss.xml"

GOOGLE_ANALYTICS = "UA-75939-1"
TWITTER_USERNAME = "ericmoritz"

MENUITEMS =[ 
    ("github", {"href": "https://github.com/ericmoritz/"}),
    ("Google+",{"href": "https://plus.google.com/111783618530459182533/", "rel": "author"}),
    ("Twitter",{"href": "https://twitter.com/ericmoritz"}),
]

WITH_PAGINATION = True
DEFAULT_PAGINATION = 20

THEME = "themes/crisp"

DEFAULT_METADATA = [
    ("description", "The blog of Eric Moritz"),
    ("google-site-verification", "8mRgPV6uVx5qdEcoZekq0h5h1UnHkCe3QTMwxWTYru8"),
]
LINK_RELS = [
    {"rel": "openid.server", "href": "http://www.myopenid.com/server"},
    {"rel": "openid.delegate", "href": "http://eric.moritz.myopenid.com"}
]

GRAVATAR_HASH = "4839d0678248e68eaeed5084e788210b"
DISQUS_SITENAME = "ericmoritz"

CSS_FILE = "main.css?v=" + VERSION
