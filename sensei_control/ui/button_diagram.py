"""Sensei Ten buton yerlesim semasi.

Kaynak: rivalcfg resmi belgelerindeki sensei_ten_buttons.svg icindeki
etiket koordinatlari (flozz.github.io/rivalcfg/devices/sensei_ten.html) +
Sensei Ten'in ambidextrous 2x2 yan tus + tekerlek arkasi DPI tus yerlesimi.

Sol/sag tik (Button1/Button2) kilitli ve degistirilemez oldugu icin
semada hic gosterilmiyor - sadece degistirilebilir 6 buton var, numarali
kirmizi rozetlerle isaretleniyor (asagidaki form listesindeki rozetlerle
birebir ayni numaralar).
"""
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor, QFont, QFontMetrics, QLinearGradient, QPainter, QPainterPath,
    QPen, QPixmap,
)
from PySide6.QtWidgets import QWidget

from ..backend import BUTTON_ORDER

_BADGE_COLOR = QColor(108, 99, 255)  # sakin indigo/mor - alarm kirmizisi degil
_DIAGRAM_W = 230
_DIAGRAM_H = 340


def make_badge_pixmap(number: int, diameter: int = 20) -> QPixmap:
    pixmap = QPixmap(diameter, diameter)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(_BADGE_COLOR)
    painter.drawEllipse(0, 0, diameter, diameter)
    painter.setPen(Qt.GlobalColor.white)
    font = QFont()
    font.setBold(True)
    font.setPointSize(int(diameter * 0.5))
    painter.setFont(font)
    painter.drawText(QRectF(0, 0, diameter, diameter),
                     Qt.AlignmentFlag.AlignCenter, str(number))
    painter.end()
    return pixmap


def make_row_label_pixmap(number: int, text: str, height: int = 26) -> QPixmap:
    """Rozet + metni TEK pixmap'te ciz - iki ayri widget'i hizalamaya
    calismak yerine, satirin kendisi zaten piksel-hassas hizali olur."""
    badge_d = height - 4
    font = QFont()
    font.setPointSize(10)
    metrics = QFontMetrics(font)
    text_w = metrics.horizontalAdvance(text)
    width = badge_d + 8 + text_w + 4

    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    cy = height / 2
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(_BADGE_COLOR)
    painter.drawEllipse(QPointF(badge_d / 2 + 2, cy), badge_d / 2, badge_d / 2)

    badge_font = QFont()
    badge_font.setBold(True)
    badge_font.setPointSize(int(badge_d * 0.42))
    painter.setFont(badge_font)
    painter.setPen(Qt.GlobalColor.white)
    painter.drawText(QRectF(2, cy - badge_d / 2, badge_d, badge_d),
                     Qt.AlignmentFlag.AlignCenter, str(number))

    painter.setFont(font)
    painter.setPen(QColor(220, 220, 220))
    painter.drawText(QRectF(badge_d + 8, 0, text_w + 4, height),
                     Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                     text)

    painter.end()
    return pixmap


class ButtonDiagram(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(_DIAGRAM_W, _DIAGRAM_H)

    def _body_geometry(self):
        cx = _DIAGRAM_W / 2
        body_w, body_h = 145, 280
        top = 26
        bottom = top + body_h
        left = cx - body_w / 2
        right = cx + body_w / 2
        return cx, top, bottom, left, right, body_w, body_h

    def _marker_positions(self) -> dict[str, QPointF]:
        cx, top, bottom, left, right, body_w, body_h = self._body_geometry()
        # Tekerlek govdenin en ucunda degil, biraz icinde (gercek Sensei
        # Ten'de govde ucu ile tekerlek arasinda pay var)
        wheel_y = top + body_h * 0.20
        return {
            "Button3": QPointF(cx, wheel_y),
            "Button8": QPointF(cx, wheel_y + 34),
            "Button5": QPointF(left + 10, top + body_h * 0.52),
            "Button4": QPointF(left + 10, top + body_h * 0.76),
            "Button7": QPointF(right - 10, top + body_h * 0.52),
            "Button6": QPointF(right - 10, top + body_h * 0.76),
        }

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, top, bottom, left, right, body_w, body_h = self._body_geometry()

        # Sensei Ten: simetrik (ambidextrous) yumurta govde, on tarafta
        # duz-ish bir kavis (sivri uc degil), arkada daha dolgun.
        body = QPainterPath()
        body.moveTo(left + body_w * 0.18, top)
        body.quadTo(cx, top - 8, right - body_w * 0.18, top)
        body.cubicTo(right + 10, top + body_h * 0.18,
                     right + 8, top + body_h * 0.5,
                     right - 5, top + body_h * 0.72)
        body.cubicTo(right - 15, top + body_h * 0.95,
                     cx + body_w * 0.3, bottom,
                     cx, bottom)
        body.cubicTo(cx - body_w * 0.3, bottom,
                     left + 15, top + body_h * 0.95,
                     left + 5, top + body_h * 0.72)
        body.cubicTo(left - 8, top + body_h * 0.5,
                     left - 10, top + body_h * 0.18,
                     left + body_w * 0.18, top)
        body.closeSubpath()

        gradient = QLinearGradient(QPointF(cx, top), QPointF(cx, bottom))
        gradient.setColorAt(0.0, QColor(72, 74, 80))
        gradient.setColorAt(1.0, QColor(24, 24, 28))
        painter.setPen(QPen(QColor(15, 15, 18), 1.5))
        painter.setBrush(gradient)
        painter.drawPath(body)

        wheel_y = top + body_h * 0.20
        painter.setPen(QPen(QColor(50, 52, 58), 1.5))
        painter.drawLine(int(cx), int(top + 5), int(cx), int(wheel_y - 17))

        wheel_rect = QRectF(cx - 9, wheel_y - 17, 18, 32)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(10, 10, 12))
        painter.drawRoundedRect(wheel_rect, 7, 7)

        positions = self._marker_positions()
        badge_d = 24
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)

        for i, name in enumerate(BUTTON_ORDER, start=1):
            point = positions[name]
            painter.setPen(QPen(QColor(20, 20, 24), 1.5))
            painter.setBrush(_BADGE_COLOR)
            painter.drawEllipse(point, badge_d / 2, badge_d / 2)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(
                QRectF(point.x() - badge_d / 2, point.y() - badge_d / 2,
                       badge_d, badge_d),
                Qt.AlignmentFlag.AlignCenter, str(i))

        painter.end()
