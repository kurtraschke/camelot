.. _doc-forms:

###############
 Creating Forms
###############

:Release: |version|
:Date: |today|

This section describes how to place fields on forms and applying
various layouts.  It also covers how to customize forms to your
specific needs.  As with everything in Camelot, the goal of the framework
is that you can create 80% of your forms with minimal effort, while
the framework should allow you to really customize the other 20% of
your forms.

Form
====

A form is a collection of fields organized within a layout.  Each
field is represented by its editor.

Usually forms are defined by specifying the 'form_display' attribute of an
Admin class :

.. literalinclude:: ../../../../test/snippet/form/simple_form.py

.. image:: ../_static/form/form.png

The 'form_display' attribute should either be a list of fields to display
or an instance of camelot.view.forms.Form or its subclasses.

Forms can be nested into each other :

.. literalinclude:: ../../../../test/snippet/form/nested_form.py

.. image:: ../_static/form/nested_form.png

Inheritance and Forms
=====================

Just as Entities support inheritance, forms support inheritance as well.  This
avoids duplication of effort when designing and maintaining forms.  Each of the
Form subclasses has a set of methods to modify its content.  In the example below
a new tab is added to the form defined in the previous section.

.. literalinclude:: ../../../../test/snippet/form/inherited_form.py

.. image:: ../_static/form/inherited_form.png

Putting notes on forms
======================

.. image:: ../_static/editors/NoteEditor.png 

A note on a form is nothing more than a property with the NoteDelegate as its
delegate and where the widget is inside a WidgetOnlyForm.

In the case of a Person, we display a note if another person with the same name
allready exists :

.. literalinclude:: ../../../../camelot/model/authentication.py
   :pyobject: Person

Available Form Subclasses
=========================

camelot.view.forms.Form has several subclasses that can be used to create
various layouts.  Each subclass maps to a QT Layout class.

.. automodule:: camelot.view.forms
   :members:
   
Customizing Forms
=================

Several options exist for completely customizing the forms of an application.

Layout
------

When the desired layout cannot be achieved with Camelot's form classes, a custom
Form subclass can be made to lay out the widgets.

When subclassing the Form class, it's 'render' method should be reimplemented to
put the labels and the editors in a custom layout.  The 'render' method will be
called by Camelot each time it needs a form for the related entity.  It should thus
return a QWidget to be used as the needed form. 

The 'render' method its most important argument is widgets which is a dictionary
containing for each field of the form a widget representing the label of the field
and a widget for editing the field.  The editor widgets are bound to the
model.

.. literalinclude:: ../../../../test/snippet/form/custom_layout.py

The form defined above puts the widgets into a QFormLayout using a different
background color, and adds some instructions for the user :

.. image:: ../_static/form/custom_layout.png

Editors
-------

The editor of a specific field can be changed, by specifying an alternative delegate
for that field, using the field attributes, see :ref:`specifying-delegates`.

Tooltips
--------

Each field on the form can be given a dynamic tooltip, using the 'tooltip' field
attribute : :ref:`tooltips`.

Buttons
-------

Buttons bound to a specific action can be put on a form, using the 'form_actions' 
attribute of the Admin class : :ref:`form-actions`.

Validation
----------

Validation is done at the object level.  Before a form is closed validation of the
bound object takes place, an invalid object will prevent closing the form.  A custom
validator can be defined : :ref:`validators`

Behaviour
---------

To change what happens when Camelot requires a form for an object, some methods
on the Admin class can be overwritten :

  * create_form_view
  * create_new_view