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

class LanguageEditor(QtGui.QComboBox, AbstractCustomEditor):
    """A ComboBox that shows a list of languages, the editor takes
    as its value the ISO code of the language"""

    editingFinished = QtCore.pyqtSignal()
    language_choices = []
    
    def __init__(self, parent=None, **kwargs):
        QtGui.QComboBox.__init__(self, parent)
        AbstractCustomEditor.__init__(self)
        self.index_by_language = dict()
        if not self.language_choices:
            for language in range(QtCore.QLocale.C, QtCore.QLocale.Chewa + 1):
                self.language_choices.append( (language, unicode( QtCore.QLocale.languageToString( language )) ) )
            self.language_choices.sort(key=lambda x:x[1])
        for i, (language, language_name) in enumerate( self.language_choices ):
            self.addItem( language_name, QtCore.QVariant(language) )
            self.index_by_language[ language ] = i
        self.activated.connect( self._activated )

    @QtCore.pyqtSlot(int)
    def _activated(self, _index):
        self.editingFinished.emit()
            
    def set_value(self, value):
        value = AbstractCustomEditor.set_value(self, value)
        if value:
            locale = QtCore.QLocale( value )
            self.setCurrentIndex( self.index_by_language[locale.language()] )
            
    def get_value(self):
        from camelot.core.utils import variant_to_pyobject
        current_index = self.currentIndex()
        if current_index >= 0:
            language = variant_to_pyobject(self.itemData(self.currentIndex()))
            locale = QtCore.QLocale( language )
            value = unicode( locale.name() )
        else:
            value = None
        return AbstractCustomEditor.get_value(self) or value
