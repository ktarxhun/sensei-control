"""rivalcfg sarmalayici: donanim baglantisi, gradient/buton string uretimi,
profil (JSON) kalicilik katmani.

Not: rivalcfg cihazdan mevcut ayarlari OKUYAMIYOR (USB HID cogunlukla
yazma-only). Bu yuzden "su anki durum" kavrami yok - sadece "en son bu
uygulamadan uygulanan ayarlar" JSON'da tutuluyor.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import rivalcfg

CONFIG_DIR = Path.home() / ".config" / "sensei-control"
PROFILES_PATH = CONFIG_DIR / "profiles.json"

DPI_MIN, DPI_MAX, DPI_STEP = 50, 18000, 50
POLLING_RATES = [125, 250, 500, 1000]

MAX_DPI_STAGES = 5
DEFAULT_DPI_STAGES = [400, 800, 1200, 2400, 3200]

BUTTON_SPECIAL_ACTIONS = ["default", "disabled", "dpi", "scrollup", "scrolldown"]
MULTIMEDIA_KEYS = [
    "PlayPause", "Next", "Previous", "Mute", "VolumeUp", "VolumeDown",
]

# rivalcfg'nin resmi sensei_ten_buttons.svg semasindaki etiket
# koordinatlarindan cikarildi (flozz.github.io/rivalcfg/devices/sensei_ten.html)
# Button1/Button2 (sol/sag tik) kilitli oldugu ve arayuzde gosterilmedigi
# icin burada yok - sadece degistirilebilir 6 buton isimlendiriliyor.
BUTTON_LOCATIONS = {
    "Button3": "Teker",
    "Button8": "DPI Buton",
    "Button5": "Sol Ön",
    "Button4": "Sol Arka",
    "Button7": "Sağ Ön",
    "Button6": "Sağ Arka",
}

# Semada/formda gosterim sirasi - mantiksal grup (teker/dpi, sonra
# sol on->arka, sonra sag on->arka). Numara rozetleri bu siraya gore 1-6.
BUTTON_ORDER = ["Button3", "Button8", "Button5", "Button4", "Button7", "Button6"]

DEFAULT_BUTTON_MAPPING = {
    "Button1": "button1", "Button2": "button2", "Button3": "button3",
    "Button4": "button4", "Button5": "button5", "Button6": "PageDown",
    "Button7": "PageUp", "Button8": "dpi",
}

# Sol/sağ tık - yanlışlıkla değiştirilirse tıklama çalışmaz hale gelebilir.
# Arayüzde hiç gösterilmiyor, sadece dahili olarak sabit değerde tutuluyor.
LOCKED_BUTTONS = {"Button1", "Button2"}

_QWERTY_LAYOUT_CACHE: Optional[list[str]] = None


def qwerty_keys() -> list[str]:
    global _QWERTY_LAYOUT_CACHE
    if _QWERTY_LAYOUT_CACHE is None:
        from rivalcfg.handlers.buttons import layout_qwerty
        keys = set(layout_qwerty.layout.keys()) | set(layout_qwerty.aliases.keys())
        _QWERTY_LAYOUT_CACHE = sorted(keys)
    return _QWERTY_LAYOUT_CACHE


def button_value_choices() -> list[str]:
    return (
        BUTTON_SPECIAL_ACTIONS
        + [f"button{i}" for i in range(1, 9)]
        + MULTIMEDIA_KEYS
        + qwerty_keys()
    )


@dataclass
class GradientStop:
    position: int  # 0-100
    color: str  # "#rrggbb"


@dataclass
class LightingConfig:
    effect: str = "solid"  # solid | gradient | breathing | rainbow
    color: str = "#ff0000"
    duration_ms: int = 2000
    stops: list[GradientStop] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "LightingConfig":
        return cls(
            **{**d, "stops": [GradientStop(**s) for s in d.get("stops", [])]})

    def to_rivalcfg_value(self) -> str:
        if self.effect == "solid":
            return self.color
        if self.effect == "breathing":
            return build_gradient_string(
                self.duration_ms,
                [GradientStop(0, self.color), GradientStop(50, "#000000"),
                 GradientStop(100, self.color)],
            )
        if self.effect == "rainbow":
            return build_rainbow_gradient(self.duration_ms)
        if self.effect == "gradient":
            stops = self.stops if len(self.stops) >= 2 else [
                GradientStop(0, self.color), GradientStop(100, self.color),
            ]
            return build_gradient_string(self.duration_ms, stops)
        raise ValueError(f"Bilinmeyen efekt: {self.effect}")


@dataclass
class MouseProfile:
    name: str = "Varsayılan"
    dpi_stages: list[int] = field(default_factory=lambda: list(DEFAULT_DPI_STAGES))
    polling_rate: int = 1000
    logo: LightingConfig = field(default_factory=LightingConfig)
    wheel: LightingConfig = field(
        default_factory=lambda: LightingConfig(color="#0000ff"))
    buttons: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "MouseProfile":
        return cls(
            name=d.get("name", "Varsayılan"),
            dpi_stages=d.get("dpi_stages", DEFAULT_DPI_STAGES),
            polling_rate=d.get("polling_rate", 1000),
            logo=LightingConfig.from_dict(d.get("logo") or {}),
            wheel=LightingConfig.from_dict(d.get("wheel") or {"color": "#0000ff"}),
            buttons=d.get("buttons", {}),
        )

    def apply_to_mouse(self, mouse: "rivalcfg.mouse.Mouse") -> None:
        dpi_str = ", ".join(str(v) for v in self.dpi_stages)
        mouse.set_sensitivity(dpi_str)
        mouse.set_polling_rate(self.polling_rate)
        mouse.set_logo_color(self.logo.to_rivalcfg_value())
        mouse.set_wheel_color(self.wheel.to_rivalcfg_value())
        if self.buttons:
            mouse.set_buttons_mapping(build_buttons_string(self.buttons))
        mouse.save()


def build_gradient_string(duration_ms: int, stops: list[GradientStop]) -> str:
    if not stops:
        raise ValueError("En az bir durak gerekli")
    colors = ", ".join(f"{s.position}%: {s.color}" for s in stops)
    return f"rgbgradient(duration={duration_ms}; colors={colors})"


def build_rainbow_gradient(duration_ms: int) -> str:
    hues = [
        (0, "#ff0000"), (17, "#ffff00"), (33, "#00ff00"),
        (50, "#00ffff"), (67, "#0000ff"), (83, "#ff00ff"), (100, "#ff0000"),
    ]
    stops = [GradientStop(pos, color) for pos, color in hues]
    return build_gradient_string(duration_ms, stops)


def build_buttons_string(mapping: dict[str, str]) -> str:
    parts = [f"{btn.lower()}={val}" for btn, val in mapping.items() if val]
    parts.append("layout=qwerty")
    return "buttons(" + "; ".join(parts) + ")"


def connect_mouse():
    """Baglı Sensei Ten'i doner, yoksa None."""
    try:
        return rivalcfg.get_first_mouse()
    except Exception:
        return None


def load_profiles() -> dict[str, MouseProfile]:
    if not PROFILES_PATH.exists():
        default = MouseProfile()
        return {default.name: default}
    try:
        raw = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
        profiles = {name: MouseProfile.from_dict(d) for name, d in raw.items()}
        if profiles:
            return profiles
    except (json.JSONDecodeError, OSError):
        pass
    default = MouseProfile()
    return {default.name: default}


def save_profiles(profiles: dict[str, MouseProfile]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    raw = {name: p.to_dict() for name, p in profiles.items()}
    PROFILES_PATH.write_text(
        json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
