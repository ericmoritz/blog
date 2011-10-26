Fun with APIs
#############
:date: 2008-06-18 16:38:41
:tags: fun, python

So, you're looking for a job you say... Need to brush up on your knowledge set... I've got the tool for you!

career_chooser.py

.. sourcecode::
   python

  import urllib
  import re
  import sys
  import cgi
  
  API_KEY="USE YOUR OWN"
  def get_result(query):
      url = "http://api.indeed.com/apisearch?q=\"%s\"&l=&start=0&limit=1&sort=&filter=on&latlong=off&key=%s&format=xml" % (query, API_KEY)
      result_count_re = re.compile(r"<totalresults>(\d+)</totalresults>")
      content = urllib.urlopen(url).read()
      
      match = result_count_re.search(content)
      if match:
          return int(match.groups()[0])
  
  def display(label, count):
      count_str = "%10d" % (count)
      spaces = 78 - (len(label) + len(count_str))
      return "%s:%s%s" % (label, " " * spaces, count_str)
  
  result_list = []
  assert len(sys.argv) > 1, "Usage %s [Query] [Query] ..." % (sys.argv[0],)
  for query in sys.argv[1:]:
      result_list.append((query, get_result(query)))
  
  result_list.sort(lambda x,y: x[1] - y[1], reverse=True)
  print "\n".join(map(lambda x: display(*x),result_list))


Try it out

.. sourcecode::
   YAML

  C:                                                                       136105
  Java:                                                                     89132
  HTML:                                                                     87963
  Assembly:                                                                 63423
  XML:                                                                      62938
  C%2B%2B:                                                                  60774
  Javascript:                                                               42368
  ASP:                                                                      42067
  Perl:                                                                     35742
  J2EE:                                                                     31609
  Visual+Basic:                                                             28924
  PHP:                                                                      17972
  ADA:                                                                      11821
  Struts:                                                                   11425
  Python:                                                                   10416
  COBOL:                                                                     6964
  Ruby:                                                                      5439
  Ruby+on+Rails:                                                             2515
  FORTRAN:                                                                   2008
  Zend:                                                                       270
  Django:                                                                     228
  CakePHP:                                                                    109
  CodeIgniter:                                                                 31
  JRuby:                                                                       30
