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

"""Actions box"""

import logging
logger = logging.getLogger('controls.actionsbox')

from PyQt4 import QtGui

from camelot.core.utils import ugettext as _

class ActionsBox(QtGui.QGroupBox):
    """A box containing actions to be applied to a view"""

    def __init__(self, parent, *args, **kwargs):
        QtGui.QGroupBox.__init__(self, _('Actions'), parent)
        logger.debug('create actions box')
        self.args = args
        self.kwargs = kwargs

    def setActions(self, actions):
        action_widgets = []
        logger.debug('setting actions')
        # keep action object alive to allow them to receive signals
        self.actions = actions
        layout = QtGui.QVBoxLayout()
        for action in actions:
            action_widget = action.render(self, *self.args)
            layout.addWidget(action_widget)
            action_widgets.append(action_widget)
        self.setLayout(layout)
        return action_widgets

