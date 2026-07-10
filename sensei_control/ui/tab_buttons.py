from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget,
)

from .. import backend
from .button_diagram import ButtonDiagram, make_row_label_pixmap

DEFAULT_MAPPING = {
    "Button1": "button1", "Button2": "button2", "Button3": "button3",
    "Button4": "button4", "Button5": "button5", "Button6": "PageDown",
    "Button7": "PageUp", "Button8": "dpi",
}

# Sol/sağ tık - yanlışlıkla değiştirilirse tıklama çalışmaz hale gelebilir.
# Arayüzde hiç gösterilmiyor, sadece dahili olarak sabit değerde tutuluyor.
LOCKED_BUTTONS = {"Button1", "Button2"}


class ButtonsTab(QWidget):
    changed = Signal()

    def __init__(self, profile: backend.MouseProfile):
        super().__init__()
        self.profile = profile

        root = QHBoxLayout(self)

        left = QVBoxLayout()
        form = QFormLayout()
        form.setVerticalSpacing(10)
        self.combos: dict[str, QComboBox] = {}
        choices = backend.button_value_choices()

        for i, btn in enumerate(backend.BUTTON_ORDER, start=1):
            combo = QComboBox()
            combo.setEditable(True)
            combo.addItems(choices)
            current = profile.buttons.get(btn, DEFAULT_MAPPING.get(btn, "default"))
            if current in choices:
                combo.setCurrentText(current)
            combo.currentTextChanged.connect(self._make_handler(btn))

            row_label = QLabel()
            row_label.setPixmap(
                make_row_label_pixmap(i, backend.BUTTON_LOCATIONS[btn]))

            form.addRow(row_label, combo)
            self.combos[btn] = combo

        left.addLayout(form)
        left.addStretch()
        root.addLayout(left, stretch=1)

        right = QVBoxLayout()
        right.addStretch()
        right.addWidget(ButtonDiagram())
        right.addStretch()
        root.addLayout(right, stretch=0)

        if not profile.buttons:
            profile.buttons = dict(DEFAULT_MAPPING)
        for locked in LOCKED_BUTTONS:
            profile.buttons[locked] = DEFAULT_MAPPING[locked]

    def _make_handler(self, btn: str):
        def handler(text: str):
            self.profile.buttons[btn] = text
            self.changed.emit()
        return handler
