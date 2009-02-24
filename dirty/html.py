"""HTML tags. Some tags are specialized e.g. xhtml, script."""

from . import Tag, Element

TAG_NAMES = ["a", "abbr", "acronym", "address", "applet", "area", "b", "base",
             "basefont", "bdo", "big", "blockquote", "body", "br", "button",
             "caption", "center", "cite", "code", "col", "colgroup", "dd",
             "del_", "dfn", "dir", "div", "dl", "dt", "em", "fieldset", "font",
             "form", "frame", "frameset", "h1", "h2", "h3", "h4", "h5", "h6",
             "head", "hr", "html", "i", "iframe", "img", "input", "ins",
             "isindex", "kbd", "label", "legend", "li", "link", "map", "menu",
             "meta", "noframes", "noscript", "object", "ol", "optgroup",
             "option", "param", "p", "pre", "q", "s", "samp", "select", "small",
             "span", "strike", "strong", "style", "sub", "sup", "table",
             "tbody", "td", "textarea", "tfoot", "th", "thead", "title", "tr",
             "tt", "u", "ul", "var", "xmp"]


class xhtml(Element):
    """XHTML document element. It prints a XHTML 1.0 Strict DTD before <html>
    and a xmlns attribute.

        >>> print(xhtml())
        <!DOCTYPE html PUBLIC
            "-//W3C//DTD XHTML 1.0 Strict//EN"
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" />

    """

    DTD = "<!DOCTYPE html PUBLIC\n" \
          '    "-//W3C//DTD XHTML 1.0 Strict//EN"\n' \
          '    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'

    XMLNS = "http://www.w3.org/1999/xhtml"

    def __init__(self, *children, **attributes):
        Element.__init__(self, html, *children, xmlns=self.XMLNS, **attributes)

    def __iter__(self):
        yield self.DTD
        yield "\n"
        for part in Element.__iter__(self):
            yield part


class script(Element):
    """
    A specialized tag for <script>. It switches the shorten_empty_tag option
    off and cdata_section on.

        >>> print(script(src="dirty.js", type="text/javascript"))
        <script src="dirty.js" type="text/javascript"></script>
        >>> print(script({"type": "text/javascript"}, "alert(1);"))
        <script type="text/javascript">
        // <![CDATA[
        alert(1);
        // ]]>
        </script>

    """

    tag = Tag("script", shorten_empty_tag=False, cdata_section=True)

    def __init__(self, *children, **attributes):
        Element.__init__(self, self.tag, *children, **attributes)

    def __iter__(self):
        for part in Element.__iter__(self):
            if part in ("<![CDATA[", "]]>"):
                yield "\n// %s\n" % part
            else:
                yield part


for _html_tag in TAG_NAMES:
    globals()[_html_tag] = Tag(_html_tag)
