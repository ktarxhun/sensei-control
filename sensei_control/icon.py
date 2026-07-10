from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QIcon, QLinearGradient, QPainter, QPainterPath, QPixmap


def make_app_icon() -> QIcon:
    """Ust-taniden gorunumlu, sade bir oyuncu faresi silueti."""
    size = 128
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    body = QPainterPath()
    body.moveTo(64, 10)
    body.cubicTo(20, 10, 14, 40, 14, 62)
    body.cubicTo(14, 96, 30, 118, 64, 118)
    body.cubicTo(98, 118, 114, 96, 114, 62)
    body.cubicTo(114, 40, 108, 10, 64, 10)
    body.closeSubpath()

    body_gradient = QLinearGradient(QPointF(64, 10), QPointF(64, 118))
    body_gradient.setColorAt(0.0, Qt.GlobalColor.darkGray)
    body_gradient.setColorAt(1.0, Qt.GlobalColor.black)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(body_gradient)
    painter.drawPath(body)

    painter.setPen(Qt.GlobalColor.black)
    painter.drawLine(64, 14, 64, 46)

    painter.setBrush(Qt.GlobalColor.black)
    painter.drawRoundedRect(QRectF(58, 22, 12, 26), 5, 5)

    accent_gradient = QLinearGradient(QPointF(20, 0), QPointF(108, 0))
    accent_gradient.setColorAt(0.0, "#ff3b3b")
    accent_gradient.setColorAt(0.5, "#a020f0")
    accent_gradient.setColorAt(1.0, "#00d4ff")
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(accent_gradient)
    painter.drawRoundedRect(QRectF(24, 100, 80, 8), 4, 4)

    painter.end()
    return QIcon(pixmap)
