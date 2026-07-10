import sys

from PySide6.QtWidgets import QApplication

from .icon import make_app_icon
from .ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sensei Control")

    window = MainWindow()
    window.setWindowIcon(make_app_icon())
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
