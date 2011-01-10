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

"""Tableview"""

import logging
logger = logging.getLogger( 'camelot.view.controls.tableview' )

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QSizePolicy

from camelot.view.proxy.queryproxy import QueryTableProxy
from camelot.view.controls.view import AbstractView
from camelot.view.controls.user_translatable_label import UserTranslatableLabel
from camelot.view.model_thread import post
from camelot.view.model_thread import gui_function
from camelot.view.model_thread import model_function
from camelot.view import register
from camelot.core.utils import ugettext as _

from search import SimpleSearchControl

class FrozenTableWidget( QtGui.QTableView ):
    """A table widget to be used as the frozen table widget inside a table
    widget."""

    def __init__(self, parent, columns_frozen):
        super(FrozenTableWidget, self).__init__(parent)
        self.setSelectionBehavior( QtGui.QAbstractItemView.SelectRows )
        self.setEditTriggers( QtGui.QAbstractItemView.SelectedClicked |
                              QtGui.QAbstractItemView.DoubleClicked )
        self._columns_frozen = columns_frozen

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def currentChanged(self, current, previous):
        """When the current index has changed, prevent it to jump to
        a column that is not frozen"""
        if current.column() >= self._columns_frozen:
            current = self.model().index( current.row(), -1 )
        if previous.column() >= self._columns_frozen:
            previous = self.model().index( previous.row(), -1 )
        super(FrozenTableWidget, self).currentChanged(current, previous)

