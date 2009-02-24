"""A dirty and simple HTML and XML template library.

Dirty is a simple DSEL template library that helps you to write some HTML
or XML markup with Python. It is inspired by Markaby.

    >>> from dirty.html import *
    >>> page = xhtml(
    ...   head(
    ...     title("Dirty"),
    ...     meta(name="Author", content="Hong, MinHee <minhee@dahlia.kr>")
    ...   ),
    ...   body(
    ...     h1("Dirty"),
    ...     p("Dirty is a simple DSEL template library that...")
    ...   )
    ... )
    >>> print(page)    # doctest: +SKIP
    <!DOCTYPE html PUBLIC
        "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" />
      <head>
        <title>Dirty</title>
        <meta content="Hong, MinHee &lt;minhee@dahlia.kr&gt;" name="Author" />
      </head>
      <body>
        <h1>Dirty</h1>
        <p>Dirty is a simple DSEL template library that...</p>
      </body>
    </html>

Output is iterable and evaluated lazily. Such behavior is important and
useful sometimes e.g. improving slowdown speed, serving big hypertext
documents. See also the Element.__iter__ method.

Use conditional operators or generator expressions if you need if-statement
or loop.

    >>> members = [{"name": "Hong, MinHee", "admin": True},
    ...            {"name": "John Doe", "admin": False}]
    >>> print(ul(
    ...    li(member["name"], class_="admin" if member["admin"] else "")
    ...    for member in members
    ... ))
    <ul><li class="admin">Hong, MinHee</li><li class="">John Doe</li></ul>

Of course, you can use list comprehensions instead, but it is evaluated
eagerly. It will make the slowdown speed seem slow.

"""

import cgi


class Tag:
    """Tag type e.g. <a>, <strong>.

        >>> strong = Tag("strong")
        >>> html = strong("This sentence is emphatic!")
        >>> str(html)
        '<strong>This sentence is emphatic!</strong>'

    It also accepts some options. Most options are for the typography of
    outputs like whitespace controls.

    For instance, a <script> tag of XHTML cannot be shorten like <script />.
    It must alway have a closing tag like <script></script>. For such cases,
    you can switch the shorten_empty_tag option off.

        >>> script = Tag("script", shorten_empty_tag=False)
        >>> str(script(src="test.js", type="text/javascript"))
        '<script src="test.js" type="text/javascript"></script>'

    Switch the cdata_section option on if the tag need CDATA section instead
    of entity escaping.

        >>> script = Tag("script", cdata_section=True)
        >>> str(script("alert(1);", type="text/javascript"))
        '<script type="text/javascript"><![CDATA[alert(1);]]></script>'

    """

    def __init__(self, name, **options):
        """Defines a new tag type. It accepts an argument which is a its name.

            >>> tag = Tag("tag-name")
            >>> tag.name
            'tag-name'

        """
        self.name = name
        self.options = options

    def __call__(self, *children, **attributes):
        return Element(self, *children, **attributes)

    def __repr__(self):
        """Representation string.

            >>> Tag("blockquote")
            Tag('blockquote')

        """
        return "Tag(%r)" % self.name


class Element:
    """HTML and XML element. In order to create a new element, call the tag
    instance.

        >>> a = Tag("a")
        >>> a("hello", href="hello.html", title="Click me")
        dirty.Tag('a')({'href': 'hello.html', 'title': 'Click me'}, ['hello'])

    """

    def __init__(self, *children, **attributes):
        """Creates a new element. Do not instantiate an element by this
        method. Instead, instantiate by a Tag instance.

            >>> Element(Tag("div")).tag
            Tag('div')

        It raises TypeError when it is not given a Tag instance.

            >>> Element("div")
            Traceback (most recent call last):
                ...
            TypeError: expected Tag, but given str
            >>> Element()
            Traceback (most recent call last):
                ...
            TypeError: missing tag

        Keyword arguments become attributes. Underscores in their names are
        replaced to dashes. First and last underscores are stripped. Such
        behavior is useful when the attribute is the same name as a Python
        keyword. All given attribute values are converted to strings.

            >>> el = Element(Tag("div"), class_="css class", attr_name=123)
            >>> str(el)
            '<div attr-name="123" class="css class" />'

        You can pass attributes by dict also.

            >>> el = Element(Tag("p"), {"class": "css class"}, "text.")
            >>> str(el)
            '<p class="css class">text.</p>'

        """
        self.children = list(c for c in children if not isinstance(c, dict))
        try:
            self.tag = self.children.pop(0)
        except IndexError:
            raise TypeError("missing tag")
        if not isinstance(self.tag, Tag):
            typename = type(self.tag).__name__
            raise TypeError("expected Tag, but given %s" % typename)
        for c in children:
            if isinstance(c, dict):
                attributes.update(c)
        self.attributes = dict((name.strip("_").replace("_", "-"), value)
                               for name, value in attributes.items())

    @property
    def flat_children(self, seq=None):
        for child in (seq or self.children):
            if isinstance(child, (str, Element)):
                yield child
            else:
                for part in Element.flat_children.fget(self, child):
                    yield part

    def __iter__(self):
        """Random splitted element string.

            >>> meta = Tag("meta")
            >>> it = iter(meta(
            ...     http_equiv="Content-Type",
            ...     content="text/html; charset=utf-8"
            ... ))
            >>> it.__next__()
            '<meta'
            >>> it.__next__()
            ' content="text/html; charset=utf-8"'
            >>> it.__next__()
            ' http-equiv="Content-Type"'
            >>> it.__next__()
            ' />'

        Its children sequence is evaluated lazily.

            >>> i = [0]
            >>> def test_generator():
            ...     while i[0] < 3:
            ...         yield str(i[0])
            ...         i[0] += 1
            ...     yield Tag("em")("fin")
            ...
            >>> el = Tag("p")(test_generator(), class_="numbers")
            >>> it = iter(el)
            >>> it.__next__(), i
            ('<p', [0])
            >>> it.__next__(), i
            (' class="numbers"', [0])
            >>> it.__next__(), i
            ('>', [0])
            >>> it.__next__(), i
            ('0', [0])
            >>> it.__next__(), i
            ('1', [1])
            >>> it.__next__(), i
            ('2', [2])
            >>> it.__next__(), i
            ('<em', [3])
            >>> it.__next__(), i
            ('>', [3])
            >>> list(it)
            ['fin', '</em>', '</p>']

        """
        yield "<" + self.tag.name
        for name, value in self.attributes.items():
            yield ' %s="%s"' % (name, cgi.escape(str(value)))
        if self.children:
            yield ">"
            for child in self.flat_children:
                if isinstance(child, str):
                    if self.tag.options.get("cdata_section"):
                        yield "<![CDATA["
                        yield child
                        yield "]]>"
                    else:
                        yield cgi.escape(child)
                else:
                    for part in child:
                        yield part
            yield "</%s>" % self.tag.name
        else:
            if self.tag.options.get("shorten_empty_tag", True):
                yield " />"
            else:
                yield "></%s>" % self.tag.name

    def __str__(self):
        """Returns a element string.

            >>> em = Tag("em")
            >>> str(em("love & peace"))
            '<em>love &amp; peace</em>'

        """
        return "".join(self)

    def __repr__(self):
        """Representation string."""
        mod = "" if __name__ == "__main__" else __name__ + "."
        return "%s%r(%r, %r)" % (mod, self.tag, self.attributes, self.children)


from . import html
from . import xml

