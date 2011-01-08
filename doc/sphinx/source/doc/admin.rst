.. _doc-admin:

###############################
  Customizing the Admin classes
###############################

:Release: |version|
:Date: |today|

The Admin classes are the classes that specify how objects should be visualized,
they define the look, feel and behaviour of the Application.  Most of the behaviour
of the Admin classes can be tuned by changing their class attributes.  This makes
it easy to subclass a default Admin class and tune it to your needs.

  .. image:: ../_static/admin_classes.png
  
Camelot is able to visualize any python class, through the use of an ObjectAdmin
class.  However, subtypes exist that use introspection to facilitate the visualisation.

The EntityAdmin class is a subclass of ObjectAdmin that can be used to visualize
class mapped to a database using SQLAlchemy.

Each class that is visualized within Camelot has an associated Admin
class which specifies how the object or a list of objects should be visualized.

Usually the Admin class is bound to the model class by defining it as an
inner class of the model class::

  class Movie(Entity):
    title = Field(Unicode(60), required=True)

    class Admin(EntityAdmin):
      verbose_name = _('Movies')
      list_display = ['title']

Most of the behaviour of the Admin class can be customized by changing
the class attributes like verbose_name or list_display.

.. toctree::

   object_admin.rst
   entity_admin.rst
   field_attributes.rst
   validators.rst
   application_admin.rst