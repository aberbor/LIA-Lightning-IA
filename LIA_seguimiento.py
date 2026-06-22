import cv2
import array
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from ultralytics import YOLO
from ola.ClientWrapper import ClientWrapper

class controlSeguimiento(QThread):

    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()

        # Parámetros ajustables de seguimiento
        self.params = {
            'pan_offset': 43, 'tilt_offset': 36,
            'rango_pan': 0.15, 'rango_tilt': 0.2,
            'suavizado': 1.0, 'curvatura_pan': 1.0,
            'pan_max': 255, 'pan_min': 0,
            'tilt_max': 255, 'tilt_min': 0,
            'zoom': 128, 'focus': 128, 'strobe': 0, 'prisma': 0,
            'gobo': 0, 'color': 0, 'iris': 0, 'frost': 0,
            'dimmer': 255, 'power': True
        }

        # Parametros de configuración DMX
        self.dmx_Config = {
            'canal_pan': 0, 'canal_pan_fine': 1,
            'canal_tilt': 2, 'canal_tilt_fine': 3,
            'canal_color': 6, 'canal_gobo': 9, 'canal_prisma': 13,
            'canal_frost': 15, 'canal_zoom': 16, 'canal_focus': 18,
            'canal_strobe': 21, 'canal_dimmer': 22,
            'universe': 0
        }

        self.cam_Config = {
            'resol_x': 640, 'resol_y': 640
        }

        # Historial para suavizado
        self.LAST_PAN = self.params['pan_offset'] 
        self.LAST_TILT = self.params['tilt_offset']
        self.running = True

    def run(self):
        
        model = YOLO('yolov11n.pt')
        cap = cv2.VideoCapture(0)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_Config['resol_x'])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_Config['resol_y'])
        
        wrapper = ClientWrapper()
        client = wrapper.Client()

        dmx_data = array.array('B', [0] * 512)

        while self.running:

            success, frame = cap.read()
            if not success:
                break

            results = model(frame, classes=0, verbose=False)

            if len(results[0].boxes) > 0 and self.params['power']:

                box = results[0].boxes[0]
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)

                pan_normal, pan_fine, tilt_normal, tilt_fine = self.calcularDMX(cx, cy)
                
                self.asignacionDMX(pan_normal, pan_fine, tilt_normal, tilt_fine, dmx_data)

                # Dibujo estético
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

            if not self.params['power']:
                dmx_data[self.dmx_Config['canal_dimmer']] = 0 

            client.SendDmx(self.dmx_Config['universe'], dmx_data)
            self.change_pixmap_signal.emit(frame)

        if cap.isOpened():
            cap.release()

    def calcularDMX(self, cx, cy):  
    
        # Mapeo a DMX (0-255)
        
        #convertimos a 8 bits haciendo una regla de 3
        relativa_x = (cx / self.cam_Config['resol_x']) - 0.5                           
        relativa_y = (cy / self.cam_Config['resol_y']) - 0.5

        #Aplicamos curvatura al pan
        relativa_x = self.aplicarCurvatura(relativa_x)

        #Aplicamos rango y offset
        pan_float, tilt_float = self.aplicarRangoOffset(relativa_x, relativa_y)
        
        #Aplicamos suavizado
        pan_float, tilt_float = self.aplicarSuavizado(pan_float, tilt_float)

        #Cogemos la parte entera para el pan normal y tilt normal, y la parte decimal para el fine
        pan_normal = int(pan_float)                                 
        tilt_normal = int(tilt_float)

        #Pasamos la parte decimal a 16 bits para el fine
        pan_fine = int((pan_float - pan_normal) * 255)               
        tilt_fine = int((tilt_float - tilt_normal) * 255)

        return pan_normal, pan_fine, tilt_normal, tilt_fine

    def aplicarCurvatura(self, relativa_x):

        # Aplicamos una función de curvatura
        return (abs(relativa_x) ** self.params['curvatura_pan']) * (1 if relativa_x >= 0 else -1)

    def aplicarRangoOffset(self, relativa_x, relativa_y):
        
        pan_float = relativa_x * self.params['rango_pan'] * 255 + self.params['pan_offset']       
        tilt_float = relativa_y * self.params['rango_tilt'] * 255 + self.params['tilt_offset']

        return pan_float, tilt_float

    def aplicarSuavizado(self, pan_float, tilt_float):

        pan_float = self.LAST_PAN + (pan_float - self.LAST_PAN) * self.params['suavizado']
        tilt_float = self.LAST_TILT + (tilt_float - self.LAST_TILT) * self.params['suavizado']

        self.LAST_PAN = pan_float
        self.LAST_TILT = tilt_float

        return pan_float, tilt_float

    def asignacionDMX(self, pan_normal, pan_fine, tilt_normal, tilt_fine, dmx_data):
        
        # Asignación de canales
        dmx_data[self.dmx_Config['canal_pan']] = max(self.params['pan_min'], min(self.params['pan_max'], pan_normal))           # Canal 1: PAN
        dmx_data[self.dmx_Config['canal_pan_fine']] = pan_fine                                                                  # Canal 2: PAN FINE
        dmx_data[self.dmx_Config['canal_tilt']] = max(self.params['tilt_min'], min(self.params['tilt_max'], tilt_normal))       # Canal 3: TILT
        dmx_data[self.dmx_Config['canal_tilt_fine']] = tilt_fine                                                                # Canal 4: TILT FINE
        dmx_data[self.dmx_Config['canal_color']] = self.params['color']                                                         # Canal 6: COLOR
        dmx_data[self.dmx_Config['canal_gobo']] = self.params['gobo']                                                           # Canal 9: GOBO
        dmx_data[self.dmx_Config['canal_prisma']] = self.params['prisma']                                                       # Canal 13: PRISMA
        dmx_data[self.dmx_Config['canal_frost']] = self.params['frost']                                                         # Canal 15: FROST
        dmx_data[self.dmx_Config['canal_zoom']] = self.params['zoom']                                                           # Canal 16: ZOOM
        dmx_data[self.dmx_Config['canal_focus']] = self.params['focus']                                                         # Canal 17: FOCUS
        dmx_data[self.dmx_Config['canal_strobe']] = self.params['strobe']                                                      # Canal 18: IRIS
        dmx_data[self.dmx_Config['canal_dimmer']] = self.params['dimmer']                                                       # Canal 22: DIMMER
    
    def stop(self):
        self.running = False
