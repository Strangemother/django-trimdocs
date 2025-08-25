"""Markdown with no changes as an overhead.

        md = ReducedMarkdown(extensions=[])
        r = md.convert(text)
        assert r == text
        print("Done. no change:")
"""
import difflib

import xml.etree.ElementTree as etree
from xml.etree.ElementTree import ProcessingInstruction
from xml.etree.ElementTree import Comment, ElementTree, Element, QName, HTML_EMPTY

import markdown

from markdown import util
from markdown.blockparser import BlockParser
from markdown.serializers import _escape_cdata, _escape_attrib_html
from markdown import blockprocessors, treeprocessors
from markdown import inlinepatterns

class ParagraphProcessor(blockprocessors.ParagraphProcessor):
    """ Process Paragraph blocks. """

    def test(self, parent, block: str) -> bool:
        return True

    def run(self, parent, blocks):
        block = blocks.pop(0)
        if block.strip():
            # Create a regular paragraph
            p = etree.SubElement(parent, 'div')
            p.text = block.lstrip()
            # if parent.text:
            #     parent.text = '{}\n\n{}'.format(parent.text, block)
            # else:
            #     parent.text = block.lstrip()

        return

        if block.strip():
            # Not a blank block. Add to parent, otherwise throw it away.
            if self.parser.state.isstate('list'):
                # The parent is a tight-list.
                #
                # Check for any children. This will likely only happen in a
                # tight-list when a header isn't followed by a blank line.
                # For example:
                #
                #     * # Header
                #     Line 2 of list item - not part of header.
                sibling = self.lastChild(parent)
                if sibling is not None:
                    # Insert after sibling.
                    if sibling.tail:
                        sibling.tail = '{}\n{}'.format(sibling.tail, block)
                    else:
                        sibling.tail = '\n%s' % block
                else:
                    # Append to parent.text
                    if parent.text:
                        parent.text = '{}\n{}'.format(parent.text, block)
                    else:
                        parent.text = block.lstrip()
            else:
                # Create a regular paragraph
                p = etree.SubElement(parent, 'p')
                p.text = block.lstrip()
                # if parent.text:
                #     parent.text = '{}\n\n{}'.format(parent.text, block)
                # else:
                #     parent.text = block.lstrip()


def build_treeprocessors(md, **kwargs):
    """ Build the default  `treeprocessors` for Markdown. """
    tp = util.Registry()
    tp.register(treeprocessors.InlineProcessor(md), 'inline', 20)
    tp.register(treeprocessors.PrettifyTreeprocessor(md), 'prettify', 10)
    tp.register(treeprocessors.UnescapeTreeprocessor(md), 'unescape', 0)
    return tp


def build_block_parser(md, **kwargs):
    """ Build the default block parser used by Markdown. """
    parser = BlockParser(md)
    # parser.blockprocessors.register(blockprocessors.EmptyBlockProcessor(parser), 'empty', 100)
    # parser.blockprocessors.register(blockprocessors.ListIndentProcessor(parser), 'indent', 90)
    # parser.blockprocessors.register(blockprocessors.CodeBlockProcessor(parser), 'code', 80)
    # parser.blockprocessors.register(blockprocessors.HashHeaderProcessor(parser), 'hashheader', 70)
    # parser.blockprocessors.register(blockprocessors.SetextHeaderProcessor(parser), 'setextheader', 60)
    # parser.blockprocessors.register(blockprocessors.HRProcessor(parser), 'hr', 50)
    # parser.blockprocessors.register(blockprocessors.OListProcessor(parser), 'olist', 40)
    # parser.blockprocessors.register(blockprocessors.UListProcessor(parser), 'ulist', 30)
    # parser.blockprocessors.register(blockprocessors.BlockQuoteProcessor(parser), 'quote', 20)

    """replace [link] refs
    """
    parser.blockprocessors.register(blockprocessors.ReferenceProcessor(parser), 'reference', 15)
    # parser.blockprocessors.register(blockprocessors.ParagraphProcessor(parser), 'paragraph', 10)
    parser.blockprocessors.register(ParagraphProcessor(parser), 'paragraph', 10)
    return parser


# def _escape_cdata(text) -> str:
#     return text

# def _escape_attrib_html(text) -> str:
#     return text