class TableWidget( QtGui.QTableView ):
    """A widget displaying a table, to be used within a TableView

.. attribute:: margin

margin, specified as a number of pixels, used to calculate the height of a row
in the table, the minimum row height will allow for this number of pixels below
and above the text.

"""

    margin = 5

    def __init__( self, parent = None, columns_frozen = 0, lines_per_row = 1 ):
        """
:param columns_frozen: the number of columns on the left that don't scroll
:param lines_per_row: the number of lines of text that should be viewable in a single row.
        """
        QtGui.QTableView.__init__( self, parent )
        logger.debug( 'create TableWidget' )
        self._columns_frozen = columns_frozen
        self.setSelectionBehavior( QtGui.QAbstractItemView.SelectRows )
        self.setEditTriggers( QtGui.QAbstractItemView.SelectedClicked |
                              QtGui.QAbstractItemView.DoubleClicked |
                              QtGui.QAbstractItemView.CurrentChanged )
        self.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        self.horizontalHeader().setClickable( True )
        self._header_font_required = QtGui.QApplication.font()
        self._header_font_required.setBold( True )
        line_height = QtGui.QFontMetrics(QtGui.QApplication.font()).lineSpacing()
        self._minimal_row_height = line_height * lines_per_row + 2*self.margin
        self.verticalHeader().setDefaultSectionSize( self._minimal_row_height )
        self.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.horizontalHeader().sectionClicked.connect(
            self.horizontal_section_clicked )
        if columns_frozen:
            frozen_table_view = FrozenTableWidget(self, columns_frozen)
            frozen_table_view.setObjectName( 'frozen_table_view' )
            frozen_table_view.verticalHeader().setDefaultSectionSize( self._minimal_row_height )
            frozen_table_view.verticalHeader().hide()
            frozen_table_view.horizontalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
            frozen_table_view.horizontalHeader().sectionClicked.connect(
                self.horizontal_section_clicked )
            self.horizontalHeader().sectionResized.connect( self._update_section_width )
            self.verticalHeader().sectionResized.connect( self._update_section_height )
            frozen_table_view.verticalScrollBar().valueChanged.connect( self.verticalScrollBar().setValue )
            self.verticalScrollBar().valueChanged.connect( frozen_table_view.verticalScrollBar().setValue )
            self.viewport().stackUnder(frozen_table_view)
            frozen_table_view.setStyleSheet("QTableView { border: none;}")
            frozen_table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            frozen_table_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            frozen_table_view.show()
            frozen_table_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

    @QtCore.pyqtSlot(int, int, int)
    def _update_section_width(self, logical_index, _int, new_size):
        frozen_table_view = self.findChild(QtGui.QWidget, 'frozen_table_view' )
        if logical_index<self._columns_frozen and frozen_table_view:
            frozen_table_view.setColumnWidth( logical_index, new_size)
            self._update_frozen_table()

    @QtCore.pyqtSlot(int, int, int)
    def _update_section_height(self, logical_index, _int, new_size):
        frozen_table_view = self.findChild(QtGui.QWidget, 'frozen_table_view' )
        if frozen_table_view:
            frozen_table_view.setRowHeight(logical_index, new_size)

    def setItemDelegate(self, item_delegate):
        super(TableWidget, self).setItemDelegate(item_delegate)
        frozen_table_view = self.findChild(QtGui.QWidget, 'frozen_table_view' )
        if frozen_table_view:
            frozen_table_view.setItemDelegate(item_delegate)

    def resizeEvent(self, event):
        super(TableWidget, self).resizeEvent(event)
        self._update_frozen_table()

    def moveCursor(self, cursorAction, modifiers):
        current = super(TableWidget, self).moveCursor(cursorAction, modifiers)
        frozen_table_view = self.findChild(QtGui.QWidget, 'frozen_table_view' )
        if frozen_table_view:
            frozen_width = 0
            last_frozen =  min(self._columns_frozen, self.model().columnCount())
            for column in range(0, last_frozen):
                frozen_width += self.columnWidth(column)
            if cursorAction == QtGui.QAbstractItemView.MoveLeft and current.column() >= last_frozen and \
               self.visualRect(current).topLeft().x() < frozen_width:
                new_value = self.horizontalScrollBar().value() + self.visualRect(current).topLeft().x() - frozen_width
                self.horizontalScrollBar().setValue(new_value)
        return current

    def scrollTo(self, index, hint):
        if(index.column()>=self._columns_frozen):
            super(TableWidget, self).scrollTo(index, hint)

    def edit(self, index, trigger=None, event=None):
        #
        # columns in the frozen part should never be edited, because this might result
        # in an editor opening below the frozen column that contains the old value
        # which will be committed again when closed
        #
        if index.column() >= self._columns_frozen:
            if trigger==None and event==None:
                return super( TableWidget, self ).edit( index )
            return super( TableWidget, self ).edit( index, trigger, event )
        return False

    @QtCore.pyqtSlot()
    def _update_frozen_table(self):
        frozen_table_view = self.findChild(QtGui.QWidget, 'frozen_table_view' )
        if frozen_table_view:
            frozen_table_view.setSelectionModel(self.selectionModel())
            last_frozen =  min(self._columns_frozen, self.model().columnCount())
            frozen_width = 0
            for column in range(0, last_frozen):
                frozen_width += self.columnWidth( column )
                frozen_table_view.setColumnWidth( column,
                                                  self.columnWidth(column) )
            for column in range(last_frozen, self.model().columnCount()):
                frozen_table_view.setColumnHidden(column, True)
            frozen_table_view.setGeometry( self.verticalHeader().width() + self.frameWidth(),
                                           self.frameWidth(),
                                           frozen_width,
                                           self.viewport().height() + self.horizontalHeader().height() )

    @QtCore.pyqtSlot( int )
    def horizontal_section_clicked( self, logical_index ):
        """Update the sorting of the model and the header"""
        header = self.horizontalHeader()
        order = Qt.AscendingOrder
        if not header.isSortIndicatorShown():
            header.setSortIndicatorShown( True )
        elif header.sortIndicatorSection()==logical_index:
            # apparently, the sort order on the header is allready switched
            # when the section was clicked, so there is no need to reverse it
            order = header.sortIndicatorOrder()
        header.setSortIndicator( logical_index, order )
        self.model().sort( logical_index, order )

    def close_editor(self):
        """Close the active editor, this method is used to prevent assertion
        failures in QT when an editor is still open in the view for a cell
        that no longer exists in the model
        
        thos assertion failures only exist in QT debug builds.
        """
        current_index = self.currentIndex()
        self.closePersistentEditor( current_index )
                
    def setModel( self, model ):
        #
        # An editor might be open that is no longer available for the new
        # model.  Not closing this editor, results in assertion failures
        # in qt, resulting in segfaults in the debug build.
        #
        self.close_editor()
        #
        # Editor, closed. it should be safe to change the model
        #
        QtGui.QTableView.setModel( self, model )
        frozen_table_view = self.findChild(QtGui.QWidget, 'frozen_table_view' )
        if frozen_table_view:
            model.layoutChanged.connect( self._update_frozen_table )
            frozen_table_view.setModel( model )
            self._update_frozen_table()
        register.register( model, self )
        self.selectionModel().currentChanged.connect( self.activated )

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def activated( self, selectedIndex, previousSelectedIndex ):
        option = QtGui.QStyleOptionViewItem()
        new_size = self.itemDelegate( selectedIndex ).sizeHint( option,
                                                                selectedIndex )
        row = selectedIndex.row()
        if previousSelectedIndex.row() >= 0:
            previous_row = previousSelectedIndex.row()
            self.setRowHeight( previous_row, self._minimal_row_height )
        self.setRowHeight( row, max( new_size.height(),
                                     self._minimal_row_height ) )

class RowsWidget( QtGui.QLabel ):
    """Widget that is part of the header widget, displaying the number of rows
    in the table view"""

    _number_of_rows_font = QtGui.QApplication.font()

    def __init__( self, parent ):
        QtGui.QLabel.__init__( self, parent )
        self.setFont( self._number_of_rows_font )

    def setNumberOfRows( self, rows ):
        self.setText( _('(%i rows)')%rows )

class HeaderWidget( QtGui.QWidget ):
    """HeaderWidget for a tableview, containing the title, the search widget,
    and the number of rows in the table"""

    search_widget = SimpleSearchControl
    rows_widget = RowsWidget

    filters_changed_signal = QtCore.pyqtSignal()

    _title_font = QtGui.QApplication.font()
    _title_font.setBold( True )

    def __init__( self, parent, admin ):
        QtGui.QWidget.__init__( self, parent )
        self._admin = admin
        layout = QtGui.QVBoxLayout()
        widget_layout = QtGui.QHBoxLayout()
        search = self.search_widget( self )
        search.expand_search_options_signal.connect(
            self.expand_search_options )
        title = UserTranslatableLabel( admin.get_verbose_name_plural(),
                                       self )
        title.setFont( self._title_font )
        widget_layout.addWidget( title )
        widget_layout.addWidget( search )
        if self.rows_widget:
            self.number_of_rows = self.rows_widget( self )
            widget_layout.addWidget( self.number_of_rows )
        else:
            self.number_of_rows = None
        layout.addLayout( widget_layout )
        self._expanded_filters_created = False
        self._expanded_search = QtGui.QWidget()
        self._expanded_search.hide()
        layout.addWidget(self._expanded_search)
        self.setLayout( layout )
        self.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed )
        self.setNumberOfRows( 0 )
        self.search = search

    def _fill_expanded_search_options(self, columns):
        """Given the columns in the table view, present the user
        with more options to filter rows in the table
        :param columns: a list of tuples with field names and attributes
        """
        from camelot.view.controls.filter_operator import FilterOperator
        layout = QtGui.QHBoxLayout()
        for field, attributes in columns:
            if 'operators' in attributes and attributes['operators']:
                widget = FilterOperator( self._admin.entity,
                                         field, attributes,
                                         self )
                widget.filter_changed_signal.connect( self._filter_changed )
                layout.addWidget( widget )
        layout.addStretch()
        self._expanded_search.setLayout( layout )
        self._expanded_filters_created = True

    def _filter_changed(self):
        self.filters_changed_signal.emit()

    def decorate_query(self, query):
        """Apply expanded filters on the query"""
        if self._expanded_filters_created:
            for i in range(self._expanded_search.layout().count()):
                if self._expanded_search.layout().itemAt(i).widget():
                    query = self._expanded_search.layout().itemAt(i).widget().decorate_query(query)
        return query

    @QtCore.pyqtSlot()
    def expand_search_options(self):
        if self._expanded_search.isHidden():
            if not self._expanded_filters_created:
                post( self._admin.get_columns, self._fill_expanded_search_options )
            self._expanded_search.show()
        else:
            self._expanded_search.hide()

    @gui_function
    def setNumberOfRows( self, rows ):
        if self.number_of_rows:
            self.number_of_rows.setNumberOfRows( rows )

class TableView( AbstractView  ):
    """A generic tableview widget that puts together some other widgets.  The behaviour of this class and
  the resulting interface can be tuned by specifying specific class attributes which define the underlying
  widgets used ::

    class MovieRentalTableView(TableView):
      title_format = 'Grand overview of recent movie rentals'

  The attributes that can be specified are :

  .. attribute:: header_widget

  The widget class to be used as a header in the table view::

    header_widget = HeaderWidget

  .. attribute:: table_widget

  The widget class used to display a table within the table view ::

  table_widget = TableWidget

  .. attribute:: title_format

  A string used to format the title of the view ::

  title_format = '%(verbose_name_plural)s'

  .. attribute:: table_model

  A class implementing QAbstractTableModel that will be used as a model for the table view ::

    table_model = QueryTableProxy

  - emits the row_selected signal when a row has been selected
  """

    header_widget = HeaderWidget
    TableWidget = TableWidget

    #
    # The proxy class to use
    #
    table_model = QueryTableProxy
    #
    # Format to use as the window title
    #
    title_format = '%(verbose_name_plural)s'

    row_selected_signal = QtCore.pyqtSignal(int)

    def __init__( self, admin, search_text = None, parent = None ):
        super(TableView, self).__init__( parent )
        self.admin = admin
        post( self.get_title, self.change_title )
        widget_layout = QtGui.QVBoxLayout()
        if self.header_widget:
            self.header = self.header_widget( self, admin )
            widget_layout.addWidget( self.header )
            self.header.search.search_signal.connect( self.startSearch )
            self.header.search.cancel_signal.connect( self.cancelSearch )
            if search_text:
                self.header.search.search( search_text )
        else:
            self.header = None
        widget_layout.setSpacing( 0 )
        widget_layout.setMargin( 0 )
        splitter = QtGui.QSplitter( self )
        splitter.setObjectName('splitter')
        widget_layout.addWidget( splitter )
        table_widget = QtGui.QWidget( self )
        filters_widget = QtGui.QWidget( self )
        self.table_layout = QtGui.QVBoxLayout()
        self.table_layout.setSpacing( 0 )
        self.table_layout.setMargin( 0 )
        self.table = None
        self.filters_layout = QtGui.QVBoxLayout()
        self.filters_layout.setSpacing( 0 )
        self.filters_layout.setMargin( 0 )
        self.actions = None
        self._table_model = None
        table_widget.setLayout( self.table_layout )
        filters_widget.setLayout( self.filters_layout )
        #filters_widget.hide()
        self.set_admin( admin )
        splitter.addWidget( table_widget )
        splitter.addWidget( filters_widget )
        self.setLayout( widget_layout )
        self.search_filter = lambda q: q
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Find), self)
        shortcut.activated.connect( self.activate_search )
        if self.header_widget:
            self.header.filters_changed_signal.connect( self.rebuild_query )
        # give the table widget focus to prevent the header and its search control to
        # receive default focus, as this would prevent the displaying of 'Search...' in the
        # search control, but this conflicts with the MDI, resulting in the window not
        # being active and the menus not to work properly
        #table_widget.setFocus( QtCore.Qt.OtherFocusReason )
        #self.setFocusProxy(table_widget)
        #self.setFocus( QtCore.Qt.OtherFocusReason )
        post( self.admin.get_subclass_tree, self.setSubclassTree )

    @QtCore.pyqtSlot()
    def activate_search(self):
        self.header.search.setFocus(QtCore.Qt.ShortcutFocusReason)

    @model_function
    def get_title( self ):
        return self.title_format % {'verbose_name_plural':self.admin.get_verbose_name_plural()}

    @QtCore.pyqtSlot(list)
    @gui_function
    def setSubclassTree( self, subclasses ):
        if len( subclasses ) > 0:
            from inheritance import SubclassTree
            splitter = self.findChild(QtGui.QWidget, 'splitter' )
            class_tree = SubclassTree( self.admin, splitter )
            splitter.insertWidget( 0, class_tree )
            class_tree.subclass_clicked_signal.connect( self.set_admin )

    @QtCore.pyqtSlot(int)
    def sectionClicked( self, section ):
        """emits a row_selected signal"""
        self.row_selected_signal.emit( section )

    def copy_selected_rows( self ):
        """Copy the selected rows in this tableview"""
        logger.debug( 'delete selected rows called' )
        if self.table and self._table_model:
            for row in set( map( lambda x: x.row(), self.table.selectedIndexes() ) ):
                self._table_model.copy_row( row )

    def select_all_rows( self ):
        self.table.selectAll()

    def create_table_model( self, admin ):
        """Create a table model for the given admin interface"""
        return self.table_model( admin,
                                 None,
                                 admin.get_columns )

    def get_admin(self):
        return self.admin

    def get_model(self):
        return self._table_model

    @QtCore.pyqtSlot( object )
    @gui_function
    def set_admin( self, admin ):
        """Switch to a different subclass, where admin is the admin object of the
        subclass"""
        logger.debug('set_admin called')
        self.admin = admin
        if self.table:
            self._table_model.layoutChanged.disconnect( self.tableLayoutChanged )
            self.table_layout.removeWidget(self.table)
            self.table.deleteLater()
            self._table_model.deleteLater()
        splitter = self.findChild( QtGui.QWidget, 'splitter' )
        self.table = self.TableWidget( splitter,
                                       self.admin.list_columns_frozen,
                                       lines_per_row = self.admin.lines_per_row )
        self._table_model = self.create_table_model( admin )
        self.table.setModel( self._table_model )
        self.table.verticalHeader().sectionClicked.connect( self.sectionClicked )
        self._table_model.layoutChanged.connect( self.tableLayoutChanged )
        self.tableLayoutChanged()
        self.table_layout.insertWidget( 1, self.table )

        def get_filters_and_actions():
            return ( admin.get_filters(), admin.get_list_actions() )

        post( get_filters_and_actions,  self.set_filters_and_actions )

    @QtCore.pyqtSlot()
    @gui_function
    def tableLayoutChanged( self ):
        logger.debug('tableLayoutChanged')
        if self.header:
            self.header.setNumberOfRows( self._table_model.rowCount() )
        item_delegate = self._table_model.getItemDelegate()
        if item_delegate:
            self.table.setItemDelegate( item_delegate )
        for i in range( self._table_model.columnCount() ):
            self.table.setColumnWidth( i, self._table_model.headerData( i, Qt.Horizontal, Qt.SizeHintRole ).toSize().width() )

    def deleteSelectedRows( self ):
        """delete the selected rows in this tableview"""
        logger.debug( 'delete selected rows called' )
        confirmation_message = self.admin.get_confirm_delete()
        confirmed = True
        if confirmation_message:
            if QtGui.QMessageBox.question(self,
                                          _('Please confirm'),
                                          unicode(confirmation_message),
                                          QtGui.QMessageBox.Yes,
                                          QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                confirmed = False
        if confirmed:
            rows = set( index.row() for index in self.table.selectedIndexes() )
            self._table_model.remove_rows( set( rows ) )

    @gui_function
    def newRow( self ):
        """Create a new row in the tableview"""
        from camelot.view.workspace import show_top_level
        form = self.admin.create_new_view( parent = None,
                                           oncreate = lambda o:self._table_model.insertEntityInstance( 0, o ),
                                           onexpunge = self._table_model.remove_objects )
        show_top_level( form, self )

    def closeEvent( self, event ):
        """reimplements close event"""
        logger.debug( 'tableview closed' )
        event.accept()

    def selectTableRow( self, row ):
        """selects the specified row"""
        self.table.selectRow( row )

    def makeImport(self):
        pass
#        for row in data:
#            o = self.admin.entity()
#            #For example, setattr(x, 'foobar', 123) is equivalent to x.foobar = 123
#            # if you want to import all attributes, you must link them to other objects
#            #for example: a movie has a director, this isn't a primitive like a string
#            # but a object fetched from the db
#            setattr(o, object_attributes[0], row[0])
#            name = row[2].split( ' ' ) #director
#            o.short_description = "korte beschrijving"
#            o.genre = ""
#            from sqlalchemy.orm.session import Session
#            Session.object_session(o).flush([o])
#
#    post( makeImport )

    def selectedTableIndexes( self ):
        """returns a list of selected rows indexes"""
        return self.table.selectedIndexes()

    def getColumns( self ):
        """return the columns to be displayed in the table view"""
        return self.admin.get_columns()

    def getData( self ):
        """generator for data queried by table model"""
        for d in self._table_model.getData():
            yield d

    def getTitle( self ):
        """return the name of the entity managed by the admin attribute"""
        return self.admin.get_verbose_name()

    def viewFirst( self ):
        """selects first row"""
        self.selectTableRow( 0 )

    def viewLast( self ):
        """selects last row"""
        self.selectTableRow( self._table_model.rowCount() - 1 )

    def viewNext( self ):
        """selects next row"""
        first = self.selectedTableIndexes()[0]
        next = ( first.row() + 1 ) % self._table_model.rowCount()
        self.selectTableRow( next )

    def viewPrevious( self ):
        """selects previous row"""
        first = self.selectedTableIndexes()[0]
        prev = ( first.row() - 1 ) % self._table_model.rowCount()
        self.selectTableRow( prev )

    @QtCore.pyqtSlot(object)
    def _set_query(self, query_getter):
        if isinstance(self._table_model, QueryTableProxy):
            self._table_model.setQuery(query_getter)
        self.table.clearSelection()

    @QtCore.pyqtSlot()
    def refresh(self):
        """Refresh the whole view"""
        post( self.get_admin, self.set_admin )

    @QtCore.pyqtSlot()
    def rebuild_query( self ):
        """resets the table model query"""
        from filterlist import FilterList

        def rebuild_query():
            query = self.admin.get_query()
            # a table view is not required to have a header
            if self.header:
                query = self.header.decorate_query(query)
            filters = self.findChild(FilterList, 'filters')
            if filters:
                query = filters.decorate_query( query )
            if self.search_filter:
                query = self.search_filter( query )
            query_getter = lambda:query
            return query_getter

        post( rebuild_query, self._set_query )

    @QtCore.pyqtSlot(str)
    def startSearch( self, text ):
        """rebuilds query based on filtering text"""
        from camelot.view.search import create_entity_search_query_decorator
        logger.debug( 'search %s' % text )
        self.search_filter = create_entity_search_query_decorator( self.admin, unicode(text) )
        self.rebuild_query()

    @QtCore.pyqtSlot()
    def cancelSearch( self ):
        """resets search filtering to default"""
        logger.debug( 'cancel search' )
        self.search_filter = lambda q: q
        self.rebuild_query()

    @model_function
    def get_selection(self):
        """:return: a list with all the objects corresponding to the selected rows in the
        table """
        selection = []
        for row in set( map( lambda x: x.row(), self.table.selectedIndexes() ) ):
            selection.append( self._table_model._get_object(row) )
        return selection

    @model_function
    def get_collection(self):
        """:return: a list with all the objects corresponding to the rows in the table
        """
        return self._table_model.get_collection()

    @QtCore.pyqtSlot(tuple)
    @gui_function
    def set_filters_and_actions( self, filters_and_actions ):
        """sets filters for the tableview"""
        filters, actions = filters_and_actions
        from camelot.view.controls.filterlist import FilterList
        from camelot.view.controls.actionsbox import ActionsBox
        logger.debug( 'setting filters for tableview' )
        filters_widget = self.findChild(FilterList, 'filters')
        if filters_widget:
            filters_widget.filters_changed_signal.disconnect( self.rebuild_query )
            self.filters_layout.removeWidget(filters_widget)
            filters_widget.deleteLater()
        if self.actions:
            self.filters_layout.removeWidget(self.actions)
            self.actions.deleteLater()
            self.actions = None
        if filters:
            splitter = self.findChild( QtGui.QWidget, 'splitter' )
            filters_widget = FilterList( filters, parent=splitter )
            filters_widget.setObjectName('filters')
            self.filters_layout.addWidget( filters_widget )
            filters_widget.filters_changed_signal.connect( self.rebuild_query )
        #
        # filters might have default values, so we can only build the queries now
        #
        self.rebuild_query()
        if actions:
            #
            # Attention, the ActionBox should only contain a reference to the
            # table, and not to the table model, since this will cause the
            # garbage collector to collect them both in random order, causing
            # segfaults (see the test_qt_bindings
            #
            self.actions = ActionsBox( self,
                                       self.get_collection,
                                       self.get_selection )

            self.actions.setActions( actions )
            self.filters_layout.addWidget( self.actions )

    def to_html( self ):
        """generates html of the table"""
        if self._table_model:
            query_getter = self._table_model.get_query_getter()
            table = [[getattr( row, col[0] ) for col in self.admin.get_columns()]
                     for row in query_getter().all()]
            context = {
              'title': self.admin.get_verbose_name_plural(),
              'table': table,
              'columns': [field_attributes['name'] for _field, field_attributes in self.admin.get_columns()],
            }
            from camelot.view.templates import loader
            from jinja2 import Environment
            env = Environment( loader = loader )
            tp = env.get_template( 'table_view.html' )
            return tp.render( context )

    def importFromFile( self ):
        """"import data : the data will be imported in the activeMdiChild """
        logger.info( 'call import method' )
        from camelot.view.wizard.importwizard import ImportWizard
        wizard = ImportWizard(self, self.admin)
        wizard.exec_()


