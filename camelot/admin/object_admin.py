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

"""Admin class for Plain Old Python Object"""

import logging
logger = logging.getLogger('camelot.view.object_admin')

from camelot.view.model_thread import gui_function, model_function
from camelot.view.controls.tableview import TableView
from camelot.core.utils import ugettext as _
from camelot.core.utils import ugettext_lazy
from camelot.view.proxy.collection_proxy import CollectionProxy
from validator.object_validator import ObjectValidator
from PyQt4 import QtCore

class FieldAttributesList(list):
    """A list with field attributes that documents them for
    sphinx"""

    def __init__(self, original_list):
        """:param original_list: the list with field attributes
        to document"""
        super(FieldAttributesList, self).__init__(original_list)
        template = "\n * :ref:`%s <field-attribute-%s>`"
        doc = '\n'.join([template%(name, name) for name in original_list])
        self.__doc__ = doc

DYNAMIC_FIELD_ATTRIBUTES = FieldAttributesList(['tooltip', 'color', 'background_color',
                                                'editable', 'choices',
                                                'prefix', 'suffix', 'arrow',
                                                'new_message', 'default'])


class ObjectAdmin(object):
    """The ObjectAdmin class describes the interface that will be used
to interact with objects of a certain class.  The behaviour of this class
and the resulting interface can be tuned by specifying specific class
attributes:

**The name used in the GUI**

The name used in the GUI for things like window titles and such can
be specified using the verbose_name attribute.

.. attribute:: verbose_name

A human-readable name for the object, singular ::

verbose_name = _('movie')

If this isn't given, the class name will be used

.. attribute:: verbose_name_plural

A human-readable name for the object, plural ::

verbose_name_plural = _('movies')

If this isn't given, Camelot will use verbose_name + "s"

**Fields displayed**

.. attribute:: list_display

a list with the fields that should be displayed in a table view

.. attribute:: list_columns_frozen

the number of columns on the left of the tableview that should be frozen
(don't dissapear when the user uses the horizontal scroll bar), defaults
to zero

.. attribute:: lines_per_row

An integer number specifying the height of a row in the table view, expressed
as the number of lines of text it should be able to display.  Defaults to 1.

.. attribute:: form_display

a list with the fields that should be displayed in a form view, defaults to
the same fields as those specified in list_display ::

class Admin(EntityAdmin):
  form_display = ['title', 'rating', 'cover']

instead of telling which forms to display. It is also possible to define
the form itself ::

    from camelot.view.forms import Form, TabForm, WidgetOnlyForm, HBoxForm

    class Admin(EntityAdmin):
      form_display = TabForm([
        ('Movie', Form([
          HBoxForm([['title', 'rating'], WidgetOnlyForm('cover')]),
          'short_description',
          'releasedate',
          'director',
          'script',
          'genre',
          'description', 'tags'], scrollbars=True)),
        ('Cast', WidgetOnlyForm('cast'))
      ])

**Behaviour**

.. attribute:: confirm_delete

Indicates if the deletion of an object should be confirmed by the user, defaults
to False.  Can be set to either True, False, or the message to display when asking
confirmation of the deletion.

.. attribute:: form_size

a tuple indicating the size of a form view, defaults to (700,500)

.. attribute:: form_actions

Actions to be accessible by pushbuttons on the side of a form,
a list of tuples (button_label, action_function) where action_function
takes as its single argument, a method that returns the the object that
was displayed by the form when the button was pressed::

class Admin(EntityAdmin):
  form_actions = [('Foo', lamda o_getter:print 'foo')]

**Field attributes**

.. attribute:: field_attributes

A dictionary specifying for each field of the model some additional
attributes on how they should be displayed.  All of these attributes
are propagated to the constructor of the delegate of this field::

class Movie(Entity):
  title = Field(Unicode(50))

  class Admin(EntityAdmin):
    list_display = ['title']
    field_attributes = dict(title=dict(editable=False))

The :ref:`doc-admin-field_attributes` documentation describes the various keys
that can be used in the field attributes class attribute of an ObjectAdmin or EntityAdmin.

**Window state**

.. attribute:: form_state

Set this attribute to 'maximized' or 'minimized' for respective behaviour. These are the only two defined at the moment.
Please use the constants defined in camelot.core.constants (MINIMIZE and MAXIMIZE).
Note that this attr needs to be set at the form, highest in the form hierarchy to work. Setting this on embedded forms
will not influence the window state. Example::

class Movie(Entity):
  title = Field(Unicode(50))

  class Admin(EntityAdmin):
    from camelot.core import constants
    list_display = ['title']
    form_state = constants.MAXIMIZED
    field_attributes = dict(title=dict(editable=False))

**Varia**

.. attribute:: model
The QAbstractItemModel class to be used to display collections of this object,
defaults to a CollectionProxy

.. attribute:: TableView
The QWidget class to be used when a table view is needed
    """
    name = None #DEPRECATED
    verbose_name = None
    verbose_name_plural = None
    list_display = []
    list_columns_frozen = 0
    lines_per_row = 1
    validator = ObjectValidator
    model = CollectionProxy
    fields = []
    form = [] #DEPRECATED
    form_display = []
    list_filter = []
    list_charts = []
    list_actions = []
    confirm_delete = False
    list_size = (600, 400)
    form_size = (700, 500)
    form_actions = []
    form_title_column = None #DEPRECATED
    field_attributes = {}
    form_state = None
    TableView = TableView

    def __init__(self, app_admin, entity):
        """

        :param app_admin: the application admin object for this application, if None,
        then the default application_admin is taken
        :param entity: the entity class for which this admin instance is to be
        used
        """
        from camelot.view.remote_signals import get_signal_handler
        if not app_admin:
            from camelot.admin.application_admin import get_application_admin
            self.app_admin = get_application_admin()
        else:
            self.app_admin = app_admin
        self.rsh = get_signal_handler()
        if entity:
            from camelot.view.model_thread import get_model_thread
            self.entity = entity
            self.mt = get_model_thread()
        #
        # caches to prevent recalculation of things
        #
        self._field_attributes = dict()
        self._subclasses = None

    def __str__(self):
        return 'Admin %s' % str(self.entity.__name__)

    def __repr__(self):
        return 'ObjectAdmin(%s)' % str(self.entity.__name__)

    def get_name(self):
        return self.get_verbose_name()

    def get_verbose_name(self):
        
