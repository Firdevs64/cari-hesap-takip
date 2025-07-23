from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDate
from db import veritabani_baglan

class ProductUpdateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Ürün Güncelle / Sil')
        self.setMinimumWidth(700)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initForm()
        self.initTable()
        self.loadProducts()

    def initForm(self):
        form_layout = QFormLayout()
        self.urun_adi_input = QLineEdit()
        self.barkod_input = QLineEdit()
        self.birim_input = QComboBox()
        self.birim_input.addItems(['Adet', 'cm', 'metre', 'metrekare', 'gram', 'kilo', 'koli'])
        self.miktar_input = QSpinBox()
        self.miktar_input.setMinimum(1)
        self.alis_fiyat_input = QDoubleSpinBox()
        self.alis_fiyat_input.setDecimals(2)
        self.alis_fiyat_input.setMinimum(0)
        self.alis_fiyat_input.setMaximum(1000000)
        self.satis_fiyat_input = QDoubleSpinBox()
        self.satis_fiyat_input.setDecimals(2)
        self.satis_fiyat_input.setMinimum(0)
        self.satis_fiyat_input.setMaximum(1000000)
        self.alis_tarihi_input = QDateEdit()
        self.alis_tarihi_input.setDisplayFormat('dd.MM.yyyy')
        self.alis_tarihi_input.setDate(QDate.currentDate())
        self.alis_tarihi_input.setCalendarPopup(True)
        self.aciklama_input = QTextEdit()
        btn_layout = QHBoxLayout()
        self.guncelle_btn = QPushButton('Güncelle')
        self.guncelle_btn.clicked.connect(self.updateProduct)
        self.sil_btn = QPushButton('Sil')
        self.sil_btn.clicked.connect(self.deleteProduct)
        btn_layout.addWidget(self.guncelle_btn)
        btn_layout.addWidget(self.sil_btn)
        form_layout.addRow('Ürün Adı:', self.urun_adi_input)
        form_layout.addRow('Barkod:', self.barkod_input)
        form_layout.addRow('Birim:', self.birim_input)
        form_layout.addRow('Miktar:', self.miktar_input)
        form_layout.addRow('Alış Fiyatı:', self.alis_fiyat_input)
        form_layout.addRow('Satış Fiyatı:', self.satis_fiyat_input)
        form_layout.addRow('Alış Tarihi:', self.alis_tarihi_input)
        form_layout.addRow('Açıklama:', self.aciklama_input)
        form_layout.addRow(btn_layout)
        self.layout.addLayout(form_layout)

    def initTable(self):
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['Ürün Adı', 'Barkod', 'Birim', 'Miktar', 'Alış Fiyatı', 'Satış Fiyatı', 'Alış Tarihi', 'Açıklama'])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.cellClicked.connect(self.fillFormFromTable)
        self.table.horizontalHeader().setSectionResizeMode(self.table.horizontalHeader().Stretch)
        self.layout.addWidget(self.table)

    def loadProducts(self):
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('SELECT urun_adi, barkod, birim, miktar, alis_fiyat, satis_fiyat, alis_tarihi, aciklama FROM urunler')
        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        conn.close()

    def fillFormFromTable(self, row, col):
        self.urun_adi_input.setText(self.table.item(row, 0).text())
        self.barkod_input.setText(self.table.item(row, 1).text())
        birim = self.table.item(row, 2).text()
        idx = self.birim_input.findText(birim)
        if idx >= 0:
            self.birim_input.setCurrentIndex(idx)
        self.miktar_input.setValue(int(self.table.item(row, 3).text()))
        self.alis_fiyat_input.setValue(float(self.table.item(row, 4).text()))
        self.satis_fiyat_input.setValue(float(self.table.item(row, 5).text()))
        tarih = QDate.fromString(self.table.item(row, 6).text(), 'dd.MM.yyyy')
        if tarih.isValid():
            self.alis_tarihi_input.setDate(tarih)
        else:
            self.alis_tarihi_input.setDate(QDate.currentDate())
        self.aciklama_input.setText(self.table.item(row, 7).text())

    def updateProduct(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen güncellemek için bir ürün seçin!')
            return
        urun_adi = self.urun_adi_input.text().strip()
        barkod = self.barkod_input.text().strip()
        birim = self.birim_input.currentText()
        miktar = self.miktar_input.value()
        alis_fiyat = self.alis_fiyat_input.value()
        satis_fiyat = self.satis_fiyat_input.value()
        alis_tarihi = self.alis_tarihi_input.date().toString('dd.MM.yyyy')
        aciklama = self.aciklama_input.toPlainText().strip()
        eski_barkod = self.table.item(selected, 1).text()
        if not urun_adi or not barkod:
            QMessageBox.warning(self, 'Uyarı', 'Ürün adı ve barkod zorunludur!')
            return
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('''UPDATE urunler SET urun_adi=?, barkod=?, birim=?, miktar=?, alis_fiyat=?, satis_fiyat=?, alis_tarihi=?, aciklama=? WHERE barkod=?''',
                       (urun_adi, barkod, birim, miktar, alis_fiyat, satis_fiyat, alis_tarihi, aciklama, eski_barkod))
        conn.commit()
        conn.close()
        self.loadProducts()
        QMessageBox.information(self, 'Başarılı', 'Ürün güncellendi!')

    def deleteProduct(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek için bir ürün seçin!')
            return
        barkod = self.table.item(selected, 1).text()
        urun_adi = self.table.item(selected, 0).text()
        cevap = QMessageBox.question(self, 'Onay', f"{urun_adi} ({barkod}) ürününü silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            conn = veritabani_baglan()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM urunler WHERE barkod = ?', (barkod,))
            conn.commit()
            conn.close()
            self.loadProducts()
            QMessageBox.information(self, 'Başarılı', 'Ürün silindi!') 