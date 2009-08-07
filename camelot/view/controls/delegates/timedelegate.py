
from customdelegate import *

class TimeDelegate(CustomDelegate):
  
  editor = editors.TimeEditor
  
  
  
  def __init__(self, parent=None, editable=True, **kwargs):
    CustomDelegate.__init__(self, parent, editable)
    
    locale = QtCore.QLocale()
    
    self.time_format = locale.timeFormat(locale.ShortFormat)
    
    
    


  def paint(self, painter, option, index):
    
    
    painter.save()
    self.drawBackground(painter, option, index)
    
    formattedTime = unicode(index.model().data(index, Qt.EditRole).toTime().toString(self.time_format))
    

    
    editor = editors.TimeEditor( None, 
                                 self.editable )
    
    rect = option.rect
    rect = QtCore.QRect(rect.left()+3, rect.top()+6, 16, 16)
    
    if( option.state & QtGui.QStyle.State_Selected ):
        painter.fillRect(option.rect, option.palette.highlight())
        fontColor = QtGui.QColor()
        if self.editable:
          Color = option.palette.highlightedText().color()
          fontColor.setRgb(Color.red(), Color.green(), Color.blue())
        else:
          fontColor.setRgb(130,130,130)
    else:
        if self.editable:
          fontColor = QtGui.QColor()
          fontColor.setRgb(0,0,0)
        else:
          painter.fillRect(option.rect, option.palette.window())
          fontColor = QtGui.QColor()
          fontColor.setRgb(130,130,130)
        
        
    painter.setPen(fontColor.toRgb())
    rect = QtCore.QRect(option.rect.left()+23,
                        option.rect.top(),
                        option.rect.width()-23,
                        option.rect.height())
    painter.drawText(rect.x()+2,
                     rect.y(),
                     rect.width()-4,
                     rect.height(),
                     Qt.AlignVCenter | Qt.AlignRight,
                     formattedTime)
    painter.restore()
  
  
  
  def setModelData(self, editor, model, index):
    value = editor.time()
    t = datetime.time(hour=value.hour(),
                      minute=value.minute(),
                      second=value.second())
    model.setData(index, create_constant_function(t))