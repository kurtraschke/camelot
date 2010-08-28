'''
Created on Sep 9, 2009

@author: tw55413
'''
import logging
logger = logging.getLogger('camelot.view.model_thread.signal_slot_model_thread')

from PyQt4 import QtCore

from camelot.view.model_thread import AbstractModelThread, gui_function, setup_model
from camelot.core.threading import synchronized

class Task(QtCore.QObject):

    finished = QtCore.pyqtSignal(object)
    exception = QtCore.pyqtSignal(object)

    def __init__(self, request, name=''):
        QtCore.QObject.__init__(self)
        self._request = request
        self._name = name

    def clear(self):
        """clear this tasks references to other objects"""
        self._request = None
        self._name = None

    def execute(self):
        logger.debug('executing %s' % (self._name))
        try:
            result = self._request()
            self.finished.emit( result )
        except Exception, e:
            logger.error( 'exception caught in model thread while executing %s'%self._name, exc_info = e )
            import traceback, cStringIO
            sio = cStringIO.StringIO()
            traceback.print_exc(file=sio)
            traceback_print = sio.getvalue()
            sio.close()
            exception_info = (e, traceback_print)
            self.exception.emit( exception_info )
        except:
            logger.error( 'unhandled exception in model thread' )

class TaskHandler(QtCore.QObject):
    """A task handler is an object that handles tasks that appear in a queue,
    when its handle_task method is called, it will sequentially handle all tasks
    that are in the queue.
    """
    
    task_handler_busy_signal = QtCore.pyqtSignal(bool)

    def __init__(self, queue):
        """:param queue: the queue from which to pop a task when handle_task
        is called"""
        QtCore.QObject.__init__(self)
        self._mutex = QtCore.QMutex()
        self._queue = queue
        self._tasks_done = []
        self._busy = False
        logger.debug("TaskHandler created.")

    def busy(self):
        """:return True/False: indicating if this task handler is busy"""
        return self._busy
    
    @QtCore.pyqtSlot()
    def handle_task(self):
        """Handle all tasks that are in the queue"""
        self._busy = True
        self.task_handler_busy_signal.emit( True )
        task = self._queue.pop()
        while task:
            task.execute()
            # we keep track of the tasks done to prevent them being garbage collected
            # apparently when they are garbage collected, they are recycled, but their
            # signal slot connections seem to survive this recycling.
            # @todo: this should be investigated in more detail, since we are causing
            #        a deliberate memory leak here
            task.clear()
            self._tasks_done.append(task)
            task = self._queue.pop()
        self.task_handler_busy_signal.emit( False )
        self._busy = False

class SignalSlotModelThread( AbstractModelThread ):
    """A model thread implementation that uses signals and slots
    to communicate between the model thread and the gui thread
    
    there is no explicit model thread verification on these methods,
    since this model thread might not be THE model thread.
    """

    task_available = QtCore.pyqtSignal()

    def __init__( self, setup_thread = setup_model ):
        """
        @param setup_thread: function to be called at startup of the thread to initialize
        everything, by default this will setup the model.  set to None if nothing should
        be done.
        """
        super(SignalSlotModelThread, self).__init__( setup_thread )
        self._task_handler = None
        self._mutex = QtCore.QMutex()
        self._request_queue = []
        self._connected = False
        self._setup_busy = True

    def run( self ):
        self.logger.debug( 'model thread started' )
        self._task_handler = TaskHandler(self)
        self._task_handler.task_handler_busy_signal.connect(self._thread_busy, QtCore.Qt.QueuedConnection)
        self._thread_busy(True)
        try:
            self._setup_thread()
        except Exception, e:
            self.logger.error('thread setup incomplete', exc_info=e)
        self._thread_busy(False)
        self.logger.debug('thread setup finished')
        # Some tasks might have been posted before the signals were connected to the task handler,
        # so once force the handling of tasks
        self._task_handler.handle_task()
        self._setup_busy = False
        self.exec_()
        self.logger.debug('model thread stopped')

    @QtCore.pyqtSlot( bool )
    def _thread_busy(self, busy_state):
        self.thread_busy_signal.emit( busy_state )
                
    @synchronized
    def post( self, request, response = None, exception = None ):
        if not self._connected and self._task_handler:
            # creating this connection in the model thread throws QT exceptions
            self.task_available.connect( self._task_handler.handle_task, QtCore.Qt.QueuedConnection )
            self._connected = True
        # response should be a slot method of a QObject
        if response:
            name = '%s -> %s.%s'%(request.__name__, response.im_self.__class__.__name__, response.__name__)
        else:
            name = request.__name__
        task = Task(request, name=name)
        # QObject::connect is a thread safe function
        if response:
            assert response.im_self != None
            assert isinstance(response.im_self, QtCore.QObject)
            task.finished.connect( response, QtCore.Qt.QueuedConnection )
        if exception:
            task.exception.connect( exception, QtCore.Qt.QueuedConnection )
        task.moveToThread(self)
        # only put the task in the queue when it is completely set up 
        self._request_queue.append(task)
        #print 'task created --->', id(task)
        self.task_available.emit()

    @synchronized
    def pop( self ):
        """Pop a task from the queue, return None if the queue is empty"""
        if len(self._request_queue):
            task = self._request_queue.pop(0)
            return task

    @synchronized
    def busy( self ):
        """Return True or False indicating wether either the model or the
        gui thread is doing something"""
        while not self._task_handler:
            import time
            time.sleep(1)
        app = QtCore.QCoreApplication.instance()
        return app.hasPendingEvents() or len(self._request_queue) or self._task_handler.busy() or self._setup_busy

    @gui_function
    def wait_on_work(self):
        """Wait for all work to be finished, this function should only be used
        to do unit testing and such, since it will block the calling thread until
        all work is done"""
        app = QtCore.QCoreApplication.instance()
        while self.busy():
            app.processEvents()

#    app = QCoreApplication.instance()
#    waiting = True
#    while waiting:
#      waiting = False
#      if app.hasPendingEvents():
#        app.processEvents()
#        waiting = True
