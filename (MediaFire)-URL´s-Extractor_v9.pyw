
#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
'''
================================================================================
Desarrollador: Cristian M. Veliz Cano
Nombre del Software: "MediaFire URL Extractor & Downloader"
Versión: v_09 [Final Fixed]
Distribución: Gratuita / Open Source

Descripción:
Aplicación de escritorio desarrollada en Python con interfaz gráfica (PyQt5)
que permite extraer automáticamente URLs de descarga directa desde carpetas
de MediaFire y gestionar descargas múltiples en paralelo de forma eficiente.

El sistema combina scraping web, consumo de API y procesamiento concurrente
para ofrecer una experiencia rápida, moderna y estable.

--------------------------------------------------------------------------------
⚙️ Características principales:

• Extracción automática de URLs desde carpetas de MediaFire
• Extracción automática de URLs Individuales
• Uso de la API oficial de MediaFire para obtener enlaces reales
• Descarga de múltiples archivos en paralelo (multithreading)
• Control dinámico de hilos (descargas simultáneas configurables)
• Visualización de progreso en tiempo real (QProgressBar)
• Medición de velocidad de descarga (KB/s en vivo)
• Interfaz gráfica moderna (Dark UI estilo profesional)
• Cancelación de descargas en ejecución
• Manejo de errores robusto y validación de conexión a internet

--------------------------------------------------------------------------------
🧠 Tecnologías utilizadas:

• Python 3.x
• PyQt5 (Interfaz gráfica)
• Requests (Peticiones HTTP)
• BeautifulSoup (Parsing HTML / Scraping)
• ThreadPoolExecutor (Concurrencia)
• QThread + Signals (Arquitectura asíncrona GUI)

--------------------------------------------------------------------------------
🚀 Funcionamiento general:

1. El usuario ingresa una URL de carpeta de MediaFire
2. O bien URL´s, ya sea una o Varias, que no se encuentran dentro de alguna Carpeta
3. El sistema extrae el "folder_key", O Analisa, la(s), URL(s), Unica(s)
4. Se consulta la API de MediaFire para obtener archivos
5. Se generan URLs de descarga directa
6. El usuario inicia descargas múltiples
7. Se ejecutan hilos paralelos para cada archivo
8. Se muestra progreso (%) y velocidad (KB/s) en tiempo real

--------------------------------------------------------------------------------
💡 Puntos destacados (Portfolio Boost):

✔ Arquitectura desacoplada (GUI + Worker Threads)
✔ Uso correcto de señales en PyQt (Thread-safe)
✔ Optimización mediante concurrencia
✔ UI/UX moderna inspirada en herramientas reales
✔ Manejo de red + scraping + API en un solo proyecto
✔ Escalable (fácil agregar nuevas fuentes o servidores)

--------------------------------------------------------------------------------
📌 Notas:

Este proyecto está orientado a demostrar habilidades en:
- Desarrollo de software de escritorio
- Automatización de descargas
- Manejo de concurrencia
- Diseño de interfaces modernas

================================================================================
'''

import sys, os
import requests
from bs4 import BeautifulSoup
import re
import json
##================================================================================
## Librerias, de PyQt5
##================================================================================
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QShortcut, QHBoxLayout, QVBoxLayout, QTextEdit, QDialog,
    QPushButton, QMessageBox, QSpacerItem, QSizePolicy, QProgressBar, QFileDialog, QSpinBox
)
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from concurrent.futures import ThreadPoolExecutor, as_completed
##================================================================================
'''
Los Header, para Burlar y aparentar, ser un Navegador, Genuino
En estos ejemplos, el User-Agent se ajusta para reflejar el navegador deseado, 
mientras que los otros headers se mantienen similares a los de un navegador real 
para mantener la coherencia con las solicitudes HTTP estándar.
Para el Caso se estara simulando un navegador real (Chrome en Windows)
'''
##================================================================================
# Headers simulando un navegador real (Chrome en Windows)
HEADERSC = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

# Headers para Firefox (Windows)
HEADERSF = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

