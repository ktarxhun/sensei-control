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


def _draw_badge(painter: QPainter, center: QPointF, diameter: float,
                 number: int, border: QPen = Qt.PenStyle.NoPen) -> None:
    """Mor arkaplanli daire icine ortalanmis, beyaz rozet numarasi cizer."""
    painter.setPen(border)
    painter.setBrush(_BADGE_COLOR)
    painter.drawEllipse(center, diameter / 2, diameter / 2)

    font = QFont()
    font.setBold(True)
    font.setPointSize(int(diameter * 0.42))
    painter.setFont(font)
    painter.setPen(Qt.GlobalColor.white)
    painter.drawText(
        QRectF(center.x() - diameter / 2, center.y() - diameter / 2,
               diameter, diameter),
        Qt.AlignmentFlag.AlignCenter, str(number))


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
    _draw_badge(painter, QPointF(badge_d / 2 + 2, cy), badge_d, number)

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

    def _body_rect(self) -> QRectF:
        cx = _DIAGRAM_W / 2
        body_w, body_h = 145, 280
        top = 26
        return QRectF(cx - body_w / 2, top, body_w, body_h)

    def _wheel_y(self, rect: QRectF) -> float:
        # Tekerlek govdenin en ucunda degil, biraz icinde (gercek Sensei
        # Ten'de govde ucu ile tekerlek arasinda pay var)
        return rect.top() + rect.height() * 0.20

    def _marker_positions(self) -> dict[str, QPointF]:
        rect = self._body_rect()
        wheel_y = self._wheel_y(rect)
        cx = rect.center().x()
        return {
            "Button3": QPointF(cx, wheel_y),
            "Button8": QPointF(cx, wheel_y + 34),
            "Button5": QPointF(rect.left() + 10, rect.top() + rect.height() * 0.52),
            "Button4": QPointF(rect.left() + 10, rect.top() + rect.height() * 0.76),
            "Button7": QPointF(rect.right() - 10, rect.top() + rect.height() * 0.52),
            "Button6": QPointF(rect.right() - 10, rect.top() + rect.height() * 0.76),
        }

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self._body_rect()
        cx, top, bottom = rect.center().x(), rect.top(), rect.bottom()
        left, right, body_w = rect.left(), rect.right(), rect.width()
        body_h = rect.height()

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

        wheel_y = self._wheel_y(rect)
        painter.setPen(QPen(QColor(50, 52, 58), 1.5))
        painter.drawLine(int(cx), int(top + 5), int(cx), int(wheel_y - 17))

        wheel_rect = QRectF(cx - 9, wheel_y - 17, 18, 32)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(10, 10, 12))
        painter.drawRoundedRect(wheel_rect, 7, 7)

        positions = self._marker_positions()
        badge_d = 24
        badge_border = QPen(QColor(20, 20, 24), 1.5)
        for i, name in enumerate(BUTTON_ORDER, start=1):
            _draw_badge(painter, positions[name], badge_d, i, border=badge_border)

        painter.end()
