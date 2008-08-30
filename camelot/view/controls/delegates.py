#  ==================================================================================
#
#  Copyright (C) 2007-2008 Conceptive Engineering bvba. All rights reserved.
#  www.conceptive.be / project-camelot@conceptive.be
#
#  This file is part of the Camelot Library.
#
#  This file may be used under the terms of the GNU General Public
#  License version 2.0 as published by the Free Software Foundation
#  and appearing in the file LICENSE.GPL included in the packaging of
#  this file.  Please review the following information to ensure GNU
#  General Public Licensing requirements will be met:
#  http://www.trolltech.com/products/qt/opensource.html
#
#  If you are unsure which license is appropriate for your use, please
#  review the following information:
#  http://www.trolltech.com/products/qt/licensing.html or contact
#  project-camelot@conceptive.be.
#
#  This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
#  WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#
#  For use of this library in commercial applications, please contact
#  project-camelot@conceptive.be
#
#  ==================================================================================

"""Contains classes for using custom delegates"""

import logging

logger = logging.getLogger('delegates')
logger.setLevel(logging.DEBUG)

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt

import datetime

class GenericDelegate(QtGui.QItemDelegate):
  """Manages custom delegates"""
  
  def __init__(self, parent=None):
    super(GenericDelegate, self).__init__(parent)
    self.delegates = {}

  def insertColumnDelegate(self, column, delegate):
    """Inserts a custom column delegate"""
    logger.debug('inserting a new custom column delegate')
    delegate.setParent(self)
    self.delegates[column] = delegate

  def removeColumnDelegate(self, column):
    """Removes custom column delegate"""
    logger.debug('removing a new custom column delegate')
    if column in self.delegates:
      del self.delegates[column]

  def paint(self, painter, option, index):
    """Use a custom delegate paint method if it exists"""
    delegate = self.delegates.get(index.column())
    if delegate is not None:
      delegate.paint(painter, option, index)
    else:
      QtGui.QItemDelegate.paint(self, painter, option, index)

  def createEditor(self, parent, option, index):
    """Use a custom delegate createEditor method if it exists"""
    delegate = self.delegates.get(index.column())
    if delegate is not None:
      return delegate.createEditor(parent, option, index)
    else:
      QtGui.QItemDelegate.createEditor(self, parent, option, index)

  def setEditorData(self, editor, index):
    """Use a custom delegate setEditorData method if it exists"""
    logger.debug('setting delegate data editor for column %s' % index.column())
    delegate = self.delegates.get(index.column())
    if delegate is not None:
      delegate.setEditorData(editor, index)
    else:
      QtGui.QItemDelegate.setEditorData(self, editor, index)

  def setModelData(self, editor, model, index):
    """Use a custom delegate setModelData method if it exists"""
    logger.debug('setting model data for column %s' % index.column())
    delegate = self.delegates.get(index.column())
    if delegate is not None:
      delegate.setModelData(editor, model, index)
    else:
      QtGui.QItemDelegate.setModelData(self, editor, model, index)

class IntegerColumnDelegate(QtGui.QItemDelegate):
  """Custom delegate for integer values"""

  def __init__(self, minimum=0, maximum=100, parent=None):
    super(IntegerColumnDelegate, self).__init__(parent)
    self.minimum = minimum
    self.maximum = maximum

  def createEditor(self, parent, option, index):
    from camelot.view.controls.editors import IntegerEditor
    editor = IntegerEditor(self.minimum, self.maximum, parent)
    return editor

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toInt()[0]
    editor.setValue(value)

  def setModelData(self, editor, model, index):
    editor.interpretText()
    model.setData(index, QtCore.QVariant(editor.value()))

class PlainTextColumnDelegate(QtGui.QItemDelegate):
  """Custom delegate for simple string values"""
    
  def __init__(self, parent=None):
    super(PlainTextColumnDelegate, self).__init__(parent)

  def createEditor(self, parent, option, index):
    from camelot.view.controls.editors import PlainTextEditor
    editor = PlainTextEditor(parent)
    return editor

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toString()
    editor.setText(value)

  def setModelData(self, editor, model, index):
    model.setData(index, QtCore.QVariant(editor.text()))