# Headers para Safari (MacOS)
HEADERSM = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

# Headers para Edge (Windows)
HEADERSE = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

# Headers para Opera (Windows)
HEADERSO = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 OPR/102.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

##================================================================================
## Clase Para Colocar todos los Assets, que se Vallan a Utilizar para el PyIntaller
##================================================================================
class Path():
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def resource_path_app():
        try:
            path_app = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
        except Exception as e:
            print(e)
        except IOError as error:
            print(error)
        return path_app

def is_online(timeout=2):
    test_urls = [
        "https://www.google.com/generate_204",
        "https://web.telegram.org",
        "https://1.1.1.1",
    ]
    for url in test_urls:
        try:
            requests.get(url, timeout=timeout)
            return True
        except: continue
    return False
##================================================================================
## Clase del Paralelismo, entre las descargas, y la busqueda de las URL´s, Reales
##================================================================================
class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    speed = pyqtSignal(float)  # KB/s
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, urls, folder, max_threads, parent=None):
        super().__init__(parent)
        self.urls = urls
        self.folder = folder
        self.max_threads = max_threads
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        total = len(self.urls)
        completed = 0

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [executor.submit(self.download_single_file, url) for url in self.urls]

            for future in as_completed(futures):
                if not self._is_running:
                    break

                try:
                    future.result()
                except Exception as e:
                    self.error.emit(str(e))

                completed += 1
                progress = int(completed / total * 100)
                self.progress.emit(progress)

        self.finished.emit()

    def download_single_file(self, url):
        import time

        if not self._is_running:
            return

        response = requests.get(url, headers=HEADERSC)
        soup = BeautifulSoup(response.text, "html.parser")
        download_btn = soup.find("a", {"id": "downloadButton"})

        if not download_btn:
            raise Exception("No se encontró botón descarga")
            self.error.emit("No se encontró botón descarga")

        real_url = download_btn.get("href")

        r = requests.get(real_url, stream=True, headers=HEADERSC)

        if r.status_code != 200:
            raise Exception("Error descargando archivo")
            self.error.emit("Error descargando archivo")

        filename = real_url.split("/")[-1].split("?")[0]
        filepath = os.path.join(self.folder, filename)

        total_size = int(r.headers.get('content-length', 0))
        downloaded = 0
        start_time = time.time()

        with open(filepath, "wb") as f:
            for chunk in r.iter_content(8192):
                if not self._is_running:
                    return

                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    elapsed = time.time() - start_time
                    if elapsed > 0:
                        speed_kb = (downloaded / 1024) / elapsed
                        self.speed.emit(speed_kb)
