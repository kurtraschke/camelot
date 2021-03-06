#  ============================================================================
#
#  Copyright (C) 2007-2010 Conceptive Engineering bvba. All rights reserved.
#  www.conceptive.be / project-camelot@conceptive.be
#
#  This file is part of the Camelot Library.
#
#  This file may be used under the terms of the GNU General Public
#  License version 2.0 as published by the Free Software Foundation
#  and appearing in the file license.txt included in the packaging of
#  this file.  Please review this information to ensure GNU
#  General Public Licensing requirements will be met.
#
#  If you are unsure which license is appropriate for your use, please
#  visit www.python-camelot.com or contact project-camelot@conceptive.be
#
#  This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
#  WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#
#  For use of this library in commercial applications, please contact
#  project-camelot@conceptive.be
#
#  ============================================================================

"""Utility functions"""

from PyQt4 import QtGui
from PyQt4 import QtCore

import logging
logger = logging.getLogger('camelot.core.utils')


def create_constant_function(constant):
    return lambda:constant


class CollectionGetterFromObjectGetter(object):
    """Convert an object getter to a collection getter.  The resulting
    class is callable and will make sure object_getter is only called
    once, even if collection getter is called multiple times.
    """

    def __init__(self, object_getter):
        """:param object_getter: a function that returns the object to
        be put in the collection.
        """
        self._object_getter = object_getter
        self._collection = None

    def __call__(self):
        if not self._collection:
            self._collection = [self._object_getter()]
        return self._collection


"""
A Note on GUI Types

Because QVariant is part of the QtCore library, it cannot provide conversion
functions to data types defined in QtGui, such as QColor, QImage, and QPixmap.
In other words, there is no toColor() function. Instead, you can use the
QVariant.value() or the qVariantValue() template function. For example:

 QVariant variant;
 ...
 QColor color = variant.value<QColor>();

The inverse conversion (e.g., from QColor to QVariant) is automatic for all
data types supported by QVariant, including GUI-related types:

 QColor color = palette().background().color();
 QVariant variant = color;
"""
def variant_to_pyobject(qvariant=None):
    """Try to convert a QVariant to a python object as good as possible"""
    import datetime
    if not qvariant:
        return None
    if qvariant.isNull():
        return None
    type = qvariant.type()
    if type == QtCore.QVariant.String:
        value = unicode(qvariant.toString())
    elif type == QtCore.QVariant.Date:
        value = qvariant.toDate()
        value = datetime.date(year=value.year(),
                              month=value.month(),
                              day=value.day())
    elif type == QtCore.QVariant.Int:
        value = int(qvariant.toInt()[0])
    elif type == QtCore.QVariant.LongLong:
        value = int(qvariant.toLongLong()[0])
    elif type == QtCore.QVariant.Double:
        value = float(qvariant.toDouble()[0])
    elif type == QtCore.QVariant.Bool:
        value = bool(qvariant.toBool())
    elif type == QtCore.QVariant.Time:
        value = qvariant.toTime()
        value = datetime.time(hour = value.hour(),
                              minute = value.minute(),
                              second = value.second())
    elif type == QtCore.QVariant.DateTime:
        value = qvariant.toDateTime()
        value = value.toPyDateTime ()
    elif type == QtCore.QVariant.Color:
        value = QtGui.QColor(qvariant)
    else:
        value = qvariant.toPyObject()

    return value


#
# Global dictionary containing all user defined translations in the
# current locale
#
_translations_ = {}

def set_translation(source, value):
    """Store a tranlation in the global translation dictionary"""
    _translations_[source] = value

def load_translations():
    """Fill the global dictionary of translations with all data from the
    database, to be able to do fast gui thread lookups of translations"""
    language = unicode(QtCore.QLocale().name())
    from sqlalchemy import sql
    from camelot.model.i18n import Translation
    # only load translations when the camelot model is active
    if not hasattr(Translation, 'query'):
        return
    query = sql.select( [Translation.source, Translation.value],
                        whereclause = sql.and_(Translation.language==language,
                                               Translation.value!=None,
                                               Translation.value!=u'') )
    for source, value in Translation.query.session.execute(query):
        _translations_[source] = value


def ugettext(string_to_translate):
    """Translate the string_to_translate to the language of the current locale.
    This is a two step process.  First the function will try to get the
    translation out of the Translation entity, if this is not successfull, the
    function will ask QCoreApplication to translate string_to_translate (which
    tries to get the translation from the .po files)"""
    assert isinstance(string_to_translate, basestring)
    result = _translations_.get(string_to_translate, None)
    if not result:
        result = unicode(QtCore.QCoreApplication.translate(
            '',
            QtCore.QString(string_to_translate)
        ))
    return result


def dgettext(domain, message):
    """Like ugettext but look the message up in the specified domain.
    This uses the Translation table.
    """
    assert isinstance(message, basestring)
    from camelot.model.i18n import Translation
    from sqlalchemy import sql
    query = sql.select( [Translation.value],
                          whereclause = sql.and_(Translation.language.like('%s%%'%domain),
                                                 Translation.source==message) ).limit(1)
    for translation in Translation.query.session.execute(query):
        return translation[0]
    return message


class ugettext_lazy(object):

    def __init__(self, string_to_translate):
        assert isinstance(string_to_translate, basestring)
        self._string_to_translate = string_to_translate

    def __str__(self):
        return ugettext(self._string_to_translate)

    def __unicode__(self):
        return ugettext(self._string_to_translate)


def xls2list(xf):
    import xlrd
    matrix = []
    s = xlrd.open_workbook(xf).sheets()[0] # assume a single sheet xls doc
    for r in range(s.nrows):
        vector = []
        for c in range(s.ncols):
            cell = s.cell(r, c)
            type = xlrd.sheet.ctype_text[cell.ctype]
            if type == 'xldate':
                t = xlrd.xldate_as_tuple(cell.value, datemode=0)
                value = '%02d/%02d/%d' % (t[2], t[1], t[0])
            else:
                value = cell.value
            #vector.append((type, value))
            vector.append(value)
        matrix.append(vector)
    return matrix


def format_float(value, precision=3):
    return QtCore.QString("%L1").arg(float(value), 0, 'f', precision)
