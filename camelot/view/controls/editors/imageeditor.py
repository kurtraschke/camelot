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

from fileeditor import FileEditor
from fileeditor import CustomEditor
from wideeditor import WideEditor

from camelot.view.art import Icon
from camelot.core.utils import ugettext_lazy as _
from camelot.view.controls.liteboxview import LiteBoxView
from camelot.view.model_thread import post
from camelot.view.action import ActionFactory

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt

class ImageEditor(FileEditor, WideEditor):
    """Editor to view and edit image files, this is a customized
    implementation of a FileEditor"""

    filter = """Image files (*.bmp *.jpg *.jpeg *.mng *.png *.pbm *.pgm *.ppm
*.tiff *.xbm *.xpm) All files (*)"""

    def __init__(
            self,
            parent=None,
            storage=None,
            preview_width=100,
            preview_height=100,
            **kwargs
        ):
        self.preview_width = preview_width
        self.preview_height = preview_height
        FileEditor.__init__(
            self, parent=parent, storage=storage, **kwargs
        )

    def setup_widget(self):
        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins( 0, 0, 0, 0 )
        #
        # Setup label
        #
        self.label = QtGui.QLabel(self)
        self.label.installEventFilter(self)
        self.layout.addWidget(self.label)
        self.label.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        #
        # Setup buttons
        #
        button_layout = QtGui.QVBoxLayout()
        button_layout.setSpacing(0)
        button_layout.setMargin(0)

        self.open_button = QtGui.QToolButton()
        self.open_button.setIcon(self.open_icon)
        self.open_button.setAutoRaise(True)
        self.open_button.setToolTip(unicode(_('open image')))
        self.open_button.clicked.connect(self.open_button_clicked)

        self.clear_button = QtGui.QToolButton()
        self.clear_button.setIcon(self.clear_icon)
        self.clear_button.setToolTip(unicode(_('delete image')))
        self.clear_button.setAutoRaise(True)
        self.clear_button.clicked.connect(self.clear_button_clicked)
        
        copy_button = QtGui.QToolButton()
        copy_button.setDefaultAction( ActionFactory.copy(self, self.copy_to_clipboard ) )
        copy_button.setAutoRaise(True)

        paste_button = QtGui.QToolButton()
        paste_button.setDefaultAction( ActionFactory.paste(self, self.paste_from_clipboard ) )
        paste_button.setAutoRaise(True)
        paste_button.setObjectName('paste')
        
        button_layout.addStretch()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(copy_button)
        button_layout.addWidget(paste_button)

        self.layout.addLayout(button_layout)
        self.layout.addStretch()
        self.setLayout(self.layout)
        self.clear_image()
        QtGui.QApplication.clipboard().dataChanged.connect( self.clipboard_data_changed )
        self.clipboard_data_changed()
        
    @QtCore.pyqtSlot()
    def clipboard_data_changed(self):
        paste_button = self.findChild(QtGui.QWidget, 'paste')
        if paste_button:
            mime_data = QtGui.QApplication.clipboard().mimeData()
            paste_button.setVisible( mime_data.hasImage() )
            
    @QtCore.pyqtSlot()
    def paste_from_clipboard(self):
        """Paste an image from the clipboard into the editor"""
        mime_data = QtGui.QApplication.clipboard().mimeData()
        if mime_data.hasImage():
            byte_array = QtCore.QByteArray()
            buffer = QtCore.QBuffer( byte_array )
            image = QtGui.QImage( mime_data.imageData() )
            image.save( buffer, 'PNG' )
            
            def create_checkin( byte_array ):
                return lambda:self.checkin_byte_array(byte_array, '.png')
            
            post( create_checkin( byte_array ), self.stored_file_ready )
        
    def checkin_byte_array(self, byte_array, suffix):
        """Check a byte_array into the storage"""
        import cStringIO
        stream = cStringIO.StringIO( byte_array.data() )
        return self.storage.checkin_stream( 'clipboard', suffix, stream)
        
    def set_enabled(self, editable=True):
        self.clear_button.setEnabled(editable)
        self.open_button.setEnabled(editable)
        self.label.setEnabled(editable)

    def set_pixmap(self, pixmap):
        self.label.setPixmap(pixmap)
        self.draw_border()

    def set_image(self, image):
        self.set_pixmap(QtGui.QPixmap.fromImage(image))
        
    @QtCore.pyqtSlot()
    def copy_to_clipboard(self):
        """Copy the image to the clipboard"""
        if self.value:
            post( self.value.checkout_image, self.set_image_to_clipboard )
        
    def set_image_to_clipboard(self, image):
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setImage( image )

    def clear_image(self):
        dummy_image = Icon('tango/32x32/mimetypes/image-x-generic.png')
        self.set_pixmap(dummy_image.getQPixmap())

    def set_value(self, value):
        value = CustomEditor.set_value(self, value)
        if value:
            self.open_button.setIcon(self.open_icon)
            self.open_button.setToolTip(unicode(_('open file')))
            if value!=self.value:
                post(
                    lambda:value.checkout_thumbnail(
                        self.preview_width,
                        self.preview_height
                    ),
                    self.set_image
                )
        else:
            self.clear_image()
            self.open_button.setIcon(self.new_icon)
            self.open_button.setToolTip(unicode(_('add file')))
        self.value = value
        return value

    def draw_border(self):
        self.label.setFrameShape(QtGui.QFrame.Box)
        self.label.setFrameShadow(QtGui.QFrame.Plain)
        self.label.setLineWidth(1)
        self.label.setFixedSize(self.preview_width, self.preview_height)

    def show_fullscreen(self, image):
        lite_box = LiteBoxView(self)
        lite_box.show_fullscreen_image(image)

    def eventFilter(self, object, event):
        if not object.isWidgetType():
            return False
        if event.type() != QtCore.QEvent.MouseButtonPress:
            return False
        if event.modifiers() != QtCore.Qt.NoModifier:
            return False
        if event.buttons() == QtCore.Qt.LeftButton:
            if self.value:
                post(
                    lambda:self.value.checkout_thumbnail(640,480),
                    self.show_fullscreen
                )
            return True
        return False

