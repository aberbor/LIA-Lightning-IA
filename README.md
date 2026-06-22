# LIA: Lightning IA ⚡🧠

### Sistema Inteligente de Seguimiento Visual para Iluminación Escénica basado en IA

**LIA (Lightning IA)** es una solución de software que democratiza el seguimiento automatizado de artistas en eventos en vivo. El sistema sustituye las costosas infraestructuras de tracking propietario (basadas en radiofrecuencia o hardware dedicado) por un algoritmo inteligente de visión artificial capaz de procesar vídeo estándar y comandar de forma autónoma cabezas móviles mediante el protocolo estándar **Art-Net/DMX512**.

Este proyecto ha sido desarrollado como Trabajo de Fin de Grado en la **Escuela Politécnica Superior de la Universidad Pablo de Olavide (Sevilla)**, obteniendo una calificación de **9/10**.

---

## 🚀 Características Principales

* **Visión Artificial en Tiempo Real:** Inferencia ultrarrápida mediante el modelo **YOLOv11** (versión Nano) optimizado para la detección y localización de figuras humanas a más de 30 FPS.
* **Arquitectura Concurrente Multihilo:** Desarrollado con **PyQt6**, aislando por completo el hilo de la interfaz de usuario (*GUI Thread*) del bucle crítico de procesamiento y envío de datos (*Worker Thread*) para garantizar un rendimiento fluido y libre de bloqueos.
* **Pipeline Matemático de Precisión (16 bits):** Conversión analógica-digital de coordenadas mediante algoritmos propios de normalización y escalado para aprovechar la precisión de motores paso a paso de alta resolución (*Pan/Tilt Fine*).
* **Amortiguación Digital (Filtro LERP):** Implementación de un filtro de interpolación lineal que elimina el *jitter* (parpadeo o temblor milimétrico de la IA), otorgando al haz de luz una inercia física de aspecto completamente orgánico y humano.
* **Consola de Control Creativo:** Interfaz gráfica avanzada en modo oscuro con un monitor de vídeo integrado y un rack de faders virtuales para alterar en vivo parámetros como *Dimmer, Zoom, Focus, Strobe, Gobos y Color*.

---

## 🛠️ Arquitectura del Sistema y Topología

El flujo de información opera de manera lineal y asíncrona:
1. **Captura:** Una cámara web estándar adquiere la imagen del escenario mediante **OpenCV**.
2. **Procesamiento:** El núcleo de LIA calcula el centroide del artista, aplica correcciones de curvatura óptica, ajusta rangos/offsets y suaviza la trayectoria.
3. **Transmisión:** Los valores DMX calculados y los faders creativos se empaquetan en un array de 512 canales.
4. **Red:** Los datos se transmiten mediante paquetes UDP bajo el protocolo **Art-Net** hacia un nodo físico de conversión de red (ej. *Botex NETcon 8-3*).
5. **Acción:** La cabeza móvil (ej. *Mark Beam 350*) ejecuta los movimientos y efectos sobre el escenario en tiempo real (latencia total < 65 ms).

---

## 📋 Prerrequisitos e Instalación

El entorno de control de este software está diseñado para ejecutarse de forma nativa sobre arquitecturas **Linux (POSIX)**.

### Dependencia Externa del Sistema (Esencial)
Este software interactúa a bajo nivel con la red de iluminación a través del ecosistema open-source **Open Lighting Architecture (OLA)**. 
* *Nota:* Para no duplicar repositorios, el código fuente de OLA no está incluido aquí. Debes instalar y configurar el demonio `olad` en tu sistema siguiendo las instrucciones oficiales de su repositorio: [OpenLightingProject/ola](https://github.com/OpenLightingProject/ola).

### Clonar el repositorio y dependencias de Python
1. Instala OLA en tu sistema operativo y asegúrate de que el servidor local está activo (`olad -l 3`).
2. Clona este repositorio:
   ```bash
   git clone [https://github.com/tu-usuario/LIA-Lightning-IA.git](https://github.com/tu-usuario/LIA-Lightning-IA.git)
   cd LIA-Lightning-IA
