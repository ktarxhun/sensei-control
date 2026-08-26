from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget,
)

from .. import backend
from .button_diagram import ButtonDiagram, make_row_label_pixmap


class ButtonsTab(QWidget):
    changed = Signal()

    def __init__(self, profile: backend.MouseProfile):
        super().__init__()
        self.profile = profile

        for btn, default in backend.DEFAULT_BUTTON_MAPPING.items():
            profile.buttons.setdefault(btn, default)
        for locked in backend.LOCKED_BUTTONS:
            profile.buttons[locked] = backend.DEFAULT_BUTTON_MAPPING[locked]

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
            combo.setCurrentText(profile.buttons[btn])
            combo.currentTextChanged.connect(
                lambda text, b=btn: self._on_button_changed(b, text))

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

    def _on_button_changed(self, btn: str, text: str):
        self.profile.buttons[btn] = text
        self.changed.emit()
