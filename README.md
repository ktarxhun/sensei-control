# Sensei Control

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/UI-PySide6-41cd52.svg)](https://doc.qt.io/qtforpython/)

SteelSeries Sensei Ten faresi için Linux'ta kapsamlı bir kontrol
uygulaması — SteelSeries'in resmi "GG" yazılımının Linux'taki karşılığı.
[rivalcfg](https://github.com/flozz/rivalcfg) üzerine kurulu, PySide6 ile
yazılmış.

## Özellikler

- **DPI** — 5 kademeye kadar, 50-18000 aralığında, 50 adımlarla
- **Aydınlatma** — Logo ve Tekerlek LED'leri bağımsız olarak: sabit renk,
  özel gradient (durak editörü), nefes alma, gökkuşağı efektleri
- **Buton eşleme** — 8 butonun 6'sı (sol/sağ tık güvenlik için kilitli)
  özel eylemlere, diğer mouse butonlarına, multimedya tuşlarına veya
  190+ klavye tuşuna atanabilir. Resmi rivalcfg şemasından çıkarılmış
  görsel buton yerleşim diyagramı içerir.
- **Polling Rate** — 125/250/500/1000 Hz
- **Yazılım profilleri** — Farklı ayar kombinasyonlarını kaydedip tek
  tıkla uygulama (JSON, `~/.config/sensei-control/`)
- **Firmware sürümü okuma**, **fabrika sıfırlama**

## Neden

`rivalcfg` mükemmel bir CLI/kütüphane ama GUI'si yok. Bu proje
`rivalcfg`'yi Python kütüphanesi olarak doğrudan kullanan (subprocess
değil), gerçek bir ayar deneyimi sunan bir GUI.

## Kurulum

### Bağımlılıklar

```bash
# Arch Linux
sudo pacman -S python-pyside6 python-pip
pip install --user rivalcfg

# rivalcfg'nin udev kuralını kurması gerekiyor (fareye root'suz erişim için)
sudo $(python3 -c "import shutil; print(shutil.which('rivalcfg'))") --update-udev
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### Uygulama

```bash
git clone https://github.com/ktarxhun/sensei-control.git
cd sensei-control

# Terminalden çalıştır
python3 -m sensei_control

# Ya da uygulama menüsüne ekle
mkdir -p ~/.local/bin
cp packaging/sensei-control ~/.local/bin/
chmod +x ~/.local/bin/sensei-control
cp packaging/sensei-control.desktop ~/.local/share/applications/
```

`~/.local/bin`'in `PATH`'te olduğundan emin ol.

## Proje Yapısı

```
sensei_control/
├── backend.py       # rivalcfg köprüsü, donanım sabitleri (DPI aralığı, buton haritası)
├── icon.py          # Uygulama ikonu
└── ui/
    ├── main_window.py    # Ana pencere, sekme yönetimi
    ├── tab_dpi.py        # DPI ayarları
    ├── tab_lighting.py   # LED/aydınlatma efektleri
    ├── tab_buttons.py    # Buton eşleme
    ├── tab_general.py    # Polling rate, profiller, firmware
    └── button_diagram.py # Görsel buton yerleşim diyagramı
```

`main_window.py` opsiyonel olarak `local_extensions.py` adında, bilerek
git'e dahil edilmeyen bir yerel eklenti dosyasını yükler — makineye özel
kişisel eklemeler için bir kanca (bkz. `.gitignore`).

## Desteklenen Donanım

Şu an sadece **SteelSeries Sensei Ten** için tasarlandı (buton
yerleşimi, DPI aralığı vb. bu modele özel). `rivalcfg`'nin desteklediği
diğer SteelSeries fareler için `sensei_control/backend.py` içindeki
sabitler güncellenerek uyarlanabilir.

## Lisans

MIT
