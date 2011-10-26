Template Tag Caveat
###################
:date: 2008-06-17 21:46:55
:tags: django

In the Django template system.  There is a small caveat that you need to 
recognize when developing your own template tags.

When Django parses the Node tree it creates a template.Node instance for 
each template tag in the template.  The node tree is just like our beloved 
HTML DOM.  

So for instance take the following

.. sourcecode::
   html

    <ul>
      <li>1</li>
      <li>2</li>
      <li>3</li>
      <li>4</li>
      <li>5</li>    
    </ul>

That turns into something like this

.. sourcecode::
   html   

    <ul:Element>
      <li:HTMLElement>
      <li:HTMLElement>
      <li:HTMLElement>
      <li:HTMLElement>
      <li:HTMLElement>

The indention shows that the li's are child nodes of the ul tag. Each li in a 
different instance of an HTMLElement, each with their own state.

So for a Django Template take the following

.. sourcecode::
   django

    {% block content %}
      {% firstof var1 var2 var3 %}
      {% firstof var1 var2 var3 %}
      {% firstof var1 var2 var3 %}
      {% firstof var1 var2 var3 %}  
    {% endblock %}

The node tree would look like this

.. sourcecode::
   xml

    <BlockNode>
      <FirstOfNode>
      <FirstOfNode>
      <FirstOfNode>
      <FirstOfNode>  

So we have a block node with four FirstOfNode instances

In python this would translate roughly to

.. sourcecode::
   python

    f1 = FirstOfNode(...)
    f2 = FirstOfNode(...)
    f3 = FirstOfNode(...)
    f4 = FirstOfNode(...)
    
    f1.render()
    f2.render()
    f3.render()
    f4.render()

Everything looks fine here.  Render is called once per node instance.

Now, check this out

.. sourcecode::
   django

    {% block content %} 
      {% for i in value_list %} 
        {% repr obj %} 
      {% endfor %} 
    {% endblock %}

The node tree that django builds would look something like this

.. sourcecode::
   xml

    <BlockNode> 
      <ForNode> 
        <ReprNode>

Now each node in that tree is it's own object instance with it's own
state.  This can be an issue if you don't realize one thing, each node
is persistent while the template is rendering.

Let me write out how the template rendering of the a loop would look
in python with the ReprNode

.. sourcecode::
   python

    repr_node = ReprNode("obj")
    
    for i in range(10): 
        repr_node.render(context)

Can you tell what the problem?  We're calling the render method
on the same instance of the Node.

Let's peek under the covers and look at ReprNode's definition

.. sourcecode::
   python

  
    class ReprNode(template.Node): 
        def __init__(self, obj) 
            self.obj = obj
    
        def render(self, context): 
            self.obj = template.resolve_variable(self.obj, context)
            return str(self.obj)
    
        def do_repr(parser, token): 
            tag_name, obj = token.split_contents()
            return ReprNode(obj)


Now look at what's going on.  self.obj is assumed to be the name of the 
variable in the context.  That's fine when render is called once.  When render
called a second time, self.obj is now the actual value of obj from the context.
What happens when you try to resolve that?  You get a VariableDoesNotExist 
error, uh oh!

I made the assumption that render() is only called once.  You don't realize 
that inside a for tag, the render method is called repeatedly.  This can cause
tons of issues.  If it wasn't a huge design change, Template Nodes should 
probably be Static classes.

I don't know if this is technically a bug in the Django templating system, 
bad design, bad documentation, or just simply poor assumptions on my part, but
I came across this issue today and it took stepping through PDB to find the 
problem with my custom template tag (the ReprNode was completely made up for 
the example)

Example code <http://www.djangosnippets.org/snippets/811/>
