from customdelegate import *
from camelot.view.art import Icon

class SmileyDelegate(CustomDelegate):
  """Delegate for Smiley's
"""

  __metaclass__ = DocumentationMetaclass
  
  editor = editors.SmileyEditor

  def __init__(self, parent, editable=True,  **kwargs):
    CustomDelegate.__init__(self,
                            parent=parent,
                            editable=editable,
                            maximum=1,
                            **kwargs)
    maximum = 1
    
    self.maximum = maximum
    
    
    #print self.imgPath
    
  def paint(self, painter, option, index):
    painter.save()
    img = index.model().data(index, Qt.DisplayRole).toString()
    imgPath = 'tango/16x16/emotes/' + img + '.png'
    self.drawBackground(painter, option, index)
    smiley = index.model().data(index, Qt.EditRole)
    editor = editors.SmileyEditor(parent=None, img=img, editable=self.editable)
    rect = option.rect
    rect = QtCore.QRect(rect.left()+3, rect.top()+6, rect.width()-5, rect.height())
    
    if( option.state & QtGui.QStyle.State_Selected ):
        painter.fillRect(option.rect, option.palette.highlight())
    else:
        if not self.editable:
          painter.fillRect(option.rect, option.palette.window())
    
    icon = Icon(imgPath).getQPixmap()
    QtGui.QApplication.style().drawItemPixmap(painter, rect, 1, icon)
    rect = QtCore.QRect(rect.left()+20, rect.top(), rect.width(), rect.height())
    painter.restore()