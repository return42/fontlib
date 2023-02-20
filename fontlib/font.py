# -*- coding: utf-8; mode: python; mode: flycheck -*-
# pylint: disable=too-few-public-methods

"""
Implemtation of class :py:class:`Font`.
"""

__all__ = ['Font', 'FontAlias', 'FontSrcFormat']

from urllib.parse import urlparse

import mimetypes
import collections
import logging
import base64
import hashlib
from sqlalchemy import Column, String
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

import pkg_resources

from .db import FontLibSchema
from .db import TableUtilsMixIn
from .css import get_css_at_rules
from .css import FontFaceRule
from .utils import lazy_property

log = logging.getLogger(__name__)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# please pay attention when adding new formats to FONTFACE_SRC_FORMAT; it is an
# ordered dict and the first '.startswith' will match!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

FONTFACE_SRC_FORMAT = _ = collections.OrderedDict()

# https://css-tricks.com/one-file-many-options-using-variable-fonts-web/
_['woff2-variations']  = ('.woff2', )

# https://www.w3.org/TR/2018/REC-css-fonts-3-20180920/#src-desc
_['woff2']  = ('.woff2', )           # WOFF 2.0 https://www.w3.org/TR/WOFF2/
_['woff'] = ('.woff', )              # WOFF 1.0 https://www.w3.org/TR/WOFF/
_['truetype'] = ('.ttf')             # TrueType --> https://docs.microsoft.com/en-us/typography/opentype/spec/
_['opentype'] = ('.otf', 'ttf' )     # OpenType --> https://docs.microsoft.com/en-us/typography/opentype/spec/
_['embedded-opentype'] = ('.eot', )  # Embedded OpenType --> https://www.w3.org/Submission/2008/SUBM-EOT-20080305/
_['svg'] = ('.svg', '.svgz')         # SVG Font --> https://www.w3.org/TR/SVG11/fonts.html

def _guess_format(src_format_string):
    if src_format_string is None:
        return None

    src_format_string = src_format_string.lower()
    if src_format_string in FONTFACE_SRC_FORMAT.keys():
        return src_format_string

    found_format = None

    for _format, extensions in FONTFACE_SRC_FORMAT.items():
        for ext in extensions:
            if ( src_format_string.startswith(ext)           # match '.<suffix>'
                 or src_format_string.startswith(ext[1:])):  # match '<suffix>'
                found_format = _format
                break

        if found_format is not None:
            break

    if found_format is not None:
        src_format_string = found_format
    return src_format_string

