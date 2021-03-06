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
'''
Created on Sep 12, 2009

@author: tw55413
'''

import logging
logger = logging.getLogger('camelot.view.model_thread.no_thread_model_thread')

from PyQt4 import QtCore
from signal_slot_model_thread import AbstractModelThread, setup_model
from camelot.view.controls.exception import register_exception

class NoThreadModelThread( AbstractModelThread ):

    def __init__(self, setup_thread = setup_model ):
        super(NoThreadModelThread, self).__init__( setup_thread = setup_model )
        self.responses = []
        self.start()

    def start(self):
        try:
            self._setup_thread()
        except Exception, e:
            name, trace = register_exception(logger, 'Exception when setting up the NoThreadModelThread', e)
            self.setup_exception_signal.emit(name, trace)

    def post( self, request, response = None, exception = None ):
        try:
            result = request()
            response( result )
        except Exception, e:
            if exception:
                logger.error( 'exception caught in model thread while executing %s'%self._name, exc_info = e )
                import traceback, cStringIO
                sio = cStringIO.StringIO()
                traceback.print_exc(file=sio)
                traceback_print = sio.getvalue()
                sio.close()
                exception_info = (e, traceback_print)
                exception(exception_info)

    def wait_on_work(self):
        app = QtCore.QCoreApplication.instance()
        i = 0
        # only process events 10 times to avoid dead locks
        while app.hasPendingEvents() and i < 10:
            app.processEvents()
            i += 1
            
    def isRunning(self):
        return True