##================================================================================
## Classe Principal
##================================================================================
class MediaFireURLExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MediaFire URL Extractor v9 (Final Fix)")
        self.resize(850, 650)

        # Variable para guardar el valor seleccionado
        self.selected_value = 4

        # Intentar cargar icono, si falla no importa
        try:
            self.Ico_app = Path.resource_path('Ico\\1.Ico')
            self.setWindowIcon(QIcon(self.Ico_app))
        except:
            pass

        # 🔥 ESTILO MODERNO (Mismo que tu ejemplo)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                font-size: 16px;
                color: #bbbbbb;
            }
            QTextEdit {
                background-color: #2e2e2e;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                selection-background-color: #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005f9e;
            }
            QPushButton:pressed {
                background-color: #004a7a;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Título
        title_label = QLabel("MediaFire URL Extractor v9")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #007acc;
            background: linear-gradient(to right, #007acc, #005f9e);
            padding: 15px;
            border-bottom: 2px solid #005f9e;
        """)
        layout.addWidget(title_label)

        layout.addSpacing(10)

        self.label = QLabel(" Pega la URL de la carpeta de MediaFire.\n O URL(s), Independientes:")
        layout.addWidget(self.label)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Ej: https://www.mediafire.com/folder/...\n\nO:\nEj #1: https://www.mediafire.com/file/...\nEj #2: https://www.mediafire.com/file/...\nEj #3: Etc...")
        layout.addWidget(self.input_text)

        button_layout = QHBoxLayout()
        self.extract_button = QPushButton("Extraer URLs")
        self.extract_button.clicked.connect(self.extract_urls)
        button_layout.addWidget(self.extract_button)

        layout.addSpacing(3)

        self.clear_input_btn = QPushButton("Limpiar Entrada")
        self.clear_input_btn.clicked.connect(self.clear_input)
        button_layout.addWidget(self.clear_input_btn)
        self.clear_input_btn.hide()

        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addLayout(button_layout)

        layout.addSpacing(3)

        self.output_label = QLabel("URLs Individuales (Descarga Directa):")
        layout.addWidget(self.output_label)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Las URLs extraídas aparecerán aquí...")
        layout.addWidget(self.output_text)

        # Botón Limpiar|descargar
        clear_output_layout = QHBoxLayout()

        self.clear_output_btn = QPushButton("Limpiar Salida")
        self.clear_output_btn.clicked.connect(self.clear_output)
        clear_output_layout.addWidget(self.clear_output_btn)

        self.download_button = QPushButton()
        self.download_button.setToolTip('Download File')
        self.download_button.setFixedSize(20, 20)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; /* Verde */
                border-radius: 10px; /* Redondito */
                border: none;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219150;
            }
        """)
        self.download_button.clicked.connect(self.download_panel)
        clear_output_layout.addItem(QSpacerItem(40, 50, QSizePolicy.Expanding, QSizePolicy.Minimum))
        clear_output_layout.addWidget(self.download_button)
        
        layout.addSpacing(3)
        layout.addLayout(clear_output_layout)

        self.setLayout(layout)
        self.center_on_screen()

        # Atajo Ctrl + Q Limpia, los Cuadros, de URL´s
        info_software = QShortcut(QKeySequence('Ctrl+Q'), self)
        info_software.activated.connect(self.clear_hall)

        # Atajo Ctrl + I para mostrar información del software
        info_software = QShortcut(QKeySequence('Ctrl+I'), self)
        info_software.activated.connect(self.show_app_info)

        self.show_app_info()

##================================================================================
##================================================================================        

    ## Metodo Mostrar la Info, del Soft, en una Ventanita Emergente, enforma de Dialogo
    def show_app_info(self):
        dialog_i = app_info(self)
        dialog_i.exec_()

    ## Metodo Para ir a el Panel de Control de Descargas de Archivos...
    def download_panel(self):
        dialog_i = panel_download(self.selected_value, self)
        dialog_i.exec_()

        # 🔥 Recuperar valor actualizado al cerrar
        self.selected_value = dialog_i.selected_value
        print(self.selected_value)

##================================================================================
##================================================================================

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            sys.exit()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = 850, 650
        x = (screen.width() - w) // 2
        y = (screen.height() - h) // 2 + 10
        self.setGeometry(x, y, w, h)

    def check_internet_status(self):
        if is_online():
            print("✔ Internet disponible")
            return "OK"
        else:
            print("✖ Sin conexión a Internet")
            QMessageBox.critical(self, "Error", "✖ No Cuentas Con conexión a Internet.\n-> Revisa tu conexión y vuelve a intentarlo.")
            return "X"

    def extract_urls(self):

        signal = self.check_internet_status()

        if signal == "OK":
            folder_url = self.input_text.toPlainText().strip()
            if not folder_url:
                QMessageBox.warning(self, 'Advertencia', 'Por favor, ingresa una URL válida.')
                return

            # Limpiar la URL de fragmentos (#...) si los tiene
            if '#' in folder_url:
                folder_url = folder_url.split('#')[0]

            try:
                urls = self.get_individual_urls(folder_url)
                if urls:
                    self.output_text.setText("\n".join(urls))
                    QMessageBox.information(self, "Éxito", f"Se extrajeron {len(urls)} URLs.")
                else:
                    QMessageBox.warning(self, 'Advertencia', 'No se encontraron URLs en la carpeta especificada.')
            except Exception as e:

                message = QMessageBox.critical(self, 'Error', f'Ocurrió un error: {e}')
                
                if message == QMessageBox.Ok:

                    url_path = self.input_text.toPlainText().strip().split("\n")                    
                    MediaFireURLExtractor.Chec_URL_Unic(self, url_path)

        elif signal == "X":
            pass

    def Chec_URL_Unic(self, url_path):

        try:

            ulr_ok = []
            cont = 0

            for i in url_path:

                if "https://www.mediafire.com/file/" in i:

                    url = f"{i}"

                    # Obtener la posición de la última ocurrencia de '/file'
                    position = url.rfind("/file")

                    # Verificar si la posición es igual a la longitud de la URL menos 5 (longitud de '/file')
                    if position == len(url) - 5:

                        cont += 1
                        ulr_ok.append(i)

                    else:
                        continue

            if cont == 0:
                pass

            else:

                message_ok = QMessageBox.information(self, "información", f"Se Detecta que la(´s) {cont} URL(´s)\nEs (´son) una URL, Valida.\nDeseas Descargala de todos Modos?.")
                if message_ok == QMessageBox.Ok:

                    self.output_text.clear()

                    for i in ulr_ok:
                        self.output_text.append(i)

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Ocurrió un error: {e}')

    def get_individual_urls(self, folder_url):
        # Extraer folder_key desde la URL
        match = re.search(r'/folder/([^/]+)', folder_url)
        if not match:
            raise Exception("No se pudo extraer el folder_key")

        folder_key = match.group(1)

        api_url = "https://www.mediafire.com/api/1.5/folder/get_content.php"

        params = {
            "content_type": "files",
            "filter": "all",
            "order_by": "name",
            "order_direction": "asc",
            "chunk": 1,
            "response_format": "json",
            "folder_key": folder_key
        }

        response = requests.get(api_url, params=params, headers=HEADERSC)

        if response.status_code != 200:
            raise Exception(f"Error API: {response.status_code}")

        data = response.json()

        files = data["response"]["folder_content"]["files"]

        urls = []
        for f in files:
            urls.append(f["links"]["normal_download"])

        return urls

    def clear_input(self):
        self.input_text.clear()

    def clear_output(self):
        self.output_text.clear()

    def clear_hall(self):
        self.input_text.clear()
        self.output_text.clear()

##================================================================================
## Panel de Control en Descargas de los Archivos
##================================================================================
class panel_download(QDialog):
    
    def __init__(self, selected_value, parent=None):
        super().__init__(parent)

        self.selected_value = selected_value

        self.setWindowTitle("MediaFire URL Extractor v9")
        self.setFixedSize(540, 200)

        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowCloseButtonHint
        )

        self.setModal(True)

        self.init_ui()
        self.apply_style()

    # =========================
    # UI
    # =========================
    def init_ui(self):

        layout = QVBoxLayout(self)
        lbl_spin_layout = QHBoxLayout()
        lbl_spin_layout.setContentsMargins(0, 0, 0, 0)
        lbl_spin_layout.setSpacing(0)

        # Título
        title = QLabel("MediaFire URL Extractor v9")
        title.setFixedHeight(40)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00c3ff;")

        layout.addWidget(title)
        layout.addSpacing(3)

        # 🔢 SpinBox para cantidad de archivos
        spin_label = QLabel("Cantidad de Archivos a Descargar, en Simultaneo?")
        spin_label.setFixedHeight(31)
        spin_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        spin_label.setStyleSheet("font-size: 14px; color: #ffffff;")
        lbl_spin_layout.addWidget(spin_label)

        space_label = QPushButton()
        lbl_spin_layout.addItem(QSpacerItem(40, 50, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.spin_count = QSpinBox()
        self.spin_count.setRange(1, 100)
        self.spin_count.setValue(self.selected_value)
        self.spin_count.setStyleSheet("""
            QSpinBox {
                background-color: #1e1e2f;
                color: white;
                padding: 5px;
                border-radius: 5px;
                font-size: 14px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background-color: #1f1f2e;
                border: none;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #00c3ff;
            }
        """)
        lbl_spin_layout.addWidget(self.spin_count, alignment=Qt.AlignCenter)
        layout.addLayout(lbl_spin_layout)
        layout.addSpacing(5)

        # Conectar la señal valueChanged para actualizar la variable
        self.spin_count.valueChanged.connect(self.update_selected_value)

        # 🔥 ProgressBar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00c3ff;
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        layout.addSpacing(3)

        # ⚡ Label velocidad
        self.speed_label = QLabel("Velocidad: 0 KB/s")
        self.speed_label.setFixedHeight(31)
        self.speed_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.speed_label)

        # 🔘 Botón (Solo esfera verde, sin texto)
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)

        self.download_btn = QPushButton("Download")
        self.download_btn.setFixedSize(130, 36)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; /* Verde */
                border-radius: 8px; /* Redondito */
                border: none;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219150;
            }
        """)
        self.download_btn.clicked.connect(self.start_download)

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setFixedSize(130, 36)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_download)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.download_btn)

        layout.addLayout(btn_layout)

    # =========================
    # Estilo
    # =========================
    def apply_style(self):
        self.setStyleSheet("""
            QDialog {
                background: #121212;
            }
            QLabel {
                color: white;
            }
            QTextEdit {
                background: #1e1e2f;
                color: #f1f1f1;
                border-radius: 8px;
                padding: 10px;
                font-size: 11pt;
            }
            QPushButton {
                background: #1f1f2e;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #00c3ff;
                color: black;
            }
        """)

    # Método para actualizar la variable con el valor seleccionado
    def update_selected_value(self, value):

        self.selected_value = value
        print(f"Valor seleccionado: {self.selected_value}")  # Para verificar en la consola

    def start_download(self):

        self.selected_value = self.spin_count.value()
        self.download_btn.setEnabled(False)

        self.progress_bar.show()
        parent = self.parent()

        if not parent:
            return

        urls = parent.output_text.toPlainText().strip().split("\n")

        if not urls or urls == ['']:
            QMessageBox.warning(self, "Error", "No hay URLs para descargar.")
            self.download_btn.setEnabled(True)
            self.progress_bar.hide()
            return

        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de descarga")

        if not folder:
            self.download_btn.setEnabled(True)
            self.progress_bar.hide()
            return

        # 🔥 Crear worker con threads dinámicos
        self.worker = DownloadWorker(urls, folder, self.selected_value)

        # 🔗 Conectar señales al dialog
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.download_finished)
        self.worker.error.connect(self.show_error)
        self.worker.speed.connect(self.update_speed)

        self.cancel_btn.setEnabled(True)

        # 🚀 Ejecutar
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def show_error(self, msg):
        print("Error:", msg)
        self.download_btn.setEnabled(True)
        self.progress_bar.hide()

    def download_finished(self):
        QMessageBox.information(self, "Completado", "Descarga finalizada.")
        self.progress_bar.setValue(100)

        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.speed_label.setText("Velocidad: 0 KB/s")

        self.progress_bar.setValue(0)
        self.progress_bar.hide()

    def update_speed(self, speed):
        self.speed_label.setText(f"Velocidad: {speed:.2f} KB/s")

    def cancel_download(self):
        if hasattr(self, 'worker'):
            self.worker.stop()
            self.cancel_btn.setEnabled(False)
            self.download_btn.setEnabled(True)
            self.speed_label.setText("Cancelado")
##================================================================================
## Información del Software
##================================================================================
class app_info(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("MediaFire URL Extractor & Downloader v_09")
        self.setFixedSize(540, 430)

        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowCloseButtonHint
        )

        self.setModal(True)

        self.init_ui()
        self.apply_style()


    # =========================
    # UI
    # =========================
    def init_ui(self):

        layout = QVBoxLayout(self)

        # 🎧 Título
        title = QLabel("MediaFire URL Extractor & Downloader")
        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)


        # 📜 Texto informativo
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)

        self.info_text.setText(
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Desarrollador: Cristian M. Veliz Cano
Nombre del Software: "MediaFire URL Extractor & Downloader"
Versión: v_09 [Final Fixed]
Distribución: Gratuita / Open Source

Descripción:
Aplicación de escritorio desarrollada en Python con interfaz gráfica 
(PyQt5) que permite extraer automáticamente URLs de descarga 
directa  desde  carpetas de MediaFire y gestionar descargas múltiples 
en paralelo de forma eficiente.

El sistema combina scraping web, consumo de API y procesamiento 
concurrente para ofrecer una experiencia rápida, moderna y estable.

-----------------------------------------------------------------------------
⚙️ Características principales:

• Extracción automática de URLs desde carpetas de MediaFire
• Extracción automática de URLs Individuales
• Uso de la API oficial de MediaFire para obtener enlaces reales
• Descarga de múltiples archivos en paralelo (multithreading)
• Control dinámico de hilos (descargas simultáneas configurables)
• Visualización de progreso en tiempo real (QProgressBar)
• Medición de velocidad de descarga (KB/s en vivo)
• Interfaz gráfica moderna (Dark UI estilo profesional)
• Cancelación de descargas en ejecución
• Manejo de errores robusto y validación de conexión a internet

-----------------------------------------------------------------------------
🧠 Tecnologías utilizadas:

• Python 3.x
• PyQt5 (Interfaz gráfica)
• Requests (Peticiones HTTP)
• BeautifulSoup (Parsing HTML / Scraping)
• ThreadPoolExecutor (Concurrencia)
• QThread + Signals (Arquitectura asíncrona GUI)

-----------------------------------------------------------------------------
🚀 Funcionamiento general:

1. El usuario ingresa una URL de carpeta de MediaFire
2. O bien URL´s, ya sea una o Varias, que no se encuentran dentro de alguna Carpeta
3. El sistema extrae el "folder_key", O Analisa, la(s), URL(s), Unica(s)
4. Se consulta la API de MediaFire para obtener archivos
5. Se generan URLs de descarga directa
6. El usuario inicia descargas múltiples
7. Se ejecutan hilos paralelos para cada archivo
8. Se muestra progreso (%) y velocidad (KB/s) en tiempo real

-----------------------------------------------------------------------------
💡 Puntos destacados (Portfolio Boost):

✔ Arquitectura desacoplada (GUI + Worker Threads)
✔ Uso correcto de señales en PyQt (Thread-safe)
✔ Optimización mediante concurrencia
✔ UI/UX moderna inspirada en herramientas reales
✔ Manejo de red + scraping + API en un solo proyecto
✔ Escalable (fácil agregar nuevas fuentes o servidores)

-----------------------------------------------------------------------------
📌 Notas:

Este proyecto está orientado a demostrar habilidades en:
- Desarrollo de software de escritorio
- Automatización de descargas
- Manejo de concurrencia
- Diseño de interfaces modernas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Atajo del teclado:
Ctrl + I  → Abrir esta ventana
Ctrl + Q  → Limpia, los Cuadros, de URL´s
ESC  → Cierra el Soft
"""
        )

        layout.addWidget(self.info_text)


        # 🔘 Botón
        btn_layout = QHBoxLayout()

        close_btn = QPushButton("Cerrar")
        close_btn.setFixedHeight(36)

        close_btn.clicked.connect(self.close)

        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)


    # =========================
    # Estilo
    # =========================
    def apply_style(self):

        self.setStyleSheet("""

        QDialog {
            background:#121212;
        }

        QLabel {
            color:white;
        }

        QLabel:first {
            font-size:20px;
            font-weight:bold;
            color:#00c3ff;
        }

        QTextEdit {
            background:#1e1e2f;
            color:#f1f1f1;
            border-radius:8px;
            padding:10px;
            font-size:11pt;
        }

        QPushButton {
            background:#1f1f2e;
            color:white;
            border-radius:10px;
            padding:8px;
            font-size:14px;
        }

        QPushButton:hover {
            background:#00c3ff;
            color:black;
        }

        """)
##================================================================================
## Parte Final e Innicio...
##================================================================================
if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MediaFireURLExtractor()
    window.show()
    sys.exit(app.exec_())
##================================================================================