class Font(FontLibSchema, TableUtilsMixIn):

    """A font resource identified by URL (ID).

    ORM of SQL table 'font'.

    """

    __tablename__ = 'font'

    id = Column(String(22), primary_key=True)
    """A url-safe hash of font's resource URL, used as unique resource ID"""

    origin = Column(String(1024), unique=True, nullable=False)
    """The URL from `CSS @font-face:src`_ of the font resource."""

    name = Column(String(80), unique=False)
    """The font-name (value of `CSS @font-face:font-family`_)"""

    unicode_range = Column(String(4098))
    """A string with the value of `CSS @font-face:unicode-range`_"""


    # https://docs.sqlalchemy.org/orm/backref.html

    aliases = relationship(
        'FontAlias'
        , back_populates = 'font'
        , uselist = True
        , cascade = 'all, delete-orphan'  # 1:N aggregation
        , doc = """A list of alias font-names (values of `CSS @font-face:font-family`_)""")

    src_formats = relationship(
        'FontSrcFormat'
        , back_populates = 'font'
        , uselist = True
        , cascade = 'all, delete-orphan'   # 1:N aggregation
        , doc = "A list of format strings (`CSS @font-face:src`_)")

    blob = relationship(
        'URLBlob'
        , back_populates = 'font'
        , uselist = False
        , cascade = ''  # 1:1 association
        , doc = """:py:class:`.urlcache.URLBlob` object from urlcache""")

    def __init__(self, origin, **kwargs):
        kwargs['origin'] = origin
        if 'id' not in kwargs:
            _ = origin.encode('utf-8')
            _ = hashlib.md5(_).digest()
            _ = base64.urlsafe_b64encode(_)[:-2]
            kwargs['id'] = _.decode('utf-8')
        super().__init__(**kwargs)

    def __repr__(self):
        return "<Font (%(name)s) id='%(id)s', origin='%(origin)s'>" % self.__dict__

    def match_name(self, name):
        """Returns ``True`` if ``name`` match one of the names"""
        return self.name == name or name in self.aliases

    @lazy_property
    def format(self):
        """String that represents the format"""
        fmt_list = []
        for row in self.src_formats:
            fmt = _guess_format(row.src_format)
            fmt_list.append(fmt)
        return ','.join(fmt_list)

    @classmethod
    def from_entry_point(cls, ep_name):
        """Build Font instances from python entry point.

        :param ep_name:
            Name of the python entry point (e.g. ``fonts_ttf`` or ``fonts_woff2``)

        :rtype: [fontlib.font.Font]
        :return:
            A generator of :py:class:`Font` instances.
        """

        ep_list = list(pkg_resources.iter_entry_points(ep_name))

        for entry_point in ep_list:
            log.debug("loading from entry point: %s (%s)", ep_name, entry_point)
            for name, file_name in entry_point.load().items():
                src_format = mimetypes.guess_type(file_name)[0]
                if src_format is not None:
                    src_format = src_format.split('/')[1]
                else:
                    src_format = file_name.split('.')[-1]
                origin = 'file:' + file_name

                # create font object
                font = Font(
                    origin = origin
                    , name = name
                )
                # create font_src_format object and append it to the font
                font.src_formats.append(
                    FontSrcFormat(
                        src_format=src_format))

                yield font

    @classmethod
    def from_css(cls, css_url):
        """Get :py:class:`Font` objects from CSS Stylesheet

        :type css_url:   str
        :param css_url:  URL of the CSS (stylesheet) file

        :rtype: [Font]
        :return:
            A generator of :py:class:`Font` instances.
        """
        at_rules = get_css_at_rules(css_url, FontFaceRule)
        for rule in at_rules:
            yield cls.from_at_rule(rule, css_url)

    @classmethod
    def from_at_rule(cls, at_rule, css_url):
        """Build Font instances from :py:class:`.css.AtRule` object.

        :param at_rule:
            ``@font-face`` rule, object of type :py:class:`.css.AtRule`

        :param css_url:
            URL of the CSS this ``@font-face`` rule comes from.  We need this
            base URL to calculate relative path names for the ``src``
            declarations.

        :rtype: [Font]
        :return:
            A generator of :py:class:`Font` instances.
        """

        base_url = "/".join(css_url.split('/')[:-1])
        src = at_rule.src()
        src_format = src['format']
        font_family = at_rule.font_family()
        unicode_range = at_rule.unicode_range()

        origin = src['url']
        url = urlparse(origin)
        if url.scheme == '' and url.netloc == '' and url.path[0] != '/':
            origin = base_url + "/" + origin

        # create font object
        font = Font(
            origin
            , name = font_family
            , unicode_range = unicode_range
        )
        # create font_src_format object and append it to the font
        font.src_formats.append(
            FontSrcFormat(
                src_format = src_format
            ))
        return font

class FontAlias(FontLibSchema, TableUtilsMixIn):

    """Object of table 'font_alias'"""

    __tablename__ = 'font_alias'

    id = Column(String(22), ForeignKey('font.id'), primary_key=True)
    id.__doc__ = Font.id.__doc__

    alias_name = Column(String(80), primary_key=True)
    """Alias font-name (value of `CSS @font-face:font-family`_)"""

    font = relationship(Font, back_populates="aliases", uselist=False)

    def __repr__(self):
        return "<FontAlias %(alias_name)s>" % self.__dict__


class FontSrcFormat(FontLibSchema, TableUtilsMixIn):

    """Object of table 'font_src_format.'"""

    __tablename__ = 'font_src_format'

    id = Column(String(22), ForeignKey('font.id'), primary_key=True)
    id.__doc__ = Font.id.__doc__

    src_format = Column(String(22), primary_key=True)
    """Format string (`CSS @font-face:src`_)"""

    font = relationship(Font, back_populates="src_formats", uselist=False)

    def __repr__(self):
        return "<FontSrcFormat %(src_format)s>" % self.__dict__
