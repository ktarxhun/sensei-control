from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog, QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from .. import backend

EFFECT_LABELS = {
    "solid": "Sabit Renk",
    "gradient": "Özel Gradient",
    "breathing": "Nefes Alma",
    "rainbow": "Gökkuşağı",
}
EFFECT_KEYS = list(EFFECT_LABELS.keys())


class LightingEditor(QGroupBox):
    changed = Signal()

    def __init__(self, title: str, config: backend.LightingConfig):
        super().__init__(title)
        self.config = config

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.effect_combo = QComboBox()
        self.effect_combo.addItems([EFFECT_LABELS[k] for k in EFFECT_KEYS])
        self.effect_combo.setCurrentText(EFFECT_LABELS[config.effect])
        self.effect_combo.currentIndexChanged.connect(self._on_effect_changed)
        form.addRow("Efekt:", self.effect_combo)

        self.color_btn = QPushButton()
        self.color_btn.setFixedHeight(28)
        self.color_btn.clicked.connect(self._pick_color)
        form.addRow("Renk:", self.color_btn)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(100, 60000)
        self.duration_spin.setSingleStep(100)
        self.duration_spin.setSuffix(" ms")
        self.duration_spin.setValue(config.duration_ms)
        self.duration_spin.valueChanged.connect(self._on_duration_changed)
        form.addRow("Süre:", self.duration_spin)

        layout.addLayout(form)

        self.stops_list = QListWidget()
        self.stops_list.setMaximumHeight(100)
        layout.addWidget(self.stops_list)

        stop_btns = QHBoxLayout()
        add_btn = QPushButton("Durak Ekle")
        add_btn.clicked.connect(self._add_stop)
        del_btn = QPushButton("Seçileni Sil")
        del_btn.clicked.connect(self._remove_selected_stop)
        stop_btns.addWidget(add_btn)
        stop_btns.addWidget(del_btn)
        layout.addLayout(stop_btns)

        self._refresh_color_btn()
        self._refresh_stops()
        self._update_visibility()

    def _on_effect_changed(self, index: int):
        self.config.effect = EFFECT_KEYS[index]
        self._update_visibility()
        self.changed.emit()

    def _on_duration_changed(self, value: int):
        self.config.duration_ms = value
        self.changed.emit()

    def _update_visibility(self):
        is_gradient = self.config.effect == "gradient"
        is_solid = self.config.effect == "solid"
        self.stops_list.setVisible(is_gradient)
        self.duration_spin.setVisible(self.config.effect != "solid")
        self.color_btn.setVisible(is_solid or self.config.effect == "breathing")

    def _refresh_color_btn(self):
        hexval = self.config.color
        fg = "#000" if int(hexval.lstrip("#"), 16) > 0x7FFFFF else "#fff"
        self.color_btn.setText(hexval)
        self.color_btn.setStyleSheet(f"background:{hexval};color:{fg};")

    def _pick_color(self):
        color = QColorDialog.getColor(QColor(self.config.color), self, "Renk seç")
        if color.isValid():
            self.config.color = color.name()
            self._refresh_color_btn()
            self.changed.emit()

    def _refresh_stops(self):
        self.stops_list.clear()
        for stop in self.config.stops:
            item = QListWidgetItem(f"{stop.position}%  —  {stop.color}")
            item.setData(1000, stop)
            self.stops_list.addItem(item)

    def _add_stop(self):
        color = QColorDialog.getColor(QColor("#ffffff"), self, "Durak rengi")
        if not color.isValid():
            return
        pos = 0 if not self.config.stops else min(
            100, self.config.stops[-1].position + 25)
        self.config.stops.append(backend.GradientStop(pos, color.name()))
        self._refresh_stops()
        self.changed.emit()

    def _remove_selected_stop(self):
        row = self.stops_list.currentRow()
        if row < 0:
            return
        del self.config.stops[row]
        self._refresh_stops()
        self.changed.emit()


class LightingTab(QWidget):
    changed = Signal()

    def __init__(self, profile: backend.MouseProfile):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Gradient/nefes/gökkuşağı efektleri farenin kendi belleğinde "
            "döngü olarak çalışır, ek yazılım gerekmez."))

        self.logo_editor = LightingEditor("Logo LED", profile.logo)
        self.wheel_editor = LightingEditor("Tekerlek LED", profile.wheel)
        self.logo_editor.changed.connect(self.changed)
        self.wheel_editor.changed.connect(self.changed)

        layout.addWidget(self.logo_editor)
        layout.addWidget(self.wheel_editor)
        layout.addStretch()
