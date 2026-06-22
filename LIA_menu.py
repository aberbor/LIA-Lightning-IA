import sys
import cv2
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QFormLayout, QLineEdit, QSlider, QLabel, QPushButton,
    QStackedWidget, QFrame, QSizePolicy, QSpacerItem, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QImage, QPixmap, QFont, QColor, QPalette, QIcon

from LIA_seguimiento import controlSeguimiento

# ─────────────────────────────────────────────
#  PALETA Y ESTILOS GLOBALES
# ─────────────────────────────────────────────
STYLE_GLOBAL = """
    QMainWindow, QWidget {
        background-color: #0e0f11;
        color: #d4d8e2;
        font-family: 'Courier New', monospace;
    }
    QTabWidget::pane {
        border: 1px solid #2a2d35;
        background: #12141a;
        border-radius: 4px;
    }
    QTabBar::tab {
        background: #1a1c23;
        color: #7a7f8e;
        padding: 8px 18px;
        border: 1px solid #2a2d35;
        border-bottom: none;
        font-size: 11px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    QTabBar::tab:selected {
        background: #12141a;
        color: #f0c040;
        border-top: 2px solid #f0c040;
    }
    QLineEdit {
        background: #1a1c23;
        border: 1px solid #2e3140;
        border-radius: 3px;
        color: #e0e4f0;
        padding: 4px 8px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
    }
    QLineEdit:focus {
        border: 1px solid #f0c040;
    }
    QLabel {
        color: #9aa0b0;
        font-size: 11px;
        letter-spacing: 0.5px;
    }
    QFormLayout QLabel {
        color: #7a8090;
        font-size: 10px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    QScrollBar:vertical {
        background: #1a1c23;
        width: 6px;
    }
    QScrollBar::handle:vertical {
        background: #3a3d4a;
        border-radius: 3px;
    }
"""

STYLE_BTN_PRIMARY = """
    QPushButton {
        background-color: #1e2128;
        color: #f0c040;
        border: 1px solid #f0c040;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        letter-spacing: 2px;
        padding: 10px 20px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #2a2d00;
        border-color: #ffe080;
        color: #ffe080;
    }
    QPushButton:pressed {
        background-color: #f0c040;
        color: #0e0f11;
    }
"""

STYLE_BTN_DANGER = """
    QPushButton {
        background-color: #1e1215;
        color: #e05050;
        border: 1px solid #e05050;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        letter-spacing: 2px;
        padding: 10px 20px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #2a0a0a;
        border-color: #ff8080;
        color: #ff8080;
    }
    QPushButton:pressed {
        background-color: #e05050;
        color: #0e0f11;
    }
"""

STYLE_SLIDER_VERTICAL = """
    QSlider::groove:vertical {
        background: #1a1c23;
        width: 6px;
        border-radius: 3px;
        border: 1px solid #2a2d35;
    }
    QSlider::handle:vertical {
        background: #f0c040;
        border: 2px solid #c09a20;
        height: 18px;
        width: 30px;
        margin: 0 -12px;
        border-radius: 3px;
    }
    QSlider::sub-page:vertical {
        background: #2a2d35;
        border-radius: 3px;
    }
    QSlider::add-page:vertical {
        background: #f0c040;
        border-radius: 3px;
        opacity: 0.8;
    }
"""

STYLE_FADER_LABEL = """
    QLabel {
        color: #f0c040;
        font-size: 9px;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: bold;
        text-align: center;
    }
"""

STYLE_FADER_VALUE = """
    QLabel {
        color: #5a6070;
        font-size: 9px;
        font-family: 'Courier New', monospace;
        text-align: center;
    }
"""

