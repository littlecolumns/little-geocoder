from  parsedatetime.pdt_locales import (
    de_DE, en_AU, en_US,
    es, nl_NL, pt_BR,
    ru_RU, fr_FR)

from PyQt5.QtWidgets import (QMainWindow, QTextEdit, 
    QAction, QFileDialog, QApplication, QWidget, QLabel, 
    QComboBox, QApplication, QHBoxLayout, QVBoxLayout, QPushButton,
    QTableWidget,QTableWidgetItem, QGridLayout)
import PyQt5.QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys
import os
import pandas as pd
from collections import OrderedDict
import censusbatchgeocoder
import platform

ROW_COUNT = 20

ADJUSTMENTS = OrderedDict()
ADJUSTMENTS["None"] = lambda x: x
ADJUSTMENTS["Comma split: first section"] = lambda x: x.split(",")[0]
ADJUSTMENTS["Comma split: second"] = lambda x: x.split(",")[1]
ADJUSTMENTS["Comma split: third"] = lambda x: x.split(",")[2]
ADJUSTMENTS["Comma split: second-to-last"] = lambda x: x.split(",")[-2]
ADJUSTMENTS["Comma split: last"] = lambda x: x.split(",")[-1]
ADJUSTMENTS["Newline split: first section"] = lambda x: x.split("\n")[0]
ADJUSTMENTS["Newline split: second"] = lambda x: x.split("\n")[1]
ADJUSTMENTS["Newline split: third"] = lambda x: x.split("\n")[2]
ADJUSTMENTS["Newline split: second-to-last"] = lambda x: x.split("\n")[-2]
ADJUSTMENTS["Newline split: last"] = lambda x: x.split("\n")[-1]

def resource_path(path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path)
    else:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(current_dir, path)

