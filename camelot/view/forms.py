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

"""Classes to layout fields on a form.  These are mostly used for specifying the
form_display attribute in Admin classes, but they can be used on their own as
well.  Form classes can be used recursive.
"""

import logging
logger = logging.getLogger( 'camelot.view.forms' )

from camelot.view.model_thread import gui_function

class Form( object ):
    """Base Form class to put fields on a form.  A form can be converted to a
    QT widget by calling its render method.  The base form uses the QFormLayout
    to render a form::

    class Admin(EntityAdmin):
      form_display = Form(['title', 'short_description', 'director', 'release_date'])

    .. image:: ../_static/form/form.png
    """

    def __init__( self, content, scrollbars = False, columns = 1  ):
        """
        :param content: a list with the field names and forms to render
        :param columns: the number of columns in which to order the fields.

        eg : with 2 columns, the fields ['street', 'city', 'country'] will
        be ordered as :

        +-------------+--------------+
        | street      | city         |
        +-------------+--------------+
        | country     |              |
        +-------------+--------------+

        """
        assert isinstance( content, list )
        self._content = content
        self._scrollbars = scrollbars
        self._columns = columns

    def get_fields( self ):
        """:return: the fields, visible in this form"""
        return [field for field in self._get_fields_from_form()]

    def _get_fields_from_form( self ):
        for field in self._content:
            if isinstance( field, Form ):
                for nested_field in  field._get_fields_from_form():
                    yield nested_field
            else:
                assert isinstance( field, ( str, unicode ) )
                yield field;


    def remove_field( self, original_field ):
        """Remove a field from the form, This function can be used to modify
        inherited forms.

        :param original_field: the name of the field to be removed
        :return: True if the field was found and removed
        """
        for c in self._content:
            if isinstance( c, Form ):
                c.remove_field( original_field )
            if original_field in self._content:
                self._content.remove( original_field )
                return True
            if original_field in self._fields:
                self._fields.remove( original_field )
                return True
        return False

    def replace_field( self, original_field, new_field ):
        """Replace a field on this form with another field.  This function can be used to
        modify inherited forms.

        :param original_field : the name of the field to be replace
        :param new_field : the name of the new field
        :return: True if the original field was found and replaced.
        """
        for i, c in enumerate( self._content ):
            if isinstance( c, Form ):
                c.replace_field( original_field, new_field )
            elif c == original_field:
                self._content[i] = new_field
                return True
        return False

    def add_field( self, new_field ):
        self._content.append( new_field )

    def __unicode__( self ):
        return 'Form(%s)' % ( u','.join( unicode( c ) for c in self._content ) )

    def render_ooxml( self, obj, delegates ):
        """Generator for lines of text in Office Open XML representing this form, using tables
        :param obj: the object or entity that will be rendered
        :param delegates: a dictionary mapping field names to their delegate
        """
        yield '<w:tbl>'
        yield '    <w:tblPr>'
        yield '      <w:tblW w:w="0" w:type="auto"/>'
        yield '      <w:tblBorders>'
        yield '          <w:top w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="auto"/>'
        yield '          <w:left w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="auto"/>'
        yield '          <w:bottom w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="auto"/>'
        yield '          <w:right w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="auto"/>'
        yield '          <w:insideH w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="auto"/>'
        yield '          <w:insideV w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="auto"/>'
        yield '        </w:tblBorders>'
        yield '      <w:tblLook w:val="04A0"/>'
        yield '    </w:tblPr>'
        yield '    <w:tblGrid>'
        yield '      <w:gridCol w:w="4811"/>'
        yield '      <w:gridCol w:w="4811"/>'
        yield '    </w:tblGrid>'
        yield '    <w:tr>'
        for index, field in enumerate(self._content):
            if index % self._columns == 0 and index != 0:
                yield '    </w:tr><w:tr>'
            yield '<w:tc>'
            yield '  <w:tcPr>'
            yield '    <w:tcW w:w="4811" w:type="dxa"/>'
            yield '    <w:shd w:val="clear" w:color="auto" w:fill="auto"/>'
            yield '  </w:tcPr>'
            yield '<w:p>'
            lines = []
            if isinstance(field, Label):
                lines = field.render_ooxml()
            elif isinstance(field, Form):
                lines = field.render_ooxml( obj, delegates )
            elif isinstance(field, basestring):
                delegate = delegates[field]
                value = getattr(obj, field)
                lines = delegate.render_ooxml(value)
            for line in lines:
                yield line
            yield '</w:p>'
            yield '</w:tc>'
        yield '</w:tr>'
        yield '</w:tbl>'

    @gui_function
    def render( self, widgets, parent = None, nomargins = False):
        """:param widgets: a dictionary mapping each field in this form to a tuple
        of (label, widget editor)

        :return: a QWidget into which the form is rendered
        """
        logger.debug( 'rendering %s' % self.__class__.__name__ )
        from camelot.view.controls.editors.wideeditor import WideEditor

        from PyQt4 import QtGui
        form_layout = QtGui.QGridLayout()

        # where 1 column in the form is a label and a field, so two columns in the grid
        columns = min(self._columns, len(self._content))
        # make sure all columns have the same width
        if columns > 1:
            for i in range(columns*2):
                form_layout.setColumnStretch(i, 1)

        row_span = 1

        class cursor(object):

            def __init__(self):
                self.row = 0
                self.col = 0

            def next_row(self):
                self.row = self.row + 1
                self.col = 0

            def next_col(self):
                self.col = self.col + 2
                if self.col >= columns * 2:
                    self.next_row()

            def next_empty_row(self):
                if self.col!=0:
                    self.next_row()

            def __str__(self):
                return '%s,%s'%(self.row, self.col)

        c = cursor()
        
        has_vertical_expanding_row = False
        for field in self._content:
            if isinstance( field, Form ):
                has_vertical_expanding_row = True
                c.next_empty_row()
                col_span = 2 * columns
                f = field.render( widgets, parent, True )
                if isinstance( f, QtGui.QLayout ):
                    form_layout.addLayout( f, c.row, c.col, row_span, col_span )
                else:
                    form_layout.addWidget( f, c.row, c.col, row_span, col_span )
                c.next_row()
            elif field in widgets:
                label, editor = widgets[field]
                if isinstance( editor, ( WideEditor, ) ):
                    c.next_empty_row()
                    col_span = 2 * columns
                    if label:
                        form_layout.addWidget( label, c.row, c.col, row_span, col_span )
                        c.next_row()
                    form_layout.addWidget( editor, c.row, c.col, row_span, col_span )
                    c.next_row()
                else:
                    col_span = 1
                    if label:
                        form_layout.addWidget( label, c.row, c.col, row_span, col_span )
                    form_layout.addWidget( editor, c.row, c.col + 1, row_span, col_span )
                    c.next_col()
                size_policy = editor.sizePolicy()
                if size_policy.verticalPolicy()==QtGui.QSizePolicy.Expanding:
                    has_vertical_expanding_row = True
            else:
                logger.warning('ProgrammingError : widgets should contain a widget for field %s'%unicode(field))

        if self._content and form_layout.count():
