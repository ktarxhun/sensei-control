from typing import Callable, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QVBoxLayout, QWidget,
)

from .. import backend


class GeneralTab(QWidget):
    changed = Signal()
    profile_reset = Signal()

    def __init__(self, profile: backend.MouseProfile,
                 get_mouse: Callable[[], Optional[object]]):
        super().__init__()
        self.profile = profile
        self.get_mouse = get_mouse

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.polling_combo = QComboBox()
        self.polling_combo.addItems([f"{r} Hz" for r in backend.POLLING_RATES])
        self.polling_combo.setCurrentText(f"{profile.polling_rate} Hz")
        self.polling_combo.currentTextChanged.connect(self._on_polling_changed)
        form.addRow("Polling Rate:", self.polling_combo)

        status_row = QHBoxLayout()
        self.status_label = QLabel("Bilinmiyor")
        refresh_btn = QPushButton("Bağlantıyı Kontrol Et")
        refresh_btn.clicked.connect(self.refresh_status)
        status_row.addWidget(self.status_label)
        status_row.addWidget(refresh_btn)
        status_row.addStretch()
        form.addRow("Bağlantı:", status_row)

        fw_row = QHBoxLayout()
        self.firmware_label = QLabel("—")
        fw_refresh_btn = QPushButton("Firmware Sürümünü Oku")
        fw_refresh_btn.clicked.connect(self.refresh_firmware)
        fw_row.addWidget(self.firmware_label)
        fw_row.addWidget(fw_refresh_btn)
        fw_row.addStretch()
        form.addRow("Firmware:", fw_row)

        layout.addLayout(form)
        layout.addStretch()

        reset_btn = QPushButton("Fabrika Ayarlarına Sıfırla")
        reset_btn.clicked.connect(self.factory_reset)
        layout.addWidget(reset_btn)

        self.refresh_status()

    def _on_polling_changed(self, text: str):
        if not text:
            return
        self.profile.polling_rate = int(text.split()[0])
        self.changed.emit()

    def _get_connected_mouse(self):
        mouse = self.get_mouse()
        if mouse is None:
            QMessageBox.warning(self, "Bağlı değil", "Fare bağlı değil.")
        return mouse

    def refresh_status(self):
        mouse = self.get_mouse()
        if mouse is None:
            self.status_label.setText("Bağlı değil")
            self.status_label.setStyleSheet("color: #d08770;")
        else:
            self.status_label.setText(f"Bağlı — {mouse.name}")
            self.status_label.setStyleSheet("color: #a3be8c;")

    def refresh_firmware(self):
        mouse = self._get_connected_mouse()
        if mouse is None:
            return
        try:
            self.firmware_label.setText(str(mouse.firmware_version))
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))

    def factory_reset(self):
        mouse = self._get_connected_mouse()
        if mouse is None:
            return
        confirm = QMessageBox.question(
            self, "Emin misin?",
            "Fabrika ayarlarına sıfırlanacak, tüm özel ayarlar kaybolacak.")
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            mouse.reset_settings()
            mouse.save()
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))
            return
        QMessageBox.information(self, "Tamam", "Fabrika ayarlarına sıfırlandı.")
        self.profile_reset.emit()
