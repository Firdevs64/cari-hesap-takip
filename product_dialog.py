from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QHeaderView
from db import veritabani_baglan

class ProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Ürün Yönetimi')
        self.setMinimumWidth(700)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initForm()
        self.initTable()
        self.loadProducts()

    def initForm(self):
        form_layout = QFormLayout()
        self.urun_adi_input = QLineEdit()
        self.urun_kodu_input = QLineEdit()
        self.birim_input = QComboBox()
        self.birim_input.addItems(['Adet', 'Kg', 'Paket', 'Koli'])
        self.adet_input = QSpinBox()
        self.adet_input.setMinimum(1)
        self.fiyat_input = QDoubleSpinBox()
        self.fiyat_input.setDecimals(2)
        self.fiyat_input.setMinimum(0)
        self.fiyat_input.setMaximum(1000000)
        self.aciklama_input = QTextEdit()
        btn_layout = QHBoxLayout()
        self.ekle_btn = QPushButton('Ekle')
        self.ekle_btn.clicked.connect(self.addProduct)
        self.guncelle_btn = QPushButton('Güncelle')
        self.guncelle_btn.clicked.connect(self.updateProduct)
        btn_layout.addWidget(self.ekle_btn)
        btn_layout.addWidget(self.guncelle_btn)
        form_layout.addRow('Ürün Adı:', self.urun_adi_input)
        form_layout.addRow('Ürün Kodu:', self.urun_kodu_input)
        form_layout.addRow('Birim:', self.birim_input)
        form_layout.addRow('Adet:', self.adet_input)
        form_layout.addRow('Fiyat:', self.fiyat_input)
        form_layout.addRow('Açıklama:', self.aciklama_input)
        form_layout.addRow(btn_layout)
        self.layout.addLayout(form_layout)

    def initTable(self):
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Ürün Adı', 'Ürün Kodu', 'Birim', 'Adet', 'Fiyat', 'Açıklama'])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.cellClicked.connect(self.fillFormFromTable)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        # Sil butonu
        btn_layout = QHBoxLayout()
        self.sil_btn = QPushButton('Ürünü Sil')
        self.sil_btn.clicked.connect(self.deleteProduct)
        btn_layout.addStretch()
        btn_layout.addWidget(self.sil_btn)
        self.layout.addLayout(btn_layout)

    def loadProducts(self):
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('SELECT urun_adi, urun_kodu, birim, adet, fiyat, aciklama FROM urunler')
        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        # self.table.resizeColumnsToContents()  # Kaldırıldı
        # self.table.horizontalHeader().setStretchLastSection(True)  # Kaldırıldı
        conn.close()

    def addProduct(self):
        urun_adi = self.urun_adi_input.text().strip()
        urun_kodu = self.urun_kodu_input.text().strip()
        birim = self.birim_input.currentText()
        adet = self.adet_input.value()
        fiyat = self.fiyat_input.value()
        aciklama = self.aciklama_input.toPlainText().strip()
        if not urun_adi or not urun_kodu:
            QMessageBox.warning(self, 'Uyarı', 'Ürün adı ve kodu zorunludur!')
            return
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO urunler (urun_adi, urun_kodu, birim, adet, fiyat, aciklama) VALUES (?, ?, ?, ?, ?, ?)', (urun_adi, urun_kodu, birim, adet, fiyat, aciklama))
        conn.commit()
        conn.close()
        self.loadProducts()
        self.urun_adi_input.clear()
        self.urun_kodu_input.clear()
        self.birim_input.setCurrentIndex(0)
        self.adet_input.setValue(1)
        self.fiyat_input.setValue(0)
        self.aciklama_input.clear()
        QMessageBox.information(self, 'Başarılı', 'Ürün eklendi!') 

    def deleteProduct(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek için bir ürün seçin!')
            return
        urun_adi = self.table.item(selected, 0).text()
        urun_kodu = self.table.item(selected, 1).text()
        cevap = QMessageBox.question(self, 'Onay', f"{urun_adi} ({urun_kodu}) ürününü silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            conn = veritabani_baglan()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM urunler WHERE urun_adi = ? AND urun_kodu = ?', (urun_adi, urun_kodu))
            conn.commit()
            conn.close()
            self.loadProducts()
            QMessageBox.information(self, 'Başarılı', 'Ürün silindi!') 

    def fillFormFromTable(self, row, col):
        self.urun_adi_input.setText(self.table.item(row, 0).text())
        self.urun_kodu_input.setText(self.table.item(row, 1).text())
        birim = self.table.item(row, 2).text()
        idx = self.birim_input.findText(birim)
        if idx >= 0:
            self.birim_input.setCurrentIndex(idx)
        self.adet_input.setValue(int(self.table.item(row, 3).text()))
        self.fiyat_input.setValue(float(self.table.item(row, 4).text()))
        self.aciklama_input.setText(self.table.item(row, 5).text())

    def updateProduct(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen güncellemek için bir ürün seçin!')
            return
        urun_adi = self.urun_adi_input.text().strip()
        urun_kodu = self.urun_kodu_input.text().strip()
        birim = self.birim_input.currentText()
        adet = self.adet_input.value()
        fiyat = self.fiyat_input.value()
        aciklama = self.aciklama_input.toPlainText().strip()
        eski_urun_adi = self.table.item(selected, 0).text()
        eski_urun_kodu = self.table.item(selected, 1).text()
        if not urun_adi or not urun_kodu:
            QMessageBox.warning(self, 'Uyarı', 'Ürün adı ve kodu zorunludur!')
            return
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('''UPDATE urunler SET urun_adi=?, urun_kodu=?, birim=?, adet=?, fiyat=?, aciklama=? WHERE urun_adi=? AND urun_kodu=?''',
                       (urun_adi, urun_kodu, birim, adet, fiyat, aciklama, eski_urun_adi, eski_urun_kodu))
        conn.commit()
        conn.close()
        self.loadProducts()
        QMessageBox.information(self, 'Başarılı', 'Ürün güncellendi!') 