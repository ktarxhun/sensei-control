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


class LightingEditor(QGroupBox):
    changed = Signal()

    def __init__(self, title: str, config: backend.LightingConfig):
        super().__init__(title)
        self.config = config

        layout = QVBoxLayout(self)
        self.form = QFormLayout()

        self.effect_combo = QComboBox()
        for key, label in EFFECT_LABELS.items():
            self.effect_combo.addItem(label, userData=key)
        self.effect_combo.setCurrentIndex(self.effect_combo.findData(config.effect))
        self.effect_combo.currentIndexChanged.connect(self._on_effect_changed)
        self.form.addRow("Efekt:", self.effect_combo)

        self.color_btn = QPushButton()
        self.color_btn.setFixedHeight(28)
        self.color_btn.clicked.connect(self._pick_color)
        self.form.addRow("Renk:", self.color_btn)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(100, 60000)
        self.duration_spin.setSingleStep(100)
        self.duration_spin.setSuffix(" ms")
        self.duration_spin.setValue(config.duration_ms)
        self.duration_spin.valueChanged.connect(self._on_duration_changed)
        self.form.addRow("Süre:", self.duration_spin)

        layout.addLayout(self.form)

        self.stops_list = QListWidget()
        self.stops_list.setMaximumHeight(100)
        layout.addWidget(self.stops_list)

        self.stop_btns = QHBoxLayout()
        add_btn = QPushButton("Durak Ekle")
        add_btn.clicked.connect(self._add_stop)
        del_btn = QPushButton("Seçileni Sil")
        del_btn.clicked.connect(self._remove_selected_stop)
        self.stop_btns.addWidget(add_btn)
        self.stop_btns.addWidget(del_btn)
        layout.addLayout(self.stop_btns)

        self._refresh_color_btn()
        self._refresh_stops()
        self._update_visibility()

    def _on_effect_changed(self, index: int):
        self.config.effect = self.effect_combo.currentData()
        self._update_visibility()
        self.changed.emit()

    def _on_duration_changed(self, value: int):
        self.config.duration_ms = value
        self.changed.emit()

    def _set_stop_widgets_visible(self, visible: bool):
        self.stops_list.setVisible(visible)
        for i in range(self.stop_btns.count()):
            widget = self.stop_btns.itemAt(i).widget()
            if widget is not None:
                widget.setVisible(visible)

    def _update_visibility(self):
        is_gradient = self.config.effect == "gradient"
        is_solid = self.config.effect == "solid"
        show_color = is_solid or self.config.effect == "breathing"
        show_duration = self.config.effect != "solid"

        self._set_stop_widgets_visible(is_gradient)
        self.form.setRowVisible(self.color_btn, show_color)
        self.form.setRowVisible(self.duration_spin, show_duration)

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
            self.stops_list.addItem(
                QListWidgetItem(f"{stop.position}%  —  {stop.color}"))

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
