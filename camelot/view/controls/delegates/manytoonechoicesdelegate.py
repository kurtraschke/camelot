
from customdelegate import *

class ManyToOneChoicesDelegate( CustomDelegate ):
    """Display a ManyToOne field as a ComboBox, filling the list of choices with
  the objects of the target class. 
  
  .. image:: ../_static/enumeration.png   
  """
  
    editor = editors.OneToManyChoicesEditor