def _serialize_html(write, elem, format) -> None:
    tag = elem.tag
    text = elem.text
    if tag is Comment:
        write("<!--%s-->" % _escape_cdata(text))
    elif tag is ProcessingInstruction:
        write("<?%s?>" % _escape_cdata(text))
    elif tag is None:
        if text:
            write(_escape_cdata(text))
        for e in elem:
            _serialize_html(write, e, format)
    else:
        namespace_uri = None
        if isinstance(tag, QName):
            # `QNAME` objects store their data as a string: `{uri}tag`
            if tag.text[:1] == "{":
                namespace_uri, tag = tag.text[1:].split("}", 1)
            else:
                raise ValueError('QName objects must define a tag.')
        write("<" + tag)
        items = elem.items()
        if items:
            items = sorted(items)  # lexical order
            for k, v in items:
                if isinstance(k, QName):
                    # Assume a text only `QName`
                    k = k.text
                if isinstance(v, QName):
                    # Assume a text only `QName`
                    v = v.text
                else:
                    v = _escape_attrib_html(v)
                if k == v and format == 'html':
                    # handle boolean attributes
                    write(" %s" % v)
                else:
                    write(' {}="{}"'.format(k, v))
        if namespace_uri:
            write(' xmlns="%s"' % (_escape_attrib(namespace_uri)))
        if format == "xhtml" and tag.lower() in HTML_EMPTY:
            write(" />")
        else:
            write(">")
            if text:
                if tag.lower() in ["script", "style"]:
                    write(text)
                else:
                    write(_escape_cdata(text))
            for e in elem:
                _serialize_html(write, e, format)
            if tag.lower() not in HTML_EMPTY:
                write("</" + tag + ">")
    if elem.tail:
        write(_escape_cdata(elem.tail))

from markdown.extensions.meta import MetaPreprocessor


class ReducedMarkdown(markdown.Markdown):

    def __init__(self, **kwargs):
        super().__init__()
        self.serializer = self.dirty_render

    def dirty_render(self, root):
        assert root is not None
        data = []
        write = data.append
        _serialize_html(write, root, format)
        return "".join(data)


    def build_parser(self):
        # We change all patterns
        super().build_parser()

        # self.preprocessors = util.Registry()
        self.parser = build_block_parser(self)
        self.update_inlinepatterns()
        self.treeprocessors = build_treeprocessors(self)
        self.postprocessors = util.Registry()
        self.preprocessors.register(MetaPreprocessor(self), 'meta', 27)
        return self

    def update_inlinepatterns(self):
        self.inlinePatterns = util.Registry()
        REFERENCE_RE = inlinepatterns.REFERENCE_RE
        LINK_RE = inlinepatterns.LINK_RE
        ipm = inlinepatterns
        md = self
        # self.inlinePatterns.register(ipm.LinkInlineProcessor(ipm.LINK_RE, self), 'link', 160)
        self.inlinePatterns.register(ipm.ReferenceInlineProcessor(ipm.REFERENCE_RE, self), 'reference', 170)
        # self.inlinePatterns.register(ipm.BacktickInlineProcessor(ipm.BACKTICK_RE), 'backtick', 190)
        # self.inlinePatterns.register(ipm.EscapeInlineProcessor(ipm.ESCAPE_RE, md), 'escape', 180)
        # self.inlinePatterns.register(ipm.ImageInlineProcessor(ipm.IMAGE_LINK_RE, md), 'image_link', 150)
        # self.inlinePatterns.register(ipm.ImageReferenceInlineProcessor(ipm.IMAGE_REFERENCE_RE, md), 'image_reference', 140)
        self.inlinePatterns.register(ipm.ShortReferenceInlineProcessor(ipm.REFERENCE_RE, md), 'short_reference', 130)
        # self.inlinePatterns.register(ipm.ShortImageReferenceInlineProcessor(ipm.IMAGE_REFERENCE_RE, md), 'short_image_ref', 125)
        # self.inlinePatterns.register(ipm.AutolinkInlineProcessor(ipm.AUTOLINK_RE, md), 'autolink', 120)
        # self.inlinePatterns.register(ipm.AutomailInlineProcessor(ipm.AUTOMAIL_RE, md), 'automail', 110)
        # self.inlinePatterns.register(ipm.SubstituteTagInlineProcessor(ipm.LINE_BREAK_RE, 'br'), 'linebreak', 100)
        # self.inlinePatterns.register(ipm.HtmlInlineProcessor(ipm.HTML_RE, md), 'html', 90)
        # self.inlinePatterns.register(ipm.HtmlInlineProcessor(ipm.ENTITY_RE, md), 'entity', 80)
        # self.inlinePatterns.register(ipm.SimpleTextInlineProcessor(ipm.NOT_STRONG_RE), 'not_strong', 70)
        # self.inlinePatterns.register(ipm.AsteriskProcessor(r'\*'), 'em_strong', 60)
        # self.inlinePatterns.register(ipm.UnderscoreProcessor(r'_'), 'em_strong2', 50)
