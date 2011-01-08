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
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

from customdelegate import CustomDelegate, DocumentationMetaclass, not_editable_background
from camelot.view.controls import editors
from camelot.core.utils import variant_to_pyobject
from camelot.view.proxy import ValueLoading

class ColorDelegate(CustomDelegate):
  
    __metaclass__ = DocumentationMetaclass
    
    editor = editors.ColorEditor
    
    def paint(self, painter, option, index):
        painter.save()
        self.drawBackground(painter, option, index)
        background_color = QtGui.QColor(index.model().data(index, Qt.BackgroundRole))
        if (option.state & QtGui.QStyle.State_Selected):
            painter.fillRect(option.rect, option.palette.highlight())
        elif not self.editable:
            painter.fillRect(option.rect, QtGui.QColor(not_editable_background))
        else:
            painter.fillRect(option.rect, background_color)
        color = variant_to_pyobject(index.model().data(index, Qt.EditRole))
        if color not in (None, ValueLoading):
            pixmap = QtGui.QPixmap(16, 16)
            qcolor = QtGui.QColor()
            qcolor.setRgb(*color)
            pixmap.fill(qcolor)
            rect = QtCore.QRect(option.rect.left()+40,
                              option.rect.top(),
                              option.rect.width()-23,
                              option.rect.height())
            
            QtGui.QApplication.style().drawItemPixmap(painter,
                                                      rect,
                                                      Qt.AlignVCenter,
                                                      pixmap)
            
        painter.restore()

