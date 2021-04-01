from PyQt5 import uic, QtWidgets, QtGui, QtCore
from config import ABSOLUTE_PATH


class KeyDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(KeyDialog, self).__init__()
        # launch mainwindow.ui file
        uic.loadUi(f"{ABSOLUTE_PATH}/keydialog.ui", self)

        # set gui window size
        self.setMinimumSize(QtCore.QSize(300, 400))
        self.setMaximumSize(QtCore.QSize(300, 400))
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint
                            | QtCore.Qt.WindowCloseButtonHint)

        if self.isSignalConnected(self.submit_dialog_button, 'clicked()'):
            self.submit_dialog_button.clicked.disconnect()
        self.submit_dialog_button.clicked.connect(lambda: self.getKeyInfo())
        self.input_keyStore.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_keyPass.setEchoMode(QtWidgets.QLineEdit.Password)

        self.exec_()

    def getKeyAlias(self):
        return self.input_keyAlias.text()

    def getKeyStore(self):
        return self.input_keyStore.text()

    def getKeyPass(self):
        return self.input_keyPass.text()

    def getKeyInfo(self):
        if self.getKeyAlias() and self.getKeyStore() and self.getKeyPass():
            if self.isSignalConnected(self.submit_dialog_button, 'clicked()'):
                self.submit_dialog_button.clicked.disconnect()
            self.close()
            return True
        else:
            if self.isSignalConnected(self.submit_dialog_button, 'clicked()'):
                self.submit_dialog_button.clicked.disconnect()
            self.close()
            return False

    def isSignalConnected(self, obj, name):
        index = obj.metaObject().indexOfMethod(name)
        if index > -1:
            method = obj.metaObject().method(index)
            if method:
                return obj.isSignalConnected(method)
        return False
