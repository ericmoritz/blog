Title: Easy ETL with RDF and Python
Date: 2014-04-15 00:00:00
Tags: RDF, ETL, pragmatic-rdf
Status: draft

So I have been tasked with optimizing our deployment pipeline.  It is
pretty obvious to us where the bottlenecks are but trying to be a data
driven developer I needed to collect stats on the current system to
know for certain where the bottlenecks are in feature deployment.

The only problem is the stages of a feature are tracked in multiple
systems.  Features are specified in Jira, implementations are
submitted as Github pull requests, tests are ran in Jenkins, code is
reviewed in Github, releases are git tags and tracked with a release
ticket in Jira.

The stages of a feature from inception, develop, verification, code
review, qa and release is tracked in all these different systems so
building a global picture of a feature's stages poses a challenge.
How do I link all this data together to construct the stages of a
feature?

Anyone who follows me on Twitter will know that I have become quite
the RDF fanatic.  It seemed only natural that I'd use RDF to link all
this data together.

First I started with a project's pull requests.  I created a simple
script that downloads the JSON for each pull request. I am exporting
the extracted data as lines of JSON packets so that I can stream these
lines to a process that turns the JSON into RDF statements.

```python
import sys
import json


###===================================================================
### from feature_scrape.extract.github
###===================================================================

def extract_pull_requests(client, repo):
    """
    Turns the closed pull requests into a sequence of JSON objects"
    """
    return url_to_object_list(
            client,
            "https://api.github.com/repos/{repo}/pulls?per_page=100&state=closed".format(repo=repo)
        )


def url_to_object_list(client, url):
    resp = requests.get(url, auth=github_auth(client))
    data = json.loads(resp.content)
    assert isinstance(data, list), "{!r} is not a list".format(data)
    return data

GithubClient = namedtuple("GithubClient", [])

def github_auth(client):
    (login, account, password) = netrc().authenticators("github.com")
    return login, password

def new_client():
    return GithubClient()

client = new_client()
for repo in sys.stdin:
    for pull in extract_pull_requests(client, repo.strip()):
        print json.dumps(pull)
```

With this script I can simply run the following to test it

```bash
echo "GannettDigital/usat-web" | ./bin/extract_github_pull_requests.py | tee "data/github/pull-requests/`uuidgen`.txt"
```

This produces a file with each pull request's JSON on each line.

```json
{"merge_commit_sha": "54fb2d31a49affafe09779740837861c9ada6a42", "comment": "truncated"}
{"merge_commit_sha": "b1dcc013d9a2ab5e022be1a23df65b37a32d1a8e", "comment": "truncated"}
{"merge_commit_sha": "062d15a2a9d885a7e729eb3580d7ca6be79be475", "comment": "truncated"}
```

Second, because developers link the Jira tickets in the comments, we
have the analyze the comments for each Pull Request for links to the
Jira tickets.  This is another reason why I export the Pull Requests
as streams of line based JSON packets.  I can pipe the Pull Request
JSON packets to this script to fetch the comments.

```bash
	cat config.txt | ./bin/extract_github_pull_requests.py | tee "data/github/pull-requests/`uuidgen`.txt" | ./bin/extract_github_pull_request_comments.py > "data/github/pull-requests-comments/`uuidgen`.txt"
```

The `./bin/extract_github_pull_request_comments.py` script takes line
oriented JSON as input and uses :

```python
from rdflib import Namespace
feature = Namespace("http://services.gannettdigital.com/vocabs/features#")

def extract_comments(client, pull):
    """
    Turns a pull request into a sequence of comment objects
    """
    comment_url = pull['_links']['comments']['href']
    for comment in url_to_object_list(client, comment_url):
	    # Use rdflib's Namespace object to create a URI for the
		# pullRequest relationship
        comment[feature.pullRequest.toPython()] = pull['url']
        yield comment

client = new_client()
# For each line in stdin, parse the line as JSON, and extract the comments
for pull_packet in sys.stdin:
    pull = json.loads(pull_packet)
    for comment in extract_comments(client, pull):
	    # print each comment as one JSON packet per line
        print json.dumps(comment)
```

I've truncated the redundant code but I think you'll see what I'm
doing pretty clearly.

Now that I've extracted the github data as JSON, I can transform it to
RDF statements.

This is quite simple, for each JSON object I yield 0 or more
statements about the JSON.

```
from rdflib import Graph
import sys
import json
from feature_scrape.models.github import map_pull
from feature_scrape.models import new_graph

g = new_graph()

for json_packet in sys.stdin:
    pull = json.loads(json_packet)
    for statement in map_pull(pull):
        g.add(statement)
print g.serialize()
```

