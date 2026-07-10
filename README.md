# Sensei Control

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

## Desteklenen Donanım

Şu an sadece **SteelSeries Sensei Ten** için tasarlandı (buton
yerleşimi, DPI aralığı vb. bu modele özel). `rivalcfg`'nin desteklediği
diğer SteelSeries fareler için `sensei_control/backend.py` içindeki
sabitler güncellenerek uyarlanabilir.

## Lisans

MIT
