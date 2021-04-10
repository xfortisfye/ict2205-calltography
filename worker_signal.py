from PyQt5 import QtCore

class MsgWorkerSignals(QtCore.QObject):
    message_received = QtCore.pyqtSignal(str)

class ServerAuthWorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)

class InitReqWorkerSignals(QtCore.QObject):
    start_timer = QtCore.pyqtSignal()
    call_accepted = QtCore.pyqtSignal(str, str)
    reject = QtCore.pyqtSignal()
    timeout = QtCore.pyqtSignal()

class ListenReqWorkerSignals(QtCore.QObject):
    caller = QtCore.pyqtSignal(str)
    init_recv_call = QtCore.pyqtSignal()
    reject = QtCore.pyqtSignal()
    timeout = QtCore.pyqtSignal()

class SendAckWorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal()
    call_accepted = QtCore.pyqtSignal(str, str)