I'll spare you from the nasty details of the `map_pull(pull)` function but this function transforms the JSON into
a single RDF graph:

```bash
cat data/github/pull-requests/*.txt | ./bin/pull_requests_to_rdf.py > data/rdf/pull-requests.rdf
```

The graph looks something like this:

```turtle
@prefix feature: <http://services.gannettdigital.com/vocabs/features#> .
@prefix github: <https://developer.github.com/v3/#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <http://schema.org/> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://api.github.com/repos/GannettDigital/usat-web/pulls/318> a feature:PullRequest ;

    rdfs:label "Long Form URL Change" ;
	schema:dateCreated "2014-02-24T19:25:42+00:00"^^xsd:dateTime ;
	feature:gitHeadSha "ffe3122d4a8a1556c54f86d38360de18c4d29d6a" ;
	feature:github <https://github.com/GannettDigital/usat-web> ;
	github:merge_commit_sha "83e77c8223fa96471786ebe45fc1be4bfbbc602a" ;
	github:review_comments <https://api.github.com/repos/GannettDigital/usat-web/pulls/318/comments> .
```

You'll notice that there is only pull request data in this graph.  
Because Jenkins posts build status as a comment on the pull request
and developers link Jira feature tickets in comments, we have to
extract more statements from the comments.

I have a `bin/pull_request_comments_to_rdf.py` script that just makes
statements about the comments as they relate to pull requests:

```bash
	cat data/github/pull-requests-comments/*.txt | ./bin/pull_request_comments_to_rdf.py > data/rdf/pull-requests-comments.rdf
```

This script produces a graph that looks something like this:

```turtle
<https://api.github.com/repos/GannettDigital/usat-web/pulls/318>
    feature:featureTicket <https://gannett.jira.com/browse/GDPWEB-1995> ;
    feature:stage <https://api.github.com/repos/GannettDigital/usat-web/issues/comments/35926475> .

<https://api.github.com/repos/GannettDigital/usat-web/issues/comments/35926475>
    a feature:BuildPassedStage ;
	schema:dateCreated "2014-02-24T19:40:40+00:00"^^xsd:dateTime .
```

Now we have the necessary information to determine which release a
pull request was first included in because of the `feature:gitHeadSha`
property.  I clone the repo locally and do a `git tag -l
--contains="ffe3122d4a8a1556c54f86d38360de18c4d29d6a"` command for
each pull request and this gives me a list of tags that I can link to
the pull request:

I wrote one more script to extract that information from the git metadata:

```turtle
<https://api.github.com/repos/GannettDigital/usat-web/pulls/318>
    feature:gitTag <https://github.com/GannettDigital/usat-web/tree/17.0> ;
    feature:stage <https://github.com/GannettDigital/usat-web/tree/17.0> .

<https://github.com/GannettDigital/usat-web/tree/17.0>
    a feature:ReleaseFinishedStage ;
    rdfs:label "17.0" ;
	schema:dateCreated "2014-03-06T21:27:50+00:00"^^xsd:dateTime .
```

So I have three different files from three different sources.  What do we do now?

```
$ ls data/rdf/*.rdf
data/rdf/git-releases.rdf           data/rdf/pull-requests-comments.rdf data/rdf/pull-requests.rdf
```

By the power of RDF, we merge all the graphs!

```python
#!/usr/bin/env python
import sys
import rdflib
from feature_scrape.models import new_graph, rdf, schema, feature
import csv
import codecs

g = new_graph()

# Load all the data
for filename in sys.stdin:
    g.parse(open(filename.strip()))

print g.serialize(format="turtle")
```

Now like magic, everything is related.

```turtle
<https://api.github.com/repos/GannettDigital/usat-web/pulls/318>
    a feature:PullRequest ;
    rdfs:label "Long Form URL Change" ;
	schema:dateCreated "2014-02-24T19:25:42+00:00"^^xsd:dateTime ;
	feature:featureTicket <https://gannett.jira.com/browse/GDPWEB-1995> ;
	feature:gitHeadSha "ffe3122d4a8a1556c54f86d38360de18c4d29d6a" ;
	feature:gitTag <https://github.com/GannettDigital/usat-web/tree/17.0> ;
	feature:github <https://github.com/GannettDigital/usat-web> ;
	feature:stage <https://api.github.com/repos/GannettDigital/usat-web/issues/comments/35926475>,
	              <https://github.com/GannettDigital/usat-web/tree/17.0> ;
	github:merge_commit_sha "83e77c8223fa96471786ebe45fc1be4bfbbc602a" ;
	github:review_comments <https://api.github.com/repos/GannettDigital/usat-web/pulls/318/comments> .

<https://api.github.com/repos/GannettDigital/usat-web/issues/comments/35926475>
    a feature:BuildPassedStage,
    feature:FeatureStage ;
	schema:dateCreated "2014-02-24T19:40:40+00:00"^^xsd:dateTime .

<https://github.com/GannettDigital/usat-web/tree/17.0> a feature:ReleaseFinishedStage ;
    rdfs:label "17.0" ;
    schema:dateCreated "2014-03-06T21:27:50+00:00"^^xsd:dateTime .
```