class DateColumnDelegate(QtGui.QItemDelegate):
  """Custom delegate for date values"""
  
  def __init__(self,
               minimum=datetime.date.min,
               maximum=datetime.date.max,
               format='dd/MM/yyyy',
               parent=None):

    super(DateColumnDelegate, self).__init__(parent)
    self.minimum = minimum 
    self.maximum = maximum
    self.format = format

  def createEditor(self, parent, option, index):
    from camelot.view.controls.editors import DateEditor
    editor = DateEditor(self.minimum, self.maximum, self.format, parent)
    return editor

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toDate()
    editor.setDate(value)

  def setModelData(self, editor, model, index):
    model.setData(index, QtCore.QVariant(editor.date()))

class FloatColumnDelegate(QtGui.QItemDelegate):
  """Custom delegate for float values"""

  def __init__(self, minimum=-100.0, maximum=100.0, precision=3, parent=None):
    super(FloatColumnDelegate, self).__init__(parent)
    self.minimum = minimum
    self.maximum = maximum
    self.precision = precision

  def createEditor(self, parent, option, index):
    from camelot.view.controls.editors import FloatEditor
    editor = FloatEditor(self.minimum, self.maximum, self.precision, parent)
    return editor

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.DisplayRole).toDouble()[0]
    editor.setValue(value)

  def setModelData(self, editor, model, index):
    editor.interpretText()
    model.setData(index, QtCore.QVariant(editor.value()))

class Many2OneColumnDelegate(QtGui.QItemDelegate):
  """Custom delegate for many 2 one relations"""
  
  def __init__(self, entity_admin, parent=None):
    logger.info('create many2onecolumn delegate')
    assert entity_admin!=None
    super(Many2OneColumnDelegate, self).__init__(parent)
    self.entity_admin = entity_admin

  def paint(self, painter, option, index):
    data = index.data().toPyObject()
    painter.drawText(option.rect, Qt.AlignLeft | Qt.AlignVCenter, unicode(data))
    
  def createEditor(self, parent, option, index):
    from camelot.view.controls.editors import Many2OneEditor
    editor = Many2OneEditor(self.entity_admin, parent)
    self.setEditorData(editor, index)
    return editor

  def setEditorData(self, editor, index):
    editor.setEntity(lambda:index.data().toPyObject())

  def setModelData(self, editor, model, index):
    #print 'current index is :', editor.currentIndex()
    pass  

class One2ManyColumnDelegate(QtGui.QItemDelegate):
  """Custom delegate for many 2 one relations"""
  
  def __init__(self, entity_admin, field_name, parent=None):
    logger.info('create one2manycolumn delegate')
    assert entity_admin!=None
    super(One2ManyColumnDelegate, self).__init__(parent)
    self.entity_admin = entity_admin
    self.field_name = field_name

  def createEditor(self, parent, option, index):
    logger.info('create a one2many editor')
    from camelot.view.controls.editors import One2ManyEditor
    editor = One2ManyEditor(self.entity_admin, self.field_name, parent)
    self.setEditorData(editor, index)
    return editor

  def setEditorData(self, editor, index):
    logger.info('set one2many editor data')
    
    def create_entity_instance_getter(model, row):
      return lambda:model._get_object(row)
    
    editor.setEntityInstance(create_entity_instance_getter(index.model(), index.row()))

  def setModelData(self, editor, model, index):
    pass  
  
class BoolColumnDelegate(QtGui.QItemDelegate):
  """Custom delegate for boolean values"""

  def __init__(self, parent=None):
    super(BoolColumnDelegate, self).__init__(parent)

  def createEditor(self, parent, option, index):
    from camelot.view.controls.editors import BoolEditor
    editor = BoolEditor(parent)
    return editor

  def setEditorData(self, editor, index):
    checked = index.model().data(index, Qt.DisplayRole).toBool()
    editor.setChecked(checked)

  def setModelData(self, editor, model, index):
    model.setData(index, QtCore.QVariant(editor.isChecked()))
