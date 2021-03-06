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

"""form view"""

import logging
logger = logging.getLogger('camelot.view.controls.formview')

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt

import sip

from camelot.view.art import Icon
from camelot.view.model_thread import post
from camelot.view.model_thread import model_function
from camelot.view.controls.view import AbstractView
from camelot.view.controls.statusbar import StatusBar
from camelot.view import register
from camelot.view.action import ActionFactory

class ContextMenuAction(QtGui.QAction):

    default_icon = Icon('tango/16x16/categories/applications-system.png')

    def __init__(self, parent, title, icon = None):
        """
        :param parent: the widget on which the context menu will be placed
        :param title: text displayed in the context menu
        :param icon: camelot.view.art.Icon object
        """
        super(ContextMenuAction, self).__init__(title, parent)
        self.icon = icon
        if self.icon:
            self.setIcon(self.icon.getQIcon())
        else:
            self.setIcon(self.default_icon.getQIcon())

class FormWidget(QtGui.QWidget):
    """A form widget comes inside a form view or inside an embedded manytoone editor"""

    changed_signal = QtCore.pyqtSignal()

    def __init__(self, parent, admin):
        QtGui.QWidget.__init__(self, parent)
        self._admin = admin
        widget_mapper = QtGui.QDataWidgetMapper(self)
        widget_mapper.setObjectName('widget_mapper')
        widget_layout = QtGui.QHBoxLayout()
        widget_layout.setSpacing(0)
        widget_layout.setMargin(0)
        self._index = 0
        self._model = None
        self._form = None
        self._columns = None
        self._delegate = None
        self.setLayout(widget_layout)

    def get_model(self):
        return self._model

    def set_model(self, model):
        self._model = model
        self._model.dataChanged.connect( self._data_changed )
        self._model.layoutChanged.connect( self._layout_changed )
        self._model.item_delegate_changed_signal.connect( self._item_delegate_changed )
        self._model.setObjectName( 'model' )
        widget_mapper = self.findChild(QtGui.QDataWidgetMapper, 'widget_mapper' )
        if widget_mapper:
            widget_mapper.setModel( model )
            register.register( model, widget_mapper )

        def get_columns_and_form():
            return (self._model.getColumns(), self._admin.get_form_display())

        post(get_columns_and_form, self._set_columns_and_form)

    def clear_mapping(self):
        widget_mapper = self.findChild(QtGui.QDataWidgetMapper, 'widget_mapper' )
        if widget_mapper:
            widget_mapper.clearMapping()

    def _data_changed(self, index_from, index_to):
        #@TODO: only revert if this form is in the changed range
        widget_mapper = self.findChild(QtGui.QDataWidgetMapper, 'widget_mapper' )
        if widget_mapper:
            widget_mapper.revert()
        if not sip.isdeleted(self):
            self.changed_signal.emit()

    def _layout_changed(self):
        widget_mapper = self.findChild(QtGui.QDataWidgetMapper, 'widget_mapper' )
        if widget_mapper:
            widget_mapper.revert()
        self.changed_signal.emit()

    @QtCore.pyqtSlot()
    def _item_delegate_changed(self):
        from camelot.view.controls.delegates.delegatemanager import \
            DelegateManager
        self._delegate = self._model.getItemDelegate()
        self._delegate.setObjectName('delegate')
        assert self._delegate != None
        assert isinstance(self._delegate, DelegateManager)
        self._create_widgets()

    def set_index(self, index):
        self._index = index
        widget_mapper = self.findChild(QtGui.QDataWidgetMapper, 'widget_mapper' )
        if widget_mapper:
            widget_mapper.setCurrentIndex(self._index)

    def get_index(self):
        widget_mapper = self.findChild(QtGui.QDataWidgetMapper, 'widget_mapper' )
        if widget_mapper:
            return widget_mapper.currentIndex()

    def submit(self):
        widget_mapper = self.findChild(QtGui.QDataWidgetMapper, 'widget_mapper' )
        if widget_mapper:
            widget_mapper.submit()

    def to_first(self):
        widget_mapper = self.findChild(QtGui.QDataWidgetMapper, 'widget_mapper' )
        if widget_mapper:
            widget_mapper.toFirst()
            self.changed_signal.emit()

    def to_last(self):
        widget_mapper = self.findChild(QtGui.QDataWidgetMapper, 'widget_mapper' )
        if widget_mapper:
            widget_mapper.toLast()
            self.changed_signal.emit()

    def to_next(self):
        widget_mapper = self.findChild(QtGui.QDataWidgetMapper, 'widget_mapper' )
        if widget_mapper:
            widget_mapper.toNext()
            self.changed_signal.emit()

    def to_previous(self):
        widget_mapper = self.findChild(QtGui.QDataWidgetMapper, 'widget_mapper' )
        if widget_mapper:
            widget_mapper.toPrevious()
            self.changed_signal.emit()

    def export_ooxml(self):
        from camelot.view.export.word import open_stream_in_word

        def create_ooxml_export(row):
            # print self._columns
            def ooxml_export():
                # TODO insert delegates
                fields = self._admin.get_all_fields_and_attributes()
                delegates = {}
                for field_name, attributes in fields.items():
                    delegates[field_name] = attributes['delegate'](**attributes)
                obj = self._model._get_object(row)
                document = self._form.render_ooxml(obj, delegates)
                open_stream_in_word( document )

            return ooxml_export

        post(create_ooxml_export(self.get_index()))
        
    @QtCore.pyqtSlot(tuple)
    def _set_columns_and_form(self, columns_and_form ):
        self._columns, self._form = columns_and_form
        self._create_widgets()

    def _create_widgets(self):
        """Create value and label widgets"""
        from camelot.view.controls.field_label import FieldLabel
        from camelot.view.controls.editors.wideeditor import WideEditor
        #
        # Dirty trick to make form views work during unit tests, since unit
        # tests have no event loop running, so the delegate will never be set,
        # so we get it and are sure it will be there if we are running without
        # threads
        #
        if not self._delegate:
            self._delegate = self._model.getItemDelegate()
        #
        # end of dirty trick
        #
        # only if all information is available, we can start building the form
        if not (self._form and self._columns and self._delegate):
            return
        widgets = {}
        widget_mapper = self.findChild(QtGui.QDataWidgetMapper, 'widget_mapper' )
        if not widget_mapper:
            return
        widget_mapper.setItemDelegate(self._delegate)
        option = QtGui.QStyleOptionViewItem()
        # set version to 5 to indicate the widget will appear on a
        # a form view and not on a table view
        option.version = 5

        #
        # this loop can take a while to complete, so processEvents is called
        # regulary
        #
        for i, (field_name, field_attributes ) in enumerate( self._columns):