#            # get last item in the layout
#            last_item = form_layout.itemAt( form_layout.count() - 1 )
#
#            # if last item does not contain a widget, 0 is returned
#            # which is fine with the isinstance test
#            w = last_item.widget()
#
#            # add stretch only if last item is not expandable
#            last_size_policy = w.sizePolicy()
#            if last_size_policy.verticalPolicy()==QtGui.QSizePolicy.Expanding:
#                pass
#            else:
            if not has_vertical_expanding_row:
                form_layout.setRowStretch( form_layout.rowCount(), 1 )

        form_widget = QtGui.QWidget( parent )

        # fix embedded forms
        if nomargins:
            form_layout.setContentsMargins( 0, 0, 0, 0 )

        form_widget.setSizePolicy( QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding )
        form_widget.setLayout( form_layout )

        if self._scrollbars:
            scroll_area = QtGui.QScrollArea( parent )
            scroll_area.setWidget( form_widget )
            scroll_area.setWidgetResizable( True )
            scroll_area.setFrameStyle( QtGui.QFrame.NoFrame )
            return scroll_area

        return form_widget


class Label( Form ):
    """Render a label with a QLabel"""

    def __init__( self, label, alignment='left', style=None):
        """
        :param label : string to be displayed in the label
        :param alignment : alignment of text in the label. values that make sense 'left', 'right' or 'center'
        :param style : string of cascading stylesheet instructions
        """
        super( Label, self ).__init__( [] )
        self.label = label
        self.alignment = alignment
        self.style = style

    def render_ooxml( self ):
        """Generator for label text in Office Open XML representing this form"""
        yield '<w:r>'
        yield '  <w:t>%s</w:t>' % self.label
        yield '</w:r>'


    @gui_function
    def render( self, widgets, parent = None, nomargins = False ):
        from PyQt4 import QtGui
        if self.style:
            widget = QtGui.QLabel( '<p align="%s" style="%s">%s</p>' % (self.alignment, self.style,unicode(self.label)) )
        else:
            widget = QtGui.QLabel( '<p align="%s">%s</p>' % (self.alignment,unicode(self.label)) )
        return widget

