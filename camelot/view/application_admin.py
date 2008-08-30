#  ==================================================================================
#
#  Copyright (C) 2007-2008 Conceptive Engineering bvba. All rights reserved.
#  www.conceptive.be / project-camelot@conceptive.be
#
#  This file is part of the Camelot Library.
#
#  This file may be used under the terms of the GNU General Public
#  License version 2.0 as published by the Free Software Foundation
#  and appearing in the file LICENSE.GPL included in the packaging of
#  this file.  Please review the following information to ensure GNU
#  General Public Licensing requirements will be met:
#  http://www.trolltech.com/products/qt/opensource.html
#
#  If you are unsure which license is appropriate for your use, please
#  review the following information:
#  http://www.trolltech.com/products/qt/licensing.html or contact
#  project-camelot@conceptive.be.
#
#  This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
#  WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#
#  For use of this library in commercial applications, please contact
#  project-camelot@conceptive.be
#
#  ==================================================================================

"""
Admin class, specify how the main window should look like
"""

class ApplicationAdmin(object):
  
  sections = []
  
  def __init__(self, main_sections):
    """The main sections to be used in the navigation pane of the application,
    all entities will be put in such a section, depending on the properties of
    their EntityAdmin class, a list of tuples of strings and icons
    [('section', ('Section display name',section_icon))]
    """
    if main_sections:
      self.sections = main_sections
      
  def getSections(self):
    return self.sections
  
  def getEntityAdmin(self, entity):
    """Get the default entity admin for this entity, return None, if not
    existant"""
    if hasattr(entity, 'Admin'):
      return entity.Admin(self, entity)
  
  def getEntityQuery(self, entity):
    """Get the root query for an entity"""
    return entity.query
  
  def getEntitiesAndQueriesInSection(self, section):
    """
    @return: a list of tuples of (admin,query) instances related to
    the entities in this section.
    """
    from elixir import entities
    return [(self.getEntityAdmin(e),self.getEntityQuery(e)) for e in entities \
                                                            if hasattr(e, 'Admin') \
                                                            and hasattr(e.Admin, 'section') \
                                                            and e.Admin.section == section]