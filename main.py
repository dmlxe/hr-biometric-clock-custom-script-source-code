#2020-2023 - dmlxe

from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QLabel, QPushButton, QVBoxLayout, QMessageBox
import sys
import pandas as pd

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Set window size and title
        self.setGeometry(0, 0, 400, 250)
        self.setWindowTitle('Generar Registros Asistencia')

        # Create the necessary Widgets
        #  Labels
        self.label1 = QLabel('Archivo de trabajadores (.csv): ')
        self.label2 = QLabel('Archivo de registros (.dat): ')
        self.label3 = QLabel('Generar: ')
        #  Buttons
        self.button1 = QPushButton('Seleccionar Archivo')
        self.button2 = QPushButton('Seleccionar Archivo')
        self.buttonCompute = QPushButton('Generar')

        # Set Box Layout
        self.setLayout(QVBoxLayout())

        # Add all Widgets to the interface
        self.layout().addWidget(self.label1)
        self.layout().addWidget(self.button1)
        self.layout().addWidget(self.label2)
        self.layout().addWidget(self.button2)
        self.layout().addWidget(self.label3)
        self.layout().addWidget(self.buttonCompute)

        # Vinculate buttons to their respective functions
        self.button1.clicked.connect(self.selectFile_csv)
        self.button2.clicked.connect(self.selectFile_dat)
        self.buttonCompute.clicked.connect(self.computeTEST)

        # File paths
        self.file_csv = None
        self.file_dat = None

    def selectFile_csv(self):
        # Opens operating system file selector
        self.file_csv, _ = QFileDialog.getOpenFileName(self, 'Seleccionar archivo de trabajadores (.csv)', '', '(*.csv)')
        # Updates the label with the selected file path
        if self.file_csv:
            self.label1.setText('Archivo de trabajadores (.csv): \n' + self.file_csv)
        else:
            self.label1.setText('Archivo de trabajadores (.csv): ')

    def selectFile_dat(self):
        # Opens operating system file selector
        self.file_dat, _ = QFileDialog.getOpenFileName(self, 'Archivo de registros (.dat): ', '', '(*.dat)')
        # Updates the label with the selected file path
        if self.file_dat:
            self.label2.setText('Archivo de registros (.dat): \n' + self.file_dat)
        else:
            self.label2.setText('Archivo de registros (.dat): ')
        
    def computeTEST(self):
        try:
            # Try to define the neccesary DataFrames with the selected files
            dfWorkers = pd.read_csv(self.file_csv)
            dfRecords = pd.read_fwf(self.file_dat, usecols=[0,1,2], names=['ID','Fecha','Hora'])
        except (ValueError, FileNotFoundError):
            # Clean the data and displays an error message
            self.file_dat = None
            self.file_csv = None
            self.label2.setText('Archivo de registros (.dat): ')
            self.label1.setText('Archivo de trabajadores (.csv): ')
            QMessageBox.critical(self, "Error", "Seleccione dos archivos")
            return

        # It is not necessary to have a separation between date and time, so they are merged and eliminated
        dfRecords['Registro'] = dfRecords['Fecha'].str.cat(dfRecords['Hora'], sep=' ')
        #del(dfRecords['Fecha'])
        #del(dfRecords['Hora'])

        # Sort the records by ID and by timestamp (Registro)
        dfRecords.sort_values(by=['ID', 'Registro'], inplace=True)
        
        # Create the necessary dataframe to perform the required operations
        dfCompleteRecords= pd.DataFrame()
        dfCompleteRecords['ID'] = dfRecords['ID']
        # Map the corresponding IDs from the registration file with their respective names and surnames
        dfCompleteRecords['Nombre'] = dfRecords['ID'].map(dfWorkers.set_index('ID')['Nombre'])
        dfCompleteRecords['Apellido'] = dfRecords['ID'].map(dfWorkers.set_index('ID')['Apellido'])
        dfCompleteRecords['Registro'] = dfRecords['Registro']

        # Translate dates to something usable by Pandas
        dfCompleteRecords['Registro'] = pd.to_datetime(dfCompleteRecords['Registro'])

        # Save the file with all the records
        dfCompleteRecords.to_csv('registros completos.csv', index=False)

        ### Filter duplicate records

        # Group the records by ID and day (Necessary for the filtering process)
        groupByDay = dfCompleteRecords.groupby([pd.Grouper(key='ID'), pd.Grouper(key='Registro', freq='D')])

        # Iterate over each group and filter the records with a time difference of less than 5 minutes
        dfFilteredRecords = []
        for _, group in groupByDay:
            group = group.sort_values(by='Registro')
            previousRecord = None
            for _, row in group.iterrows():
                if previousRecord is None or abs((row['Registro'] - previousRecord['Registro']).seconds) > 300: # 15 minutes
                    dfFilteredRecords.append(row)
                    previousRecord = row

        # Create a new DataFrame with the filtered records
        dfFilteredRecords = pd.DataFrame(dfFilteredRecords, columns=['ID', 'Nombre', 'Apellido', 'Registro'])

        # Create a new file with the filtered records
        dfFilteredRecords.to_csv('registros filtrados.csv', index=False)
        
        # Displays success message
        QMessageBox.information(self, "Completado", "Generado: registros completos.csv \n Generado: registros filtrados.csv")
        
if __name__ == '__main__':
    # Lauch app
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())