class TabForm( Form ):
    """
  Render forms within a QTabWidget::

    from = TabForm([('First tab', ['title', 'short_description']),
                    ('Second tab', ['director', 'release_date'])])

  .. image:: ../_static/form/tab_form.png
    """

    NORTH = 'North'
    SOUTH = 'South'
    WEST = 'West'
    EAST = 'East'

    def __init__( self, tabs, position=NORTH ):
        """
        :param tabs: a list of tuples of (tab_label, tab_form)
        :param position: the position of the tabs with respect to the pages
        """
        assert isinstance( tabs, list )
        assert position in [self.NORTH, self.SOUTH, self.WEST, self.EAST]
        self.position = position
        for tab in tabs:
            assert isinstance( tab, tuple )
        self.tabs = [( tab_label, structure_to_form( tab_form ) ) for tab_label, tab_form in tabs]
        super( TabForm, self ).__init__( sum( ( tab_form.get_fields()
                                      for tab_label, tab_form in self.tabs ), [] ) )

    def __unicode__( self ):
        return 'TabForm { %s\n        }' % ( u'\n  '.join( '%s : %s' % ( label, unicode( form ) ) for label, form in self.tabs ) )

    def add_tab_at_index( self, tab_label, tab_form, index ):
        """Add a tab to the form at the specified index

  :param tab_label: the name to the tab
  :param tab_form: the form to display in the tab or a list of field names.
  :param index: the position of tab in the tabs list.
        """
        tab_form = structure_to_form( tab_form )
        self.tabs.insert( index, ( tab_label, tab_form ) )
        self._content.extend( [tab_form] )

    def add_tab( self, tab_label, tab_form ):
        """Add a tab to the form

    :param tab_label: the name of the tab
    :param tab_form: the form to display in the tab or a list of field names.
        """
        tab_form = structure_to_form( tab_form )
        self.tabs.append( ( tab_label, tab_form ) )
        self._content.extend( [tab_form] )

    def get_tab( self, tab_label ):
        """Get the tab form of associated with a tab_label, use this function to
        modify the underlying tab_form in case of inheritance

    :param tab_label : a label of a tab as passed in the construction method
    :return: the tab_form corresponding to tab_label
        """
        for label, form in self.tabs:
            if label == tab_label:
                return form

    def replace_field( self, original_field, new_field ):
        super(TabForm, self).replace_field( original_field, new_field )
        for _label, form in self.tabs:
            if form.replace_field( original_field, new_field ):
                return True
        return False
    
    def remove_field( self, original_field ):
        super(TabForm, self).remove_field( original_field )
        for _label, form in self.tabs:
            if form.remove_field( original_field ):
                return True
        return False
    
    def _get_fields_from_form( self ):
        for _label, form in self.tabs:
            for field in form._get_fields_from_form():
                yield field

    @gui_function
    def render( self, widgets, parent = None, nomargins = False ):
        logger.debug( 'rendering %s' % self.__class__.__name__ )
        from PyQt4 import QtGui
        widget = QtGui.QTabWidget( parent )
        widget.setTabPosition(getattr(QtGui.QTabWidget, self.position))
        vertical_expanding = False
        for tab_label, tab_form in self.tabs:
            tab_form_widget = tab_form.render( widgets, widget )
            size_policy = tab_form_widget.sizePolicy()
            if size_policy.verticalPolicy()==QtGui.QSizePolicy.Expanding:
                vertical_expanding = True
            widget.addTab( tab_form_widget, unicode(tab_label) )
        if vertical_expanding:
            widget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        return widget


