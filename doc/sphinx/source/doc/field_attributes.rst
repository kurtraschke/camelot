.. _doc-admin-field_attributes:

##################
  Field Attributes
##################

:Release: |version|
:Date: |today|

  .. image:: ../_static/field_attributes.png

Field attributes are the most convenient way to customize
an application, they can be specified through the
`field_attributes` dictionary of an `Admin` class :

.. literalinclude:: ../../../../example/model.py
   :pyobject: VisitorReport
   
Each combination of a delegate and an editor used to handle
a field supports a different set of field attributes.  To know
which field attribute is supported by which editor or delegate,
have a look at the :ref:`doc-delegates` documentation.

Static Field Attributes
=======================

Static field attributes should be the same for every row in
the same column, as such they should be specified as constant
in the field attributes dictionary.

Dynamic Field Attributes
========================

Some field attributes, like background_color, can be dynamic.
This means they can be specified as a function in the field
attributes dictionary.

This function should take as its single argument the object on
which the field attribute applies, as can be seen in the
:ref:`background color example <field-attribute-background_color>`

These are the field attributes that can be dynamic:

.. autodata:: camelot.admin.object_admin.DYNAMIC_FIELD_ATTRIBUTES
   
Overview of the field attributes
================================

.. _field-attribute-calculator:

calculator 
----------

:const:`True` or :const:`False` Indicates whether a calculator should be available when editing this field.

.. _field-attribute-editable:

editable 
--------

:const:`True` or :const:`False`
  
Indicates whether the user can edit the field.

.. _field-attribute-minimum:

minimum
-------

The minimum allowed value for :ctype:`Integer` and
:ctype:`Float` delegates or their related delegates like the Star delegate.

.. _field-attribute-maximum:

maximum
-------

The maximum allowed value for :ctype:`Integer` and
:ctype:`Float` delegates or their related delegates like the Star delegate.

.. _field-attribute-choices:

choices
-------

A function taking as a single argument the object to which the field
belongs.  The function returns a list of tuples containing for each
possible choice the value to be stored on the model and the value
displayed to the user.

The use of :attr:`choices` forces the use of the ComboBox delegate::

  field_attributes = {'state':{'choices':lambda o:[(1, 'Active'), 
                                                   (2, 'Passive')]}}
	   
.. _field-attribute-minmal_column_width:
                                              
minimal_column_width
--------------------

An integer specifying the minimal column width when this field is 
displayed in a table view.  The width is expressed as the number of 
characters that should fit in the column::

  field_attributes = {'name':{'minimal_column_width':50}}
  
will make the column wide enough to display at least 50 characters.

.. _field-attribute-prefix:

prefix
------

String to display before a number

.. _field-attribute-single_step:

single_step
-----------

The size of a single step when the up and down arrows are used in 
on a float or an integer field.
  
.. _field-attribute-suffix:

suffix
------

String to display after a number

.. _tooltips:

.. _field-attribute-tooltip:

tooltip
-------

A function taking as a single argument the object to which the field
belongs.  The function should return a string that will be used as a
tooltip.  The string may contain html markup.
  
.. literalinclude:: ../../../../test/snippet/fields_with_tooltips.py
  
.. image:: ../_static/snippets/fields_with_tooltips.png

.. _field-attribute-background_color:

background_color
----------------

A function taking as a single argument the object to which the field
belongs.  The function should return None if the default background should
be used, or a QColor to be used as the background.

.. literalinclude:: ../../../../test/snippet/background_color.py
  
.. image:: ../_static/snippets/background_color.png

.. _field-attribute-name:

name
----

The name of the field used, this defaults to the name of the attribute

.. _field-attribute-target:

target
------

In case of relation fields, specifies the class that is at the other
end of the relation.  Defaults to the one found by introspection.  This
can be used to let a many2one editor always point to a subclass of the
one found by introspection.

.. _field-attribute-admin:

admin
-----

In case of relation fields, specifies the admin class that is to be used
to visualize the other end of the relation.  Defaults to the default admin
class of the target class.  This can be used to make the table view 
within a one2many widget look different from the default table view for
the same object.

.. _field-attribute-embedded:

embedded
--------

Should be True or False, if True, the related object will be
displayed with its own form inside the form of the parent object.

.. _field-attribute-address_type:

address_type
------------

Should be None or one of the Virtual Address Types, like 'phone' or
'email'.  When specified, it indicates that a VirtualAddressEditor should
only accept addresses of the specified type.

Customizing multiple field attributes
=====================================

When multiple field attributes need to be customized, specifying the
`field_attributes` dictionary can become inefficient.

Several methods of the `Admin` class can be overwritten to take care of
this.

Instead of filling the `field_attributes` dictionary manually, the
`get_field_attributes` method can be overwritten :

.. automethod:: camelot.admin.object_admin.ObjectAdmin.get_field_attributes

When multiple dynamic field attributes need to execute the same logic
to determine their value, it can be more efficient to overwrite the
method `get_dynamic_field_attributes` and execute the logic once there
and set the value for all dynamic field attributes at once.

.. automethod:: camelot.admin.object_admin.ObjectAdmin.get_dynamic_field_attributes

The complement of `get_dynamic_field_attributes` is `get_static_field_attributes` :

.. automethod:: camelot.admin.object_admin.ObjectAdmin.get_static_field_attributes
