"""XML tag template. You should just try xml.tagname if you need <tagname>
XML tag.

    >>> atom = xml.feed(
    ...     {"xmlns": "http://www.w3.org/2005/Atom"},
    ...     xml.title("Example Feed"),
    ...     xml.link(href="http://example.org/"),
    ...     xml.updated("2003-12-13T18:30:02Z"),
    ...     xml.author(xml.name("John Doe")),
    ...     xml.id("urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6"),
    ...     xml.entry(
    ...         xml.title("Atom-Powered Robots Run Amok"),
    ...         xml.link(href="http://example.org/2003/12/13/atom03"),
    ...         xml.id("urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a"),
    ...         xml.updated("2003-12-13T18:30:02Z"),
    ...         xml.summary("Some text.")
    ...     )
    ... )
    >>> print(atom)    # doctest: +SKIP
    <feed xmlns="http://www.w3.org/2005/Atom">
      <title>Example Feed</title>
      <link href="http://example.org/" />
      <updated>2003-12-13T18:30:02Z</updated>
      <author>
        <name>John Doe</name>
      </author>
      <id>urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6</id>
      <entry>
        <title>Atom-Powered Robots Run Amok</title>
        <link href="http://example.org/2003/12/13/atom03" />
        <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
        <updated>2003-12-13T18:30:02Z</updated>
        <summary>Some text.</summary>
      </entry>
    </feed>

The example is from following URL:

    http://www.atomenabled.org/developers/syndication
          /atom-format-spec.php#rfc.section.1.1

"""

from . import Tag


class XMLTagTemplate:
    """XML tag template. Getting attribute returns a Tag instance from the
    given attribute name. Returned tags are instantiated on the fly. (However
    a tag is cached if it is instantiated once.)

        >>> xml = XMLTagTemplate()
        >>> xml.a
        Tag('a')
        >>> id(xml.a), id(xml.a)    # doctest: +SKIP
        (17005200, 17005200)

    """

    def __getattr__(self, name):
        tag = Tag(name)
        setattr(self, name, tag)
        return tag


xml = XMLTagTemplate()

