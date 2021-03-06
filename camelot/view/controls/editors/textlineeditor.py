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

from PyQt4 import QtGui
from customeditor import AbstractCustomEditor


class TextLineEditor(QtGui.QLineEdit, AbstractCustomEditor):

    def __init__(self, parent, length=20, editable=True, **kwargs):
        QtGui.QLineEdit.__init__(self, parent)
        AbstractCustomEditor.__init__(self)
        if length:
            self.setMaxLength(length)
        if not editable:
            self.setEnabled(False)

    def set_value(self, value):
        value = AbstractCustomEditor.set_value(self, value)
        if value is not None:
            self.setText(unicode(value))
        else:
            self.setText('')
        return value

    def get_value(self):
        value_loading = AbstractCustomEditor.get_value(self)
        if value_loading is not None:
            return value_loading

        value = unicode(self.text())
        if self.value_is_none and not value:
            return None

        return value

    #def set_field_attributes(self, editable=True, background_color=None, **kwargs):
    #    super(TextLineEditor, self).set_field_attributes(editable, background_color, **kwargs)
    #    tooltip = unicode(kwargs['tooltip']) if 'tooltip' in kwargs and kwargs['tooltip'] else None
    #    if tooltip is not None:
    #        self.setToolTip(tooltip)
    #    else:
    #        self.setToolTip('')

    def set_enabled(self, editable=True):
        value = self.text()
        self.setEnabled(editable)
        self.setText(value)