#            if i%10==0:
#                QtCore.QCoreApplication.processEvents(
#                    QtCore.QEventLoop.ExcludeSocketNotifiers,
#                    100
#                )
            model_index = self._model.index(self._index, i)
            hide_title = False
            if 'hide_title' in field_attributes:
                hide_title = field_attributes['hide_title']
            widget_label = None
            widget_editor = self._delegate.createEditor(
                self,
                option,
                model_index
            )
            widget_editor.setObjectName('%s_editor'%field_name)
            if not hide_title:
                widget_label = FieldLabel(
                    field_name,
                    field_attributes['name'],
                    field_attributes,
                    self._admin
                )
                widget_label.setObjectName('%s_label'%field_name)
                if not isinstance(widget_editor, WideEditor):
                    widget_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

            # required fields font is bold
            if ('nullable' in field_attributes) and \
               (not field_attributes['nullable']):
                font = QtGui.QApplication.font()
                font.setBold(True)
                widget_label.setFont(font)

            assert widget_editor != None
            assert isinstance(widget_editor, QtGui.QWidget)

            widget_mapper.addMapping(widget_editor, i)
            widgets[field_name] = (widget_label, widget_editor)

        widget_mapper.setCurrentIndex(self._index)
        self.layout().insertWidget(0, self._form.render(widgets, self))
        #self._widget_layout.setContentsMargins(7, 7, 7, 7)