#        def uncamelize(text):
#            def downcase(matchobj):
#                return "_" + matchobj.group(0).lower()
#            if text:
#                text = text[0].lower() + re.sub(r'([A-Z])', downcase, text[1:])
#            return text 

        return unicode(
            self.verbose_name or self.name or _(self.entity.__name__.capitalize())
        )

    def get_verbose_name_plural(self):
        return unicode(
            self.verbose_name_plural
            or self.name
            or (self.get_verbose_name() + 's')
        )

    @model_function
    def get_verbose_identifier(self, obj):
        """Create an identifier for an object that is interpretable
        for the user, eg : the primary key of an object.  This verbose identifier can
        be used to generate a title for a form view of an object.
        """
        return u'%s : %s' % (self.get_verbose_name(), unicode(obj))

    def get_entity_admin(self, entity):
        return self.app_admin.get_entity_admin(entity)

    def get_confirm_delete(self):
        if self.confirm_delete:
            if self.confirm_delete==True:
                return _('Are you sure you want to delete this')
            return self.confirm_delete
        return False

    @model_function
    def get_form_actions(self, entity):
        from camelot.admin.form_action import structure_to_form_actions
        return structure_to_form_actions(self.form_actions)

    @model_function
    def get_list_actions(self):
        from camelot.admin.list_action import structure_to_list_actions
        return structure_to_list_actions(self.list_actions)

    @model_function
    def get_depending_objects(self, obj):
        """Overwrite this function to generate a list of objects that depend on a given
        object.  When obj is modified by the user, this function will be called to determine
        which other objects need their views updated.

        :param obj: an object of the type that is managed by this admin class
        :return: an iterator over objects that depend on obj
        """
        return []

    @model_function
    def get_subclass_tree( self ):
        """Get a tree of admin classes representing the subclasses of the class
        represented by this admin class

        :return: [(subclass_admin, [(subsubclass_admin, [...]),...]),...]
        """
        subclasses = []
        for subclass in self.entity.__subclasses__():
            subclass_admin = self.get_related_entity_admin(subclass)
            if subclass_admin!=self:
                subclasses.append((
                    subclass_admin,
                    subclass_admin.get_subclass_tree()
                ))

        def sort_admins(a1, a2):
            return cmp(a1[0].get_verbose_name_plural(), a2[0].get_verbose_name_plural())

        subclasses.sort(cmp=sort_admins)
        return subclasses

    def get_related_entity_admin(self, entity):
        """Get an admin object for another entity.  Taking into account
        preferences of this admin object or for those of admin object higher up
        the chain such as the application admin object.

        :param entity: the entity class for which an admin object is requested
        """
        if entity == self.entity:
            return self
        related_admin = self.app_admin.get_entity_admin(entity)
        if not related_admin:
            logger.warn('no related admin found for %s' % (entity.__name__))
        return related_admin

    def get_static_field_attributes(self, field_names):
        """
        Convenience function to get all the field attributes
        that are static (don't depend on the object being visualized).  This
        method is only called once for a table or form view, independent of
        the number of objects/records being visualized.

        :param field_names: a list of field names
        :return: [{field_attribute_name:field_attribute_value, ...}, {}, ...]

        The returned list has the same order than the requested
        field_names.
        """
        for field_name in field_names:
            field_attributes = self.get_field_attributes(field_name)
            static_field_attributes = {}
            for name, value in field_attributes.items():
                if name not in DYNAMIC_FIELD_ATTRIBUTES or not callable(value):
                    static_field_attributes[name] = value
            yield static_field_attributes

    def get_dynamic_field_attributes(self, obj, field_names):
        """
        Convenience function to get all the field attributes
        that are dynamic (depend on the object being visualized). This method
        is called once for each object/row in a table view and once for
        each object being visualized in a form view.

        :param field_names: a list of field names
        :param obj: the object at the row for which to get the values of the dynamic field attributes
        :return: [{field_attribute_name:field_attribute_value, ...}, {}, ...]

        The returned list has the same order than the requested
        field_names.
        """
        for field_name in field_names:
            field_attributes = self.get_field_attributes(field_name)
            dynamic_field_attributes = {}
            for name, value in field_attributes.items():
                if name not in DYNAMIC_FIELD_ATTRIBUTES:
                    continue
                if callable(value):
                    return_value = None
                    try:
                        return_value = value(obj)
                    except (ValueError, Exception, RuntimeError, TypeError, NameError), exc:
                        logger.error(u'error in field_attribute function of %s'%name, exc_info=exc)
                    finally:
                        dynamic_field_attributes[name] = return_value
            yield dynamic_field_attributes

    def get_field_attributes(self, field_name):
        """
        Get the attributes needed to visualize the field field_name.  This
        function is called by get_static_field_attributes and
        get_dynamic_field_attributes.

        This function first tries to fill the dictionary with field
        attributes for a field with those gathered through introspection,
        and then updates them with those found in the field_attributes
        class attribute.

        :param field_name: the name of the field
        :return: a dictionary of attributes needed to visualize the field

        The values of the returned dictionary either contain the value
        of the field attribute, or in the case of dynamic field attributes,
        a function that returns the value of the field attribute.
        """
        try:
            return self._field_attributes[field_name]
        except KeyError:

            def create_default_getter(field_name):
                return lambda o:getattr(o, field_name)

            from camelot.view.controls import delegates
            #
            # Default attributes for all fields
            #
            attributes = dict(
                getter=create_default_getter(field_name),
                field_name=field_name,
                python_type=str,
                length=None,
                tooltip=None,
                background_color=None,
                minimal_column_width=12,
                editable=False,
                nullable=True,
                widget='str',
                blank=True,
                delegate=delegates.PlainTextDelegate,
                validator_list=[],
                name=ugettext_lazy(field_name.replace( '_', ' ' ).capitalize())
            )
            #
            # Field attributes forced by the field_attributes property
            #
            forced_attributes = {}
            try:
                forced_attributes = self.field_attributes[field_name]
            except KeyError:
                pass

            #
            # TODO : move part of logic from entity admin class over here
            #

            #
            # Overrule introspected field_attributes with those defined
            #
            attributes.update(forced_attributes)

            #
            # In case of a 'target' field attribute, instantiate an appropriate
            # 'admin' attribute
            #

            def get_entity_admin(target):
                """Helper function that instantiated an Admin object for a
                target entity class

                :param target: an entity class for which an Admin object is
                needed
                """
                try:
                    fa = self.field_attributes[field_name]
                    target = fa.get('target', target)
                    admin_class = fa['admin']
                    return admin_class(self.app_admin, target)
                except KeyError:
                    return self.get_related_entity_admin(target)

            if 'target' in attributes:
                attributes['admin'] = get_entity_admin(attributes['target'])

            self._field_attributes[field_name] = attributes
            return attributes

    @model_function
    def get_columns(self):
        """
        The columns to be displayed in the list view, returns a list of pairs
        of the name of the field and its attributes needed to display it
        properly

        @return: [(field_name,
                  {'widget': widget_type,
                   'editable': True or False,
                   'blank': True or False,
                   'validator_list':[...],
                   'name':'Field name'}),
                 ...]
        """
        return [(field, self.get_field_attributes(field))
                for field in self.list_display]

    def create_validator(self, model):
        return self.validator(self, model)

    @model_function
    def get_fields(self):
        if self.form or self.form_display:
            fields = self.get_form_display().get_fields()
        elif self.fields:
            fields = self.fields
        else:
            fields = self.list_display
        fields_and_attributes =  [
                (field, self.get_field_attributes(field))
                for field in fields
        ]
        return fields_and_attributes

    @model_function
    def get_all_fields_and_attributes(self):
        """A dictionary of (field_name:field_attributes) for all fields that can
        possibly appear in a list or a form or for which field attributes have
        been defined
        """
        fields = dict(self.get_columns())
        fields.update(dict(self.get_fields()))
        return fields

    @model_function
    def get_form_display(self):
        from camelot.view.forms import Form, structure_to_form
        if self.form or self.form_display:
            return structure_to_form(self.form or self.form_display)
        if self.list_display:
            return Form(self.list_display)
        return Form([])

    @gui_function
    def create_form_view(self, title, model, index, parent=None):
        """Creates a Qt widget containing a form view, for a specific index in
        a model.  Use this method to create a form view for a collection of objects,
        the user will be able to use PgUp/PgDown to move to the next object.

        :param title: the title of the form view
        :param model: the data model to be used to fill the form view
        :param index: which row in the data model to display
        :param parent: the parent widget for the form
        """
        logger.debug('creating form view for index %s' % index)
        from camelot.view.controls.formview import FormView
        form = FormView(title, self, model, index)

        if hasattr(self, 'form_state'):
            from camelot.core import constants
            if self.form_state == constants.MAXIMIZED:
                form.setWindowState(QtCore.Qt.WindowMaximized)
            if self.form_state == constants.MINIMIZED:
                form.setWindowState(QtCore.Qt.WindowMinimized)

        return form

    # simply copied from EntityAdmin
    def set_defaults(self, object_instance, include_nullable_fields=True):
        """Set the defaults of an object
        :param include_nullable_fields: also set defaults for nullable fields, depending
        on the context, this should be set to False to allow the user to set the field
        to None
        """
        from sqlalchemy.schema import ColumnDefault
        for field, attributes in self.get_fields():
            has_default = False
            try:
                default = attributes['default']
                has_default = True
            except KeyError:
                pass
            if has_default:
                #
                # prevent the setting of a default value when one has been
                # set allready
                #
                value = attributes['getter'](object_instance)
                if value!=None: # False is a legitimate value for Booleans
                    continue
                if isinstance(default, ColumnDefault):
                    default_value = default.execute()
                elif callable(default):
                    import inspect
                    args, _varargs, _kwargs, _defs = \
                        inspect.getargspec(default)
                    if len(args):
                        default_value = default(object_instance)
                    else:
                        default_value = default()
                else:
                    default_value = default
                logger.debug(
                    'set default for %s to %s' % (
                        field,
                        unicode(default_value)
                    )
                )
                try:
                    setattr(object_instance, field, default_value)
                except AttributeError, exc:
                    logger.error(
                        'Programming Error : could not set'
                        ' attribute %s to %s on %s' % (
                            field,
                            default_value,
                            object_instance.__class__.__name__
                        ),
                        exc_info=exc
                    )

    @gui_function
    def create_object_form_view(self, title, object_getter, parent=None):
        """Create a form view for a single object, PgUp/PgDown will do
        nothing.

        :param title: the title of the form view
        :param object_getter: a function taking no arguments, and returning the object
        :param parent: the parent widget for the form
        """

        def create_collection_getter( object_getter, object_cache ):
            """Transform an object_getter into a collection_getter which
            returns a collection with only the object returned by object
            getter.

            :param object_getter: a function that returns the object that should be in
            the collection
            :param object_cache: a list that will be used to store the result
            of object_getter, to prevent multiple calls of object_getter
            """

            def collection_getter():
                if not object_cache:
                    object_cache.append( object_getter() )
                return object_cache

            return collection_getter

        model = self.model( self,
                            create_collection_getter( object_getter, [] ),
                            self.get_fields )
        return self.create_form_view(title, model, 0, parent)

    @gui_function
    def create_new_view(admin, parent=None, oncreate=None, onexpunge=None):
        """Create a Qt widget containing a form to create a new instance of the
        entity related to this admin class

        The returned class has an 'entity_created_signal' that will be fired
        when a valid new entity was created by the form
        """
        from PyQt4 import QtGui, QtCore
        from camelot.view.controls.view import AbstractView
        from camelot.view.model_thread import post
        new_object = []

        @model_function
        def collection_getter():
            if not new_object:
                entity_instance = admin.entity()
                if oncreate:
                    oncreate(entity_instance)
                # Give the default fields their value
                admin.set_defaults(entity_instance)
                new_object.append(entity_instance)
            return new_object

        model = CollectionProxy(
            admin,
            collection_getter,
            admin.get_fields,
            max_number_of_rows=1
        )
        post(model.updateUnflushedRows)
        validator = admin.create_validator(model)

        class NewForm(AbstractView):

            entity_created_signal = QtCore.pyqtSignal(object)

            def __init__(self, parent):
                AbstractView.__init__(self, parent)
                self.widget_layout = QtGui.QVBoxLayout()
                self.widget_layout.setMargin(0)
                title = _('New')
                index = 0
                self.form_view = admin.create_form_view(
                    title, model, index, parent
                )
                self.widget_layout.insertWidget(0, self.form_view)
                self.setLayout(self.widget_layout)
                self.validate_before_close = True
                #
                # every time data has been changed, it could become valid,
                # when this is the case, it should be propagated
                #
                model.dataChanged.connect( self.dataChanged )
                self.form_view.title_changed_signal.connect( self.change_title )

            def emit_if_valid(self, valid):
                if valid:

                    def create_instance_getter(new_object):
                        return lambda:new_object[0]

                    self.entity_created_signal.emit(
                        create_instance_getter(new_object)
                    )

            @QtCore.pyqtSlot( QtCore.QModelIndex, QtCore.QModelIndex )
            def dataChanged(self, index1, index2):

                def validate():
                    return validator.isValid(0)

                post(validate, self.emit_if_valid)

            def showMessage(self, valid):
                self.emit_if_valid(valid)
                form = self.form_view.findChild(QtGui.QWidget, 'form' )
                if not valid and form:
                    row = 0
                    reply = validator.validityDialog(row, self).exec_()
                    if reply == QtGui.QMessageBox.Discard:
                        # clear mapping to prevent data being written again to
                        # the model, after we reverted the row
                        form.clear_mapping()

                        def onexpunge_on_all():
                            if onexpunge:
                                onexpunge( new_object )

                        post(onexpunge_on_all)
                        self.validate_before_close = False
                        self.close()
                else:
                    def create_instance_getter(new_object):
                        return lambda:new_object[0]

                    for _o in new_object:
                        self.entity_created_signal.emit( create_instance_getter(new_object) )
                    self.validate_before_close = False
                    self.close()

            def validateClose(self):
                logger.debug(
                    'validate before close : %s' %
                    self.validate_before_close
                )
                form = self.form_view.findChild(QtGui.QWidget, 'form' )
                if self.validate_before_close:
                    form.submit()
                    logger.debug(
                        'unflushed rows : %s' %
                        str(model.hasUnflushedRows())
                    )
                    if model.hasUnflushedRows():

                        def validate_and_flush():
                            valid = validator.isValid(0)
                            if valid:
                                admin.flush(new_object[0])
                            return valid

                        post(validate_and_flush, self.showMessage)
                        return False
                    else:
                        return True
                return True

            def closeEvent(self, event):
                if self.validateClose():
                    event.accept()
                else:
                    event.ignore()

        form = NewForm(parent)
        if hasattr(admin, 'form_size'):
            form.setMinimumSize(admin.form_size[0], admin.form_size[1])
        return form

    @model_function
    def delete(self, entity_instance):
        """Delete an entity instance"""
        del entity_instance

    @model_function
    def flush(self, entity_instance):
        """Flush the pending changes of this entity instance to the backend"""
        pass

    @model_function
    def refresh(self, entity_instance):
        """Undu the pending changes to the backend and restore the original
        state"""
        pass

    @model_function
    def add(self, entity_instance):
        """Add an entity instance as a managed entity instance"""
        pass

    @model_function
    def copy(self, entity_instance):
        """Duplicate this entity instance"""
        new_entity_instance = entity_instance.__class__()
        return new_entity_instance
