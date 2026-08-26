from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox, QGridLayout, QLabel, QSpinBox, QVBoxLayout, QWidget,
)

from .. import backend


class DpiTab(QWidget):
    changed = Signal()

    def __init__(self, profile: backend.MouseProfile):
        super().__init__()
        self.profile = profile

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Buton 8 (varsayılan) presetler arasında geçiş yapar. "
            "İlk kademe her zaman açık kalır."))

        grid = QGridLayout()
        self.checks: list[QCheckBox] = []
        self.spins: list[QSpinBox] = []

        stages = profile.dpi_stages or backend.DEFAULT_DPI_STAGES
        for i in range(backend.MAX_DPI_STAGES):
            check = QCheckBox(f"Kademe {i + 1}")
            spin = QSpinBox()
            spin.setRange(backend.DPI_MIN, backend.DPI_MAX)
            spin.setSingleStep(backend.DPI_STEP)
            spin.setSuffix(" DPI")
            spin.setValue(
                stages[i] if i < len(stages) else backend.DEFAULT_DPI_STAGES[i])
            enabled = i == 0 or i < len(profile.dpi_stages)
            check.setChecked(enabled)
            spin.setEnabled(enabled)
            if i == 0:
                check.setEnabled(False)  # en az bir kademe zorunlu

            check.toggled.connect(self._make_toggle_handler(i))
            spin.valueChanged.connect(self._sync)

            grid.addWidget(check, i, 0)
            grid.addWidget(spin, i, 1)
            self.checks.append(check)
            self.spins.append(spin)

        layout.addLayout(grid)
        layout.addStretch()

    def _make_toggle_handler(self, index: int):
        def handler(checked: bool):
            # Kademeler her zaman ardışık bir önek (prefix) olmalı - modelin
            # tuttuğu dpi_stages listesi sıra bazlı, boşluklu seçim desteklemiyor.
            if checked:
                for i in range(index):
                    self.checks[i].setChecked(True)
            else:
                for i in range(index + 1, len(self.checks)):
                    self.checks[i].setChecked(False)
            self.spins[index].setEnabled(checked)
            self._sync()
        return handler

    def _sync(self):
        self.profile.dpi_stages = [
            spin.value() for check, spin in zip(self.checks, self.spins)
            if check.isChecked()
        ]
        self.changed.emit()
