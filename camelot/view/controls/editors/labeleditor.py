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
from PyQt4 import QtCore

from customeditor import AbstractCustomEditor

class LabelEditor(QtGui.QLabel, AbstractCustomEditor):
    editingFinished = QtCore.pyqtSignal()
    def __init__(self,
                 parent=None,
                 text="<loading>",
                 **kwargs):
        QtGui.QLabel.__init__(self, parent)
        AbstractCustomEditor.__init__(self)
        # do not set disabled, it is quite pointless for LabelEditor
        #self.setEnabled(False)
        self.setOpenExternalLinks(True)
        self.text = text

    def set_value(self, value):
        self.setEnabled(True)
        value = AbstractCustomEditor.set_value(self, value)
        if value:
            self.setText(value)

