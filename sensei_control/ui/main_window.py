from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QInputDialog, QLabel, QMainWindow, QMessageBox,
    QPushButton, QTabWidget, QVBoxLayout, QWidget,
)

from .. import backend
from .tab_buttons import ButtonsTab
from .tab_dpi import DpiTab
from .tab_general import GeneralTab
from .tab_lighting import LightingTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensei Control")
        self.resize(460, 560)

        self.profiles = backend.load_profiles()
        self.current_name = next(iter(self.profiles))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        profile_row = QHBoxLayout()
        profile_row.addWidget(QLabel("Profil:"))
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(self.profiles.keys())
        self.profile_combo.currentTextChanged.connect(self._on_profile_selected)
        profile_row.addWidget(self.profile_combo, stretch=1)

        new_btn = QPushButton("Yeni")
        new_btn.clicked.connect(self._new_profile)
        delete_btn = QPushButton("Sil")
        delete_btn.clicked.connect(self._delete_profile)
        profile_row.addWidget(new_btn)
        profile_row.addWidget(delete_btn)
        layout.addLayout(profile_row)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        bottom_row = QHBoxLayout()
        self.apply_btn = QPushButton("Cihaza Uygula")
        self.apply_btn.clicked.connect(self._apply_to_device)
        save_btn = QPushButton("Profili Kaydet")
        save_btn.clicked.connect(self._save_profiles)
        bottom_row.addWidget(save_btn)
        bottom_row.addWidget(self.apply_btn)
        layout.addLayout(bottom_row)

        self._rebuild_tabs()
        self._load_local_extensions()

    def _load_local_extensions(self):
        """Bu makineye ozel, repoya yuklenmeyen eklentiler icin genisletme
        noktasi (bkz. .gitignore: local_extensions.py)."""
        try:
            from .. import local_extensions
        except ImportError:
            return
        local_extensions.register(self)

    @property
    def profile(self) -> backend.MouseProfile:
        return self.profiles[self.current_name]

    def get_mouse(self):
        return backend.connect_mouse()

    def _rebuild_tabs(self):
        self.tabs.clear()
        profile = self.profile
        self.tabs.addTab(DpiTab(profile), "DPI")
        self.tabs.addTab(LightingTab(profile), "Aydınlatma")
        self.tabs.addTab(ButtonsTab(profile), "Butonlar")
        general_tab = GeneralTab(profile, self.get_mouse)
        general_tab.profile_reset.connect(self._on_factory_reset)
        self.tabs.addTab(general_tab, "Genel")

    def _on_factory_reset(self):
        self.profiles[self.current_name] = backend.MouseProfile(
            name=self.current_name)
        backend.save_profiles(self.profiles)
        self._rebuild_tabs()

    def _on_profile_selected(self, name: str):
        if not name or name == self.current_name:
            return
        self.current_name = name
        self._rebuild_tabs()

    def _new_profile(self):
        name, ok = QInputDialog.getText(self, "Yeni Profil", "Profil adı:")
        if not ok or not name.strip():
            return
        name = name.strip()
        if name in self.profiles:
            QMessageBox.warning(self, "Zaten var", "Bu isimde bir profil var.")
            return
        self.profiles[name] = backend.MouseProfile(name=name)
        self.profile_combo.addItem(name)
        self.profile_combo.setCurrentText(name)
        backend.save_profiles(self.profiles)

    def _delete_profile(self):
        if len(self.profiles) <= 1:
            QMessageBox.warning(self, "Olmaz", "En az bir profil kalmalı.")
            return
        name = self.current_name
        confirm = QMessageBox.question(self, "Emin misin?", f"'{name}' silinsin mi?")
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self.profile_combo.removeItem(self.profile_combo.findText(name))
        del self.profiles[name]
        backend.save_profiles(self.profiles)

    def _save_profiles(self):
        backend.save_profiles(self.profiles)
        QMessageBox.information(self, "Kaydedildi", "Profil diske kaydedildi.")

    def _apply_to_device(self):
        mouse = self.get_mouse()
        if mouse is None:
            QMessageBox.warning(self, "Bağlı değil",
                                "Sensei Ten bulunamadı. Kabloyu kontrol et.")
            return
        try:
            self.profile.apply_to_mouse(mouse)
            backend.save_profiles(self.profiles)
            QMessageBox.information(self, "Uygulandı",
                                    "Ayarlar fareye yazıldı ve kaydedildi.")
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))