class VisualCensusGeocoder(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.filename = None
        self.setWindowIcon(QIcon(resource_path("worldwide.png")))

        self.initUI()
        
        
    def initUI(self):      
        vbox = QVBoxLayout()
        # File picker

        file_picker = QPushButton("Browse...")
        file_picker.clicked.connect(self.showFilePicker)

        row = QHBoxLayout()
        row.addWidget(file_picker)
        self.file_label = QLabel("Please select a CSV file to geocode")
        row.addWidget(self.file_label)

        row.addStretch(1)

        vbox.addLayout(row)

        # Not using .keys() to keep them in order when drawing
        self.field_names = ['address', 'city', 'state', 'zipcode']
        self.fields = {
            'address': { 'title': 'Address', 'column': 0 },
            'city': { 'title': 'City', 'column': 1 },
            'state': { 'title': 'State', 'column': 2 },
            'zipcode': { 'title': 'Zipcode', 'column': 3 }
        }

        for key in self.field_names:
            field_selector = QComboBox(self)
            field_selector.currentIndexChanged.connect(self.comboChanged)
            self.fields[key]['combo'] = field_selector

            adjustment_selector = QComboBox(self)
            adjustment_selector.addItems(ADJUSTMENTS.keys())
            adjustment_selector.currentIndexChanged.connect(self.comboChanged)
            self.fields[key]['adjustment'] = adjustment_selector

            self.fields[key]['sample'] = QLabel("")

        grid = QGridLayout()

        grid.addWidget(QLabel("<strong>Column Name</strong>"), 0, 1, 1, 2)
        grid.addWidget(QLabel("<strong>Adjustments</strong>"), 0, 3, 1, 2)
        grid.addWidget(QLabel("<strong>Column Sample</strong>"), 0, 5, 1, 2)

        for i, key in enumerate(self.field_names):
            field = self.fields[key]
            grid.addWidget(QLabel(field['title']), i+1, 0, 1, 1, alignment=Qt.AlignRight)
            grid.addWidget(field['combo'], i+1, 1, 1, 2)
            grid.addWidget(field['adjustment'], i+1, 3, 1, 2)
            grid.addWidget(field['sample'], i+1, 5, 1, 2)
        vbox.addLayout(grid)

        # Preview
        vbox.addWidget(QLabel("<strong>API Preview</strong>"))

        self.table = QTableWidget()
        self.table.setRowCount(ROW_COUNT)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Address", "City", "State", "ZIP"])
        self.table.verticalHeader().setVisible(False)

        row = QHBoxLayout()
        row.addWidget(self.table)
        vbox.addLayout(row)

        # Geocode button
        geo_button = QPushButton("Geocode")
        geo_button.clicked.connect(self.doGeocode)

        row = QHBoxLayout()
        row.addWidget(geo_button)

        vbox.addLayout(row)

        self.setLayout(vbox)     
        
        self.setGeometry(300, 300, 750, 500)
        self.setWindowTitle('Visual Census Geocoder')
        self.table.setMinimumSectionSize = 150
        self.table.horizontalHeader().setSectionResizeMode(0, 1)
        self.table.horizontalHeader().setSectionResizeMode(1, 1)
        self.table.horizontalHeader().setSectionResizeMode(2, 2)
        self.table.horizontalHeader().setSectionResizeMode(3, 2)
        self.show()
    
    def prepareForGeocoding(self, row):
        data = {}
        data['id'] = row.name

        for key in self.field_names:
            try:
                data_col_name = self.fields[key]['combo'].currentText()
                adjustment_name = self.fields[key]['adjustment'].currentText()
                adjustment = ADJUSTMENTS[adjustment_name]
                val = adjustment(row[data_col_name])

                data[key] = val
            except:
                data[key] = ""
        return data

    def doGeocode(self):
        self.pickTargetFilename()

        if not self.target_filename:
            return

        prepared_data = self.df.fillna("").apply(self.prepareForGeocoding, axis=1)
        results = censusbatchgeocoder.geocode(prepared_data)

        # Combine geodata with original dataframe, same results
        results_df = pd.DataFrame(results)
        self.df.merge(results_df, 
            left_index=True, 
            right_on='id', 
            suffixes=("","_geo")
        ).to_csv(self.target_filename)

        # Reveal processed data in the file browser
        if platform.system() == "Windows":
            os.system("explorer /select,\"%s\"" % os.path.normpath(self.target_filename))
        else:
            # Try/except to make it probably work in Linux, too
            try:
                os.system("open -R \"%s\"" % self.target_filename)
            except:
                pass

    def updateColumn(self, field):
        colnum = field['column']
        data_col_name = field['combo'].currentText()
        adjustment_name = field['adjustment'].currentText()

        for index, row in self.df.head(ROW_COUNT).fillna("").iterrows():
            try:
                adjustment = ADJUSTMENTS[adjustment_name]
                val = adjustment(row[data_col_name])
                if index == 0:
                    field['sample'].setText("<small>" + row[data_col_name] + "</small>")
                self.table.setItem(index, colnum, QTableWidgetItem(val))
            except:
                self.table.setItem(index, colnum, QTableWidgetItem(""))

    def comboChanged(self):
        for key in self.field_names:
            self.updateColumn(self.fields[key])

    def updateComboBoxes(self):
        options = ['-'] + list(self.df.columns.values) + ['custom', 'none']
        for index, key in enumerate(self.field_names):
            combo = self.fields[key]['combo']
            combo.clear()
            combo.addItems(options)
            self.fields[key]['adjustment'].setCurrentIndex(0)

    def updateTable(self):
        rows = df.head()

    def pickTargetFilename(self):
        fname = QFileDialog.getSaveFileName(self, 
            'Select output filename', 
            self.filename.replace(".csv", "-geocoded.csv"))

        if fname[0]:
            self.target_filename = fname[0]
        else:
            self.target_filename = None

    def showFilePicker(self):
        fname = QFileDialog.getOpenFileName(self, 
            'Select file')

        if fname[0]:
            self.filename = fname[0]
            self.df = pd.read_csv(self.filename, dtype='str')
            self.file_label.setText(self.filename)
            self.updateComboBoxes()

            # with f:
            #     data = f.read()
            #     self.textEdit.setText(data) 

    def onActivated(self, text):
      
        self.lbl.setText(text)
        self.lbl.adjustSize()  
        
                
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = VisualCensusGeocoder()
    sys.exit(app.exec_())