# ───────────────────────
#  PANTALLA DE INICIO
# ───────────────────────
class pantallaInicio(QWidget):
    def __init__(self, on_start):
        super().__init__()
        self.on_start = on_start
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)

        # Logo / Título
        lbl_logo = QLabel("L I A")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet("""
            font-family: 'Courier New', monospace;
            font-size: 52px;
            font-weight: bold;
            color: #f0c040;
            letter-spacing: 18px;
        """)

        lbl_sub = QLabel("ILUMINANDO EL FUTURO")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet("""
            font-family: 'Courier New', monospace;
            font-size: 11px;
            color: #4a5060;
            letter-spacing: 6px;
        """)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setMaximumWidth(300)
        sep.setStyleSheet("color: #2a2d35; background: #2a2d35;")

        # Estado
        self.lbl_status = QLabel("SISTEMA EN ESPERA")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("""
            font-family: 'Courier New', monospace;
            font-size: 10px;
            color: #3a4050;
            letter-spacing: 3px;
        """)

        # Botón de encendido
        btn_power = QPushButton("⏻  ENCENDER SISTEMA")
        btn_power.setFixedSize(280, 60)
        btn_power.setStyleSheet("""
            QPushButton {
                background-color: #0e1a0e;
                color: #40d060;
                border: 2px solid #40d060;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                letter-spacing: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #162516;
                border-color: #60ff80;
                color: #60ff80;
            }
            QPushButton:pressed {
                background-color: #40d060;
                color: #0e0f11;
            }
        """)
        btn_power.clicked.connect(self._iniciar)

        lbl_version = QLabel("v1.0  —  © LIA Project")
        lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_version.setStyleSheet("color: #2a2d35; font-size: 9px; letter-spacing: 2px;")

        layout.addStretch()
        layout.addWidget(lbl_logo)
        layout.addWidget(lbl_sub)
        layout.addWidget(sep, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(10)
        layout.addWidget(self.lbl_status)
        layout.addSpacing(20)
        layout.addWidget(btn_power, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
        layout.addWidget(lbl_version)

    def _iniciar(self):
        self.lbl_status.setText("INICIANDO...")
        self.lbl_status.setStyleSheet("""
            font-family: 'Courier New', monospace;
            font-size: 10px;
            color: #f0c040;
            letter-spacing: 3px;
        """)
        QTimer.singleShot(300, self.on_start)


# ──────────────────
#  FADER VERTICAL
# ──────────────────
class faderWidget(QWidget):
    def __init__(self, label, paramName, min_val=0, max_val=255, default=0, callback=None, parent=None):
        super().__init__(parent)
        self.callback = callback
        self.paramName = paramName

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Etiqueta del nombre
        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(STYLE_FADER_LABEL)
        lbl.setWordWrap(True)
        lbl.setFixedWidth(58)

        # Valor numérico
        self.lbl_val = QLabel(str(default))
        self.lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_val.setStyleSheet(STYLE_FADER_VALUE)

        # Slider vertical (arriba = max)
        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setRange(min_val, max_val)
        self.slider.setValue(default)
        self.slider.setFixedHeight(160)
        self.slider.setStyleSheet(STYLE_SLIDER_VERTICAL)
        self.slider.valueChanged.connect(self._on_change)

        layout.addWidget(lbl)
        layout.addWidget(self.slider, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.lbl_val)

    def _on_change(self, val):
        self.lbl_val.setText(str(val))
        if self.callback:
            self.callback(val)

    def value(self):
        return self.slider.value()

    def setValue(self, val):
        self.slider.setValue(val)


# ────────────────────
#  VENTANA PRINCIPAL
# ────────────────────
class ventanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LIA  ◈  Control Panel")
        self.setMinimumSize(1200, 680)
        self.setStyleSheet(STYLE_GLOBAL)

        self.thread = None
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.splash = pantallaInicio(self._lanzarApp)
        self.stack.addWidget(self.splash)

    # ── Lanza el hilo y muestra la UI principal ──
    def _lanzarApp(self):
        self.thread = controlSeguimiento()
        self.thread.change_pixmap_signal.connect(self._update_image)
        self.thread.start()
        self.thread.params['power'] = True

        self.main_widget = self._construirUI()
        self.stack.addWidget(self.main_widget)
        self.stack.setCurrentIndex(1)

    # ── Construye la UI principal ──
    def _construirUI(self):
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # — Barra superior —
        topbar = self._makeTopBar()
        root_layout.addWidget(topbar)

        # — Área central —
        center = QWidget()
        center_layout = QHBoxLayout(center)
        center_layout.setContentsMargins(10, 10, 10, 10)
        center_layout.setSpacing(10)

        # Video
        video_frame = QFrame()
        video_frame.setStyleSheet("background: #000; border: 1px solid #2a2d35; border-radius: 4px;")
        vf_layout = QVBoxLayout(video_frame)
        vf_layout.setContentsMargins(0, 0, 0, 0)
        self.video_label = QLabel("ESPERANDO SEÑAL DE CÁMARA")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("color: #2a2d35; font-size: 13px; letter-spacing: 3px; background: transparent; border: none;")
        vf_layout.addWidget(self.video_label)
        center_layout.addWidget(video_frame, stretch=5)

        # Faders + Tabs a la derecha
        right_panel = QVBoxLayout()
        right_panel.setSpacing(8)

        faders_frame = self._makeFadersPanel()
        right_panel.addWidget(faders_frame)

        self.tabs = QTabWidget()
        self._pestañaAjuste()
        self._pestañaConfig()
        right_panel.addWidget(self.tabs, stretch=1)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        center_layout.addWidget(right_widget, stretch=3)

        root_layout.addWidget(center)
        return root

    # ── Barra superior ──
    def _makeTopBar(self):
        bar = QFrame()
        bar.setFixedHeight(44)
        bar.setStyleSheet("background: #0a0b0d; border-bottom: 1px solid #1e2028;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)

        lbl = QLabel("◈  L I A   —   LIGHTING IA")
        lbl.setStyleSheet("color: #f0c040; font-size: 11px; letter-spacing: 4px; font-weight: bold;")

        self.lbl_estado = QLabel("● ACTIVO")
        self.lbl_estado.setStyleSheet("color: #40d060; font-size: 10px; letter-spacing: 2px;")

        btn_off = QPushButton("⏻  APAGAR")
        btn_off.setFixedHeight(28)
        btn_off.setStyleSheet(STYLE_BTN_DANGER)
        btn_off.clicked.connect(self._apagarSistema)

        layout.addWidget(lbl)
        layout.addStretch()
        layout.addWidget(self.lbl_estado)
        layout.addSpacing(20)
        layout.addWidget(btn_off)
        return bar

    # ── Panel de faders ──
    def _makeFadersPanel(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #0f1118;
                border: 1px solid #1e2028;
                border-radius: 4px;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        titulo = QLabel("— FADERS DMX —")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #3a4050; font-size: 9px; letter-spacing: 4px; border: none; background: transparent;")
        layout.addWidget(titulo)

        faders_row = QHBoxLayout()
        faders_row.setSpacing(2)
        faders_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        def sep():
            s = QFrame()
            s.setFrameShape(QFrame.Shape.VLine)
            s.setStyleSheet("color: #1e2028; background: #1e2028;")
            return s

        self.f_dimmer = faderWidget("DIMMER", "dimmer", 0, 255, self.thread.params['dimmer'],
            lambda v: self._set_param('dimmer', v))
        self.f_zoom   = faderWidget("ZOOM", "zoom", 0, 255, self.thread.params['zoom'],
            lambda v: self._set_param('zoom', v))
        self.f_focus  = faderWidget("FOCUS", "focus", 0, 255, self.thread.params['focus'],
            lambda v: self._set_param('focus', v))
        self.f_strobe = faderWidget("STROBE", "strobe", 0, 255, self.thread.params['strobe'],
            lambda v: self._set_param('strobe', v))
        self.f_gobo   = faderWidget("GOBO",   "gobo", 0, 255, self.thread.params['gobo'],
            lambda v: self._set_param('gobo', v))
        self.f_color  = faderWidget("COLOR",  "color", 0, 255, self.thread.params['color'],
            lambda v: self._set_param('color', v))
        self.f_frost  = faderWidget("FROST",  "frost",  0, 255, self.thread.params['frost'],
            lambda v: self._set_param('frost', v))

        for w in [self.f_dimmer, sep(), self.f_zoom, self.f_focus,
                  sep(), self.f_strobe, self.f_gobo,
                  sep(), self.f_color,
                  sep(), self.f_frost]:
            faders_row.addWidget(w)

        layout.addLayout(faders_row)
        return frame

    def _set_param(self, key, val):
        if self.thread:
            self.thread.params[key] = int(val)

    def _set_dmx_channel(self, key, val):
        if self.thread:
            # Guardamos override para canales extra
            if not hasattr(self.thread, 'fader_overrides'):
                self.thread.fader_overrides = {}
            self.thread.fader_overrides[key] = val

    # ── Pestaña de ajuste de seguimiento ──
    def _pestañaAjuste(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        form = QFormLayout()
        form.setSpacing(6)

        self.pan_offset   = QLineEdit(str(self.thread.params['pan_offset']))
        self.tilt_offset  = QLineEdit(str(self.thread.params['tilt_offset']))
        self.suavizado    = QLineEdit(str(self.thread.params['suavizado']))
        self.rango_pan    = QLineEdit(str(self.thread.params['rango_pan']))
        self.rango_tilt   = QLineEdit(str(self.thread.params['rango_tilt']))

        form.addRow("PAN OFFSET:", self.pan_offset)
        form.addRow("TILT OFFSET:", self.tilt_offset)
        form.addRow("SUAVIZADO (0.01–1.0):", self.suavizado)
        form.addRow("RANGO PAN (FOV):", self.rango_pan)
        form.addRow("RANGO TILT (FOV):", self.rango_tilt)

        btn_apply = QPushButton("ACTUALIZAR SEGUIMIENTO")
        btn_apply.setStyleSheet(STYLE_BTN_PRIMARY)
        btn_apply.clicked.connect(self._aplicarAjustes)

        layout.addLayout(form)
        layout.addWidget(btn_apply)
        layout.addStretch()
        self.tabs.addTab(tab, "SEGUIMIENTO")

    # ── Pestaña de configuración DMX ──
    def _pestañaConfig(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self.canal_pan       = QLineEdit(str(self.thread.dmx_Config['canal_pan']))
        self.canal_pan_fine  = QLineEdit(str(self.thread.dmx_Config['canal_pan_fine']))
        self.canal_tilt      = QLineEdit(str(self.thread.dmx_Config['canal_tilt']))
        self.canal_tilt_fine = QLineEdit(str(self.thread.dmx_Config['canal_tilt_fine']))
        self.canal_zoom      = QLineEdit(str(self.thread.dmx_Config['canal_zoom']))
        self.canal_focus     = QLineEdit(str(self.thread.dmx_Config['canal_focus']))
        self.canal_frost     = QLineEdit(str(self.thread.dmx_Config['canal_frost']))
        self.canal_gobo      = QLineEdit(str(self.thread.dmx_Config['canal_gobo']))
        self.canal_color     = QLineEdit(str(self.thread.dmx_Config['canal_color']))
        self.canal_dimmer    = QLineEdit(str(self.thread.dmx_Config['canal_dimmer']))
        self.universe        = QLineEdit(str(self.thread.dmx_Config['universe']))

        layout.addRow("CANAL PAN:", self.canal_pan)
        layout.addRow("CANAL PAN FINE:", self.canal_pan_fine)
        layout.addRow("CANAL TILT:", self.canal_tilt)
        layout.addRow("CANAL TILT FINE:", self.canal_tilt_fine)
        layout.addRow("CANAL ZOOM:", self.canal_zoom)
        layout.addRow("CANAL FOCUS:", self.canal_focus)
        layout.addRow("CANAL FROST:", self.canal_frost)
        layout.addRow("CANAL GOBO:", self.canal_gobo)
        layout.addRow("CANAL COLOR:", self.canal_color)
        layout.addRow("CANAL DIMMER:", self.canal_dimmer)
        layout.addRow("ART-NET UNIVERSE:", self.universe)

        btn_patch = QPushButton("GUARDAR PATCH DMX")
        btn_patch.setStyleSheet(STYLE_BTN_PRIMARY)
        btn_patch.clicked.connect(self._aplicarConfig)
        layout.addWidget(btn_patch)

        self.tabs.addTab(tab, "PATCH DMX")

    # ── Callbacks ──
    def _aplicarAjustes(self):
        try:
            self.thread.params['pan_offset']  = int(self.pan_offset.text())
            self.thread.params['tilt_offset'] = int(self.tilt_offset.text())
            self.thread.params['suavizado']   = float(self.suavizado.text())
            self.thread.params['rango_pan']   = float(self.rango_pan.text())
            self.thread.params['rango_tilt']  = float(self.rango_tilt.text())
        except ValueError:
            print("[LIA] Error: valores numéricos inválidos en ajuste de seguimiento.")

    def _aplicarConfig(self):
        try:
            self.thread.dmx_Config['canal_pan']       = int(self.canal_pan.text())
            self.thread.dmx_Config['canal_pan_fine']  = int(self.canal_pan_fine.text())
            self.thread.dmx_Config['canal_tilt']      = int(self.canal_tilt.text())
            self.thread.dmx_Config['canal_tilt_fine'] = int(self.canal_tilt_fine.text())
            self.thread.dmx_Config['canal_zoom']      = int(self.canal_zoom.text())
            self.thread.dmx_Config['canal_focus']     = int(self.canal_focus.text())
            self.thread.dmx_Config['canal_frost']     = int(self.canal_frost.text())
            self.thread.dmx_Config['canal_gobo']      = int(self.canal_gobo.text())
            self.thread.dmx_Config['canal_color']     = int(self.canal_color.text())
            self.thread.dmx_Config['canal_dimmer']    = int(self.canal_dimmer.text())
            self.thread.dmx_Config['universe']        = int(self.universe.text())
        except ValueError:
            print("[LIA] Error: valores numéricos inválidos en patch DMX.")

    def _update_image(self, cv_img):
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        scaled = qt_img.scaled(
            self.video_label.width(), self.video_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_label.setPixmap(QPixmap.fromImage(scaled))

    def _apagarSistema(self):
        if self.thread:
            self.thread.params['power'] = False
            self.thread.params['dimmer'] = 0
            self.thread.stop()
        QApplication.instance().quit()


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ventanaPrincipal()
    window.show()
    sys.exit(app.exec())
