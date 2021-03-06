"""A dirty and simple HTML and XML template library.

Copyright (c) 2009 Hong, MinHee <http://dahlia.kr/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


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

You can write raw XML/HTML strings also with RawString. It puts strings
transparently without any touching.

    >>> from dirty import RawString
    >>> print(div(RawString('<a href="http://dahlia.kr/">My homepage.</a>')))
    <div><a href="http://dahlia.kr/">My homepage.</a></div>

"""

import cgi


class RawString:
    """Raw XML/HTML string. It does not escape any characters e.g. double
    quotation marks, ampersands.

        >>> print(RawString("<em>It has a ", "raw HTML string.</em>"))
        <em>It has a raw HTML string.</em>
        >>> div = Tag("div")
        >>> print(div(RawString('<a href="http://dahlia.kr/">Hello</a>')))
        <div><a href="http://dahlia.kr/">Hello</a></div>

    """

    def __init__(self, *raw_strings):
        """Creates an raw string. Accepts one or more strings as arguments."""
        self.raw_strings = raw_strings

    def __iter__(self):
        """Returns an iterator which contains a raw string.

            >>> list(RawString("<em>It has a", " raw HTML string.", "</em>"))
            ['<em>It has a', ' raw HTML string.', '</em>']

        """
        return iter(self.raw_strings)

    def __str__(self):
        """To string.

            >>> str(RawString("<em>It has a ", "raw HTML string.</em>"))
            '<em>It has a raw HTML string.</em>'

        """
        return "".join(self.raw_strings)

    def __repr__(self):
        """Representation string.

            >>> RawString("<em>It has a ", "raw HTML string.</em>")
            RawString('<em>It has a ', 'raw HTML string.</em>')
            >>> RawString("text")
            RawString('text',)

        """
        return "RawString%r" % (self.raw_strings,)


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


class Element(RawString):
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

        None objects are ignored in attributes or children.

            >>> print(Element(Tag("p"), "No class.", class_=None))
            <p>No class.</p>
            >>> Element(Tag("p"), {"class": None})
            dirty.Tag('p')()
            >>> print(Element(Tag("p"), "a", None, "b", None))
            <p>ab</p>

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
                               for name, value in attributes.items()
                               if value is not None)

    @property
    def flat_children(self, seq=None):
        for child in (seq or self.children):
            if isinstance(child, (str, RawString)):
                yield child
            elif child is not None:
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
        tag, attrs, children = self.tag, self.attributes, self.children
        if attrs and children:
            return "%s%r(%r, %r)" % (mod, tag, attrs, children)
        elif attrs:
            return "%s%r(%r)" % (mod, tag, attrs)
        elif children:
            return "%s%r(%r)" % (mod, tag, children)
        else:
            return "%s%r()" % (mod, tag)


from . import html
from . import xml

