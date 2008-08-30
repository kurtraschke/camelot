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

"""Action buttons"""
import logging

logger = logging.getLogger('controls.actions')
logger.setLevel(logging.DEBUG)

from PyQt4 import QtCore, QtGui

_ = lambda x:x

from camelot.view.remote_signals import get_signal_handler

class ActionsBox(QtGui.QGroupBox):
  """A box containing actions to be applied to a form view"""

  def __init__(self, parent, model_thread):
    logger.debug('create actions box')
    QtGui.QGroupBox.__init__(self, _('Actions'), parent)
    self.group = QtGui.QButtonGroup()
    self.mt = model_thread
    self.rsh = get_signal_handler()
    self.connect(self.group, QtCore.SIGNAL('buttonPressed(int)'), self.executeAction)

  def setActions(self, actions):
    logger.debug('setting actions')
    self.actions = []
    layout = QtGui.QVBoxLayout()
    for i,(name,functor) in enumerate(actions):
      button = QtGui.QPushButton(_(name))
      layout.addWidget(button)
      self.group.addButton(button, i)
      self.actions.append((name, functor))
    layout.addStretch()
    self.setLayout(layout)
    
  def setEntity(self, entity):
    self.entity = entity
    
  def executeAction(self, button_id):
    
    def execute_and_flush():
      from elixir import session
      self.actions[button_id][1](self.entity)
      session.flush([self.entity])
      
    def executed(result):
      logger.debug('action %i executed'%button_id)
      self.rsh.on_message(None, None)
      
    self.mt.post(execute_and_flush, executed )
 
  def __del__(self):
    logger.debug('delete actions box')

