
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QDialog, QFileDialog,QMessageBox
from PyQt5.uic import loadUi
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pydicom
import os
import numpy as np
import math

class Eje_sagital(FigureCanvas):
    def __init__(self, parent, archivo, carpeta, numero):
        super().__init__(Figure())
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)
        self.numero_imagen= numero

        # Llama al método para mostrar la imagen en el widget
        self.mostrar_en_qt(archivo, carpeta)
        
    def mostrar_en_qt(self, archivo_dicom, carpeta):
        # Convierte el archivo DICOM a QImage
        slices = [pydicom.dcmread(carpeta + '/' + s) for s in os.listdir(carpeta)]
        slices.sort(key = lambda x: int(x.ImagePositionPatient[0]))
        volumen = np.stack([s.pixel_array for s in slices])
        volumen = volumen.astype(np.int16)
        self.ax.imshow(volumen[self.numero_imagen-1,:,:],cmap="gray", aspect='auto') 
        self.ax.axis('off')
        self.ax.set_position([0, 0, 1, 1])  # Configura el objeto Axes para ocupar todo el espacio
        self.draw()

class Eje_coronal(FigureCanvas):
    def __init__(self, parent, archivo, carpeta,numero):
        super().__init__(Figure())
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)
        self.numero_imagen= numero
        
        # Llama al método para mostrar la imagen en el widget
        self.mostrar_en_qt(archivo, carpeta)
        
    def mostrar_en_qt(self, archivo_dicom, carpeta):
        # Convierte el archivo DICOM a QImage
        slices = [pydicom.dcmread(carpeta + '/' + s) for s in os.listdir(carpeta)]
        slices.sort(key = lambda x: int(x.ImagePositionPatient[0]))
        #HALLAMOS UN APROXIMADO DE LA PROPORCION DE CADA EJE PARA USAR EL SLIDER
        pixel_spacing=slices[0].PixelSpacing
        slice_thickness=slices[0].SliceThickness
        proporcion_filas = float(slice_thickness)/ float(pixel_spacing[1])
        proporcion_columnas =float(slice_thickness)/ float(pixel_spacing[0])
        proporciones=(proporcion_filas,proporcion_columnas)
        valores = tuple(int(math.floor(coord)) for coord in proporciones) #Los valores hallados se usan para la posicion del eje
        volumen = np.stack([s.pixel_array for s in slices])
        volumen = volumen.astype(np.int16)
        valor=(self.numero_imagen-1)*valores[0]
        self.ax.imshow(volumen[:,:,valor], cmap="gray",aspect="auto")  
        self.ax.axis('off')
        self.ax.set_position([0, 0, 1, 1])  # Configura el objeto Axes para ocupar todo el espacio
        self.draw()

class Eje_axial(FigureCanvas):
    def __init__(self, parent, archivo, carpeta,numero):
        super().__init__(Figure())
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)
        self.numero_imagen= numero
        self.mostrar_en_qt(archivo, carpeta)
        
    def mostrar_en_qt(self, archivo_dicom, carpeta): 
        slices = [pydicom.dcmread(carpeta + '/' + s) for s in os.listdir(carpeta)]
        slices.sort(key = lambda x: int(x.ImagePositionPatient[0]))
        #HALLAMOS UN APROXIMADO DE LA PROPORCION DE CADA EJE PARA USAR EL SLIDER
        pixel_spacing=slices[0].PixelSpacing
        slice_thickness=slices[0].SliceThickness
        proporcion_filas = float(slice_thickness)/ float(pixel_spacing[1])
        proporcion_columnas =float(slice_thickness)/ float(pixel_spacing[0])
        proporciones=(proporcion_filas,proporcion_columnas)
        valores = tuple(int(math.floor(coord)) for coord in proporciones) #Los valores hallados se usan para la posicion del eje
        volumen = np.stack([s.pixel_array for s in slices])
        volumen = volumen.astype(np.int16)
        valor=(self.numero_imagen-1)*valores[0]
        self.ax.imshow(volumen[:,valor,:], cmap="gray", aspect='auto') 
        self.ax.axis('off')
        self.ax.set_position([0, 0, 1, 1])  # Configura el objeto Axes para ocupar todo el espacio
        self.draw()        

class Ventana(QMainWindow):
    def __init__(self): #Constructor de la clase
        QMainWindow.__init__(self)
        loadUi('log-in.ui',self)
        self.setWindowTitle("Log-in")
        self.setup()

    def setup(self): # Llama al método setup, que está definido más adelante en la clase.
        #se programa la senal para el boton
        self.ingresar.clicked.connect(self.accion_ingresar) #cuando el botón se presiona, se ejecutará el método accion_ingresar.
        

    def abrirVentana(self):
        ventana_emergente = ventanaEmergente(self)  # Pasar la referencia de la ventana principal
        ventana_emergente.show()

    
    def asignarControlador(self,c): #Guarda un controlador para posteriormente hacer validaciones
        self.__controlador = c

    def accion_ingresar(self):
        # Extraer el texto de los campos campo_usuario y campo_password.
        usuario = self.usuario.text()
        password = self.password.text()
        # Esta información la debemos pasar al controlador
        resultado = self.__controlador.validar_usuario(usuario, password) # Función de validación del controlador
        # Se crea la ventana de resultado
        msg = QMessageBox(self)
        msg.setWindowTitle("Error")
        # Se selecciona el resultado de acuerdo al resultado de la operación
        if resultado:
            self.abrirVentana()
        else:
            msg.setText("Usuario no Válido")
            msg.show()
        # Se muestra la ventana
        

