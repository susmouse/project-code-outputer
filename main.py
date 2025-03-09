from gui import TreeGeneratorGUI
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication([])
    window = TreeGeneratorGUI()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
