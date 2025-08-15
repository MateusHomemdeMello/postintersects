# Main
#Olá
import sys
from PyQt6.QtWidgets import QApplication
from utils.style import DARK_STYLE
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)

    janela = MainWindow()
    janela.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