class HBoxForm( Form ):
    """
  Render different forms in a horizontal box::

    form = forms.HBoxForm([['title', 'short_description'], ['director', 'release_date']])

  .. image:: ../_static/form/hbox_form.png

  """

    def __init__( self, columns, scrollbars=False ):
        """:param columns: a list of forms to display in the different columns
        of the horizontal box"""
        assert isinstance( columns, list )
        self.columns = [structure_to_form( col ) for col in columns]
        super( HBoxForm, self ).__init__( sum( ( column_form.get_fields()
                                      for column_form in self.columns ), [] ), scrollbars=scrollbars )

    def __unicode__( self ):
        return 'HBoxForm [ %s\n         ]' % ( '         \n'.join( [unicode( form ) for form in self.columns] ) )

    def replace_field( self, original_field, new_field ):
        for form in self.columns:
            if form.replace_field( original_field, new_field ):
                return True
        return False

    def _get_fields_from_form( self ):
        for form in self.columns:
            for field in form._get_fields_from_form():
                yield field

    @gui_function
    def render( self, widgets, parent = None, nomargins = False ):
        logger.debug( 'rendering %s' % self.__class__.__name__ )
        from PyQt4 import QtGui
        widget = QtGui.QWidget( parent )
        form_layout = QtGui.QHBoxLayout()
        for form in self.columns:
            f = form.render( widgets, widget, nomargins )
            if isinstance( f, QtGui.QLayout ):
                form_layout.addLayout( f )
            else:
                form_layout.addWidget( f )
        widget.setLayout( form_layout )
        return widget

class VBoxForm( Form ):
    """
  Render different forms or widgets in a vertical box::

    form = forms.VBoxForm([['title', 'short_description'], ['director', 'release_date']])

  .. image:: ../_static/form/vbox_form.png
  """

    def __init__( self, rows ):
        """:param rows: a list of forms to display in the different columns
        of the horizontal box
        """
        assert isinstance( rows, list )
        self.rows = [structure_to_form( row ) for row in rows]
        super( VBoxForm, self ).__init__( sum( ( row_form.get_fields() for row_form in self.rows ), [] ) )

    def replace_field( self, original_field, new_field ):
        for form in self.rows:
            if form.replace_field( original_field, new_field ):
                return True
        return False

    def _get_fields_from_form( self ):
        for form in self.rows:
            for field in form._get_fields_from_form():
                yield field

    def __unicode__( self ):
        return 'VBoxForm [ %s\n         ]' % ( '         \n'.join( [unicode( form ) for form in self.rows] ) )

    @gui_function
    def render( self, widgets, parent = None, nomargins = False ):
        logger.debug( 'rendering %s' % self.__class__.__name__ )
        from PyQt4 import QtGui
        widget = QtGui.QWidget( parent )
        form_layout = QtGui.QVBoxLayout()
        for form in self.rows:
            f = form.render( widgets, widget, nomargins )
            if isinstance( f, QtGui.QLayout ):
                form_layout.addLayout( f )
            else:
                form_layout.addWidget( f )
        widget.setLayout( form_layout )
        return widget