class ventanaEmergente(QDialog):
    def __init__(self, ppal=None):  # Añadir el argumento parent
        super().__init__(ppal)
        loadUi("ventanaEmergente.ui", self) # Lee el archivo de QtDesigner
        self.setWindowTitle("BioTech Solutions") # Añadimos un título a nuestra ventana
        self.__ventanaPadre = ppal  # Guardar la referencia al padre
        self.setup()

    def setup(self):
        
        self.dicom.clicked.connect(self.mostrar_dicom)
        self.cancelar.clicked.connect(self.mostrar_inicio)

    def mostrar_dicom(self):
        try:
            carpeta=QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta", "/ruta/inicial")
            archivos_dicom = [archivo for archivo in os.listdir(carpeta) if archivo.endswith('.dcm')]
            
            # Verifica si hay archivos DICOM en la carpeta
            if not archivos_dicom:
                text="¡No se encontraron archivos .dcm en la ruta especificada!"
                message= QMessageBox.critical(self, "Alerta!", text, QMessageBox.Ok)
            else:
                v_dicom=Ventana_dicom(archivos_dicom, carpeta, self.__ventanaPadre, self)
                self.hide() 
                v_dicom.show() 
        except FileNotFoundError:
            text="¡No se encontraron archivos .dcm en la ruta especificada!"
            message= QMessageBox.critical(self, "Alerta!", text, QMessageBox.Ok) 

    def mostrar_inicio (self):
        text = "¿Está seguro que desea salir?"
        message = QMessageBox.question(self, "Log out", text, QMessageBox.Yes | QMessageBox.No)
        if message == QMessageBox.Yes:
            text = "Sesión cerrada con éxito \n¡Hasta pronto!"
            message = QMessageBox.information(self, "Log out", text, QMessageBox.Ok)
            self.close()
            self.__ventanaPadre.show()

    
class Ventana_dicom(QDialog):   
    def __init__(self, archivos, carpeta, ppal=None, sec= None):
        super().__init__(ppal)              
        loadUi("DICOM.ui", self)    
        self.setWindowTitle("Imagenes DICOM")
        self.__ventanaPadre = ppal
        self.__ventanaSec= sec
        self.archivos = archivos
        self.carpeta = carpeta
        self.valor_actual.setText("1")
        self.setup()
        self.graficar_eje_sag()
        self.graficar_eje_co()
        self.graficar_eje_ax()

    def setup(self):
        self.regresar.clicked.connect(self.mostrar_inicio) 
        self.slider.setMinimum(1)
        self.slider.setMaximum(len(self.archivos))
        self.slider.setValue(1)
        self.slider.valueChanged.connect(self.ver_valor)
        self.info_im.clicked.connect(self.abrir_info)
        self.slider.valueChanged.connect(self.graficar_eje_sag)
        self.slider.valueChanged.connect(self.graficar_eje_co)
        self.slider.valueChanged.connect(self.graficar_eje_ax)
        self.valor_maximo.setText(str(len(self.archivos)))

    def graficar_eje_sag(self):
        layout = self.eje_sagital.layout() or QVBoxLayout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        self.grafico = Eje_sagital(self.eje_sagital, self.archivos, self.carpeta, self.slider.value())
        layout.addWidget(self.grafico)

        self.eje_sagital.setLayout(layout)

    def graficar_eje_co(self):
        layout = self.eje_coronal.layout() or QVBoxLayout()

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self.grafico = Eje_coronal(self.eje_coronal, self.archivos, self.carpeta,self.slider.value())
        layout.addWidget(self.grafico)
        self.eje_coronal.setLayout(layout)

    def graficar_eje_ax(self):
        layout = self.eje_axial.layout() or QVBoxLayout()
    
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self.grafico = Eje_axial(self.eje_axial, self.archivos, self.carpeta, self.slider.value())
        layout.addWidget(self.grafico)
        self.eje_axial.setLayout(layout)

    def ver_valor(self):
        self.valor_actual.setText(str(self.slider.value()))
        
    def abrir_info(self): 
        v_info=VentanaInfo_img(self.archivos,self.carpeta,self.slider.value(), self, self.__ventanaPadre)
        v_info.show()

    def mostrar_inicio (self):
        text = "¿Está seguro que desea salir?"
        message = QMessageBox.question(self, "Log out", text, QMessageBox.Yes | QMessageBox.No)
        if message == QMessageBox.Yes:
            text = "Sesión cerrada con éxito \n¡Hasta pronto!"
            message = QMessageBox.information(self, "Log out", text, QMessageBox.Ok)
            self.close()
            self.__ventanaPadre.show()

class VentanaInfo_img(QDialog):
    def __init__(self, archivos,carpeta, indice, ppal=None, ventana_main=None):
        super().__init__(ppal)
        loadUi("INFO.ui",self)
        self.setWindowTitle("Información del paciente")
        self.indice=indice
        self.archivos=archivos
        self.carpeta=carpeta
        self.ventana_main=ventana_main
        self.setup()

    def setup(self):
        self.regresar.clicked.connect(lambda: self.close())
        self.body_part.setText(self.info("BodyPartExamined"))
        self.pat_sex.setText(self.info("PatientSex"))
        self.peso_pac.setText(str(self.info("PatientWeight")))
        self.date.setText(f'{str(self.info("AcquisitionDate"))[:4]}/ {str(self.info("AcquisitionDate"))[4:6]}/ {str(self.info("AcquisitionDate"))[6:]}')

    def info(self,caracteristica):
        imagen_dicom = pydicom.dcmread(os.path.join(self.carpeta, self.archivos[self.indice-1]))
        x= getattr(imagen_dicom, caracteristica, "N.A")
        if x == "":
            return "No existe"
        else:
            return x
        
    
                



    
        

   




    



    



    

        
   

        
   

    

    

        
        
        