class FormView(AbstractView):
    """A FormView is the combination of a FormWidget, possible actions and menu
    items

    .. form_widget: The class to be used as a the form widget inside the form
    view"""

    form_widget = FormWidget

    def __init__(self, title, admin, model, index):
        AbstractView.__init__(self)

        layout = QtGui.QVBoxLayout()
        form_and_actions_layout = QtGui.QHBoxLayout()
        form_and_actions_layout.setObjectName('form_and_actions_layout')
        layout.addLayout(form_and_actions_layout)

        self.model = model
        self.admin = admin
        self.title_prefix = title

        form = FormWidget(self, admin)
        form.setObjectName( 'form' )
        form.changed_signal.connect( self.update_title )
        form.set_model(model)
        form.set_index(index)
        form_and_actions_layout.addWidget(form)

        statusbar = StatusBar(self)
        statusbar.setObjectName('statusbar')
        statusbar.setSizeGripEnabled(False)
        layout.addWidget(statusbar)
        layout.setAlignment(statusbar, Qt.AlignBottom)
        self.setLayout(layout)

        self.change_title(title)

        if hasattr(admin, 'form_size') and admin.form_size:
            self.setMinimumSize(admin.form_size[0], admin.form_size[1])

        self.validator = admin.create_validator(model)
        self.validate_before_close = True

        def get_actions():
            return admin.get_form_actions(None)

        post(get_actions, self.setActions)
        self.update_title()
        #
        # Define actions
        #
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.addAction( ActionFactory.view_first(self, self.viewFirst) )
        self.addAction( ActionFactory.view_last(self, self.viewLast) )
        self.addAction( ActionFactory.view_next(self, self.viewNext) )
        self.addAction( ActionFactory.view_previous(self, self.viewPrevious) )
        self.addAction( ActionFactory.refresh(self, self.refresh_session) )
        self.addAction( ActionFactory.export_ooxml(self, form.export_ooxml) )

    @QtCore.pyqtSlot()
    def refresh_session(self):
        from elixir import session
        from camelot.core.orm import refresh_session
        refresh_session( session )
                
    @QtCore.pyqtSlot()
    def refresh(self):
        """Refresh the data in the current view"""
        self.model.refresh()
    
    def update_title(self):

        def get_title():
            obj = self.getEntity()
            return u'%s %s' % (
                self.title_prefix,
                self.admin.get_verbose_identifier(obj)
            )

        post(get_title, self.change_title)

    def getEntity(self):
        form = self.findChild(QtGui.QWidget, 'form' )
        if form:
            return self.model._get_object(form.get_index())

    @QtCore.pyqtSlot(list)
    def setActions(self, actions):
        form = self.findChild(QtGui.QWidget, 'form' )
        layout = self.findChild(QtGui.QLayout, 'form_and_actions_layout' )
        if actions and form and layout:
            side_panel_layout = QtGui.QVBoxLayout()
            from camelot.view.controls.actionsbox import ActionsBox
            logger.debug('setting Actions for formview')
            actions_widget = ActionsBox(self, self.getEntity)
            actions_widget.setObjectName('actions')
            action_widgets = actions_widget.setActions(actions)
            for action_widget in action_widgets:
                form.changed_signal.connect( action_widget.changed )
                action_widget.changed()
            side_panel_layout.insertWidget(1, actions_widget)
            side_panel_layout.addStretch()
            layout.addLayout(side_panel_layout)

    def viewFirst(self):
        """select model's first row"""
        form = self.findChild(QtGui.QWidget, 'form' )
        if form:
            form.submit()
            form.to_first()

    def viewLast(self):
        """select model's last row"""
        # submit should not happen a second time, since then we don't want
        # the widgets data to be written to the model
        form = self.findChild(QtGui.QWidget, 'form' )
        if form:
            form.submit()
            form.to_last()

    def viewNext(self):
        """select model's next row"""
        # submit should not happen a second time, since then we don't want
        # the widgets data to be written to the model
        form = self.findChild(QtGui.QWidget, 'form' )
        if form:
            form.submit()
            form.to_next()

    def viewPrevious(self):
        """select model's previous row"""
        # submit should not happen a second time, since then we don't want
        # the widgets data to be written to the model
        form = self.findChild(QtGui.QWidget, 'form' )
        if form:
            form.submit()
            form.to_previous()

    @QtCore.pyqtSlot(bool)
    def showMessage(self, valid):
        form = self.findChild(QtGui.QWidget, 'form' )
        if not valid and form:
            reply = self.validator.validityDialog(
                form.get_index(), self
            ).exec_()
            if reply == QtGui.QMessageBox.Discard:
            # clear mapping to prevent data being written again to the model,
            # then we reverted the row
                form.clear_mapping()
                self.model.revertRow(form.get_index())
                self.validate_before_close = False
                self.close()
        else:
            self.validate_before_close = False
            self.close()

    def validateClose(self):
        logger.debug('validate before close : %s' % self.validate_before_close)
        form = self.findChild(QtGui.QWidget, 'form' )
        if self.validate_before_close and form:
            # submit should not happen a second time, since then we don't
            # want the widgets data to be written to the model
            form.submit()

            def validate():
                return self.validator.isValid(form.get_index())

            post(validate, self.showMessage)
            return False

        return True

    def closeEvent(self, event):
        #print 'close event'
        logger.debug('formview closed')
        if self.validateClose():
            event.accept()
        else:
            event.ignore()
        
    @model_function
    def toHtml(self):
        """generates html of the form"""
        from jinja2 import Environment

        def to_html(d = u''):
            """Jinja 1 filter to convert field values to their default html
            representation
            """

            def wrapped_in_table(env, context, value):
                if isinstance(value, list):
                    return u'<table><tr><td>' + \
                           u'</td></tr><tr><td>'.join(
                                [unicode(e) for e in value]
                           ) + u'</td></tr></table>'
                return unicode(value)

            return wrapped_in_table

        entity = self.getEntity()
        fields = self.admin.get_fields()
        table = [dict( field_attributes = field_attributes,
                      value = getattr(entity, name ))
                      for name, field_attributes in fields]

        context = {
          'title': self.admin.get_verbose_name(),
          'table': table,
        }

        from camelot.view.templates import loader
        env = Environment(loader = loader)
        env.filters['to_html'] = to_html
        tp = env.get_template('form_view.html')

        return tp.render(context)