class ColumnSpan( Form ):
    def __init__(self, field=None, num=2):
        self.num = num
        self.field = field
        super( ColumnSpan, self ).__init__( [field] )

class GridForm( Form ):
    """Put different fields into a grid, without a label.  Row or column labels can be added
  using the Label form::

    GridForm([['title', 'short_description'], ['director','release_date']])

  .. image:: ../_static/form/grid_form.png
  """

    def __init__( self, grid, nomargins = False ):
        """:param grid: A list for each row in the grid, containing a list with all fields that should be put in that row
        """
        assert isinstance( grid, list )
        self._grid = grid
        self._nomargins = nomargins
        fields = []
        for row in grid:
            assert isinstance( row, list )
            fields.extend( row )
        super( GridForm, self ).__init__( fields )

    def append_row(self, row):
        """:param row: the list of fields that should come in the additional row
        use this method to modify inherited grid forms"""
        assert isinstance( row, list )
        self._content.extend(row)
        self._grid.append(row)

    def append_column(self, column):
        """:param column: the list of fields that should come in the additional column
        use this method to modify inherited grid forms"""
        assert isinstance( column, list )
        self._content.extend(column)
        for row, additional_field in zip(self._grid, column):
            row.append(additional_field)

    @gui_function
    def render( self, widgets, parent = None, nomargins = False ):
        from PyQt4 import QtGui
        widget = QtGui.QWidget( parent )
        grid_layout = QtGui.QGridLayout()
        for i, row in enumerate( self._grid ):
            skip = 0
            for j, field in enumerate( row ):
                num = 1
                if isinstance( field, ColumnSpan ):
                    num = field.num
                    field = field.field

                if isinstance( field, Form ):
                    grid_layout.addWidget( field.render( widgets, parent ), i, j + skip, 1, num )
                    skip += num - 1
                else:
                    _label, editor = widgets[field]
                    grid_layout.addWidget( editor, i, j + skip, 1, num )
                    skip += num - 1

        widget.setLayout( grid_layout )
        if nomargins:
            grid_layout.setContentsMargins( 0, 0, 0, 0 )

        return widget

class WidgetOnlyForm( Form ):
    """Renders a single widget without its label, typically a one2many widget"""

    def __init__( self, field ):
        assert isinstance( field, ( str, unicode ) )
        super( WidgetOnlyForm, self ).__init__( [field] )

    @gui_function
    def render( self, widgets, parent = None, nomargins = False ):
        logger.debug( 'rendering %s' % self.__class__.__name__ )
        _label, editor = widgets[self.get_fields()[0]]
        return editor

class GroupBoxForm( Form ):
    """
  Renders a form within a QGroupBox::

    class Admin(EntityAdmin):
      form_display = GroupBoxForm('Movie', ['title', 'short_description'])

  .. image:: ../_static/form/group_box_form.png
  """

    def __init__( self, title, content, scrollbars=None, min_width=None, min_height=None, columns=1 ):
        self.title = title
        self.min_width = min_width
        self.min_height = min_height
        if isinstance(content, Form):
            content = [content]
        Form.__init__( self, content, scrollbars, columns=columns )

    @gui_function
    def render( self, widgets, parent = None, nomargins = False ):
        from PyQt4 import QtGui
        widget = QtGui.QGroupBox( unicode(self.title), parent )
        layout = QtGui.QVBoxLayout()
        if self.min_width and self.min_height:
            widget.setMinimumSize ( self.min_width, self.min_height )
        widget.setLayout( layout )
        form = Form.render( self, widgets, widget, nomargins )
        layout.addWidget( form )
        return widget

def structure_to_form( structure ):
    """Convert a python data structure to a form, using the following rules :

   * if structure is an instance of Form, return structure
   * if structure is a list, create a Form from this list

  This function is mainly used in the Admin class to construct forms out of
  the form_display attribute
    """
    if isinstance( structure, Form ):
        return structure
    return Form( structure )