Finally, I can query the merged graph to sequence the feature stages:

```python
#!/usr/bin/env python
import sys
import rdflib
from feature_scrape.models import new_graph, rdf, schema, feature
import csv
import codecs

g = new_graph()

# Load all the data
for filename in sys.stdin:
    g.parse(open(filename.strip()))


# sort the stages by their created data, link them together in a linked list
records = g.query("""
SELECT ?feature_uri ?dateCreated ?stage_uri ?stage_type
WHERE
{
     ?resource feature:featureTicket ?feature_uri ;
	                feature:stage ?stage_uri .

     ?stage_uri schema:dateCreated ?dateCreated ;
	                 a ?stage_type .

     # We don't care about the super class
	      FILTER ( ?stage_type != feature:FeatureStage ) .
		  }
		  ORDER BY ?feature_uri ?dateCreated
		  """)

writer = csv.writer(codecs.EncodedFile(sys.stdout, "utf-8", "utf-8"))
writer.writerow(
    (unicode(rdf.subject), unicode(feature.stage), unicode(schema.dateCreated))
)
for record in records:
    writer.writerow(
        (unicode(record.feature_uri), unicode(record.stage_type), unicode(record.dateCreated))
    )
```

```csv
"http://www.w3.org/1999/02/22-rdf-syntax-ns#subject","http://services.gannettdigital.com/vocabs/features#stage","http://schema.org/dateCreated"
"https://gannett.jira.com/browse/GDPWEB-1995","http://services.gannettdigital.com/vocabs/features#BuildPassedStage","2014-02-24T19:40:40+00:00"
"https://gannett.jira.com/browse/GDPWEB-1995","http://services.gannettdigital.com/vocabs/features#ReleaseFinishedStage","2014-03-06T21:27:50+00:00"
```

So you can see the power of a graph data model that uses global
identifiers.  I was able to scrape data from three different sources,
with three different specialized scripts and merge that data
effortlessly and query it.

RDF takes what is usually a really cumbersome data extraction job of
inter-related objects into a simple data mapping job.  You take data
as input and map that into 0 or more statements about an URI.  You can
do that from multiple sources and merge the results and have a global
view of your objects in all the systems.

Because we're just mapping sequences of values to other sequences of
values we can easily parallelize this opperation by using
[GNU Parallel](http://www.gnu.org/software/parallel/) or even chains
of
[Hadoop Streaming Jobs](http://hadoop.apache.org/docs/r1.2.1/streaming.html).

So, if you find yourself scraping data from multiple sources or
migrating data from many systems into one, you really should look into
using RDF for your next project because it makes this stuff really
simple.

## Reference

* [My Pragmatic RDF series](./tag/pragmatic-rdf.html)
* [Source code](https://github.com/GannettDigital/value-stream-visualization)
* [RDF 1.1 primer](http://www.w3.org/TR/2014/NOTE-rdf11-primer-20140225/)
* [Programming the Semantic Web (Amazon)](http://www.amazon.com/gp/product/0596153813/ref=as_li_ss_tl?ie=UTF8&camp=1789&creative=390957&creativeASIN=0596153813&linkCode=as2&tag=erimor-20)
* [Learning SPARQL (Amazon)](http://www.amazon.com/gp/product/1449306594/ref=as_li_ss_tl?ie=UTF8&camp=1789&creative=390957&creativeASIN=1449306594&linkCode=as2&tag=erimor-20)
* [Semantic Web for the Working Ontologist, Second Edition: Effective Modeling in RDFS and OWL (Amazon)](http://www.amazon.com/gp/product/0123859654/ref=as_li_ss_tl?ie=UTF8&camp=1789&creative=390957&creativeASIN=0123859654&linkCode=as2&tag=erimor-20)
* [rdflib](https://rdflib.readthedocs.org/en/latest/)
