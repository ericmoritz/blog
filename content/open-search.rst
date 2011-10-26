Open Search
###########
:date: 2008-02-05 11:28:01
:tags: code, firefox, opensearch

With the invention of the opensearch specification, it has become super easy to create search plugins for Firefox 2.0+ and IE7.  Here's an example:

.. sourcecode::
   xml

  <?xml version="1.0"?>
  <OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/">
  <ShortName></ShortName>
  <Description></Description>
  <Image height="16" width="16" type="image/x-icon"></Image>
  <Url type="text/html" method="get" template=""/> 
  </OpenSearchDescription>

