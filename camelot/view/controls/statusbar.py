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

"""A custom status bar containing a progress indicator"""

import logging
logger = logging.getLogger('camelot.view.controls.statusbar')

from PyQt4 import QtGui
from camelot.view.model_thread import get_model_thread

class StatusBar(QtGui.QStatusBar):
  
    def __init__(self, parent):
        QtGui.QStatusBar.__init__(self, parent)
        from camelot.view.controls.busy_widget import BusyWidget
        self.busy_widget = BusyWidget(self)
        self.busy_widget.setMinimumWidth(100)
        self.addPermanentWidget(self.busy_widget, 0)
        mt = get_model_thread()
        mt.thread_busy_signal.connect( self.busy_widget.set_busy )
        # the model thread might allready be busy before we connected to it
        self.busy_widget.set_busy(mt.busy())

