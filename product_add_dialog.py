from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QMessageBox
from PyQt5.QtCore import QDate
from db import veritabani_baglan

class ProductAddDialog(QDialog):
    def __init__(self, parent=None, urun_id=None):
        super().__init__(parent)
        self.urun_id = urun_id
        self.setWindowTitle('Ürün Ekle')
        self.setMinimumWidth(400)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initForm()
        if self.urun_id:
            self.setWindowTitle('Ürünü Güncelle')
            self.ekle_btn.setText('Güncelle')
            self.loadProduct()

    def initForm(self):
        form_layout = QFormLayout()
        self.urun_adi_input = QLineEdit()
        self.barkod_input = QLineEdit()
        self.birim_input = QComboBox()
        self.birim_input.addItems(['Adet', 'cm', 'metre', 'metrekare', 'gram', 'kilo', 'koli'])
        self.miktar_input = QDoubleSpinBox()
        self.miktar_input.setDecimals(2)
        self.miktar_input.setMinimum(0)
        self.miktar_input.setMaximum(999999)
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
        self.ekle_btn = QPushButton('Ekle')
        self.ekle_btn.clicked.connect(self.addProduct)
        form_layout.addRow('Ürün Adı:', self.urun_adi_input)
        form_layout.addRow('Barkod:', self.barkod_input)
        form_layout.addRow('Birim:', self.birim_input)
        form_layout.addRow('Miktar:', self.miktar_input)
        form_layout.addRow('Alış Fiyatı:', self.alis_fiyat_input)
        form_layout.addRow('Satış Fiyatı:', self.satis_fiyat_input)
        form_layout.addRow('Alış Tarihi:', self.alis_tarihi_input)
        form_layout.addRow('Açıklama:', self.aciklama_input)
        form_layout.addRow(self.ekle_btn)
        self.layout.addLayout(form_layout)

    def loadProduct(self):
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('SELECT urun_adi, barkod, birim, miktar, alis_fiyat, satis_fiyat, alis_tarihi, aciklama FROM urunler WHERE id=?', (self.urun_id,))
        row = cursor.fetchone()
        if row:
            self.urun_adi_input.setText(row[0])
            self.barkod_input.setText(row[1])
            self.birim_input.setCurrentText(row[2])
            self.miktar_input.setValue(row[3])
            self.alis_fiyat_input.setValue(row[4])
            self.satis_fiyat_input.setValue(row[5])
            self.alis_tarihi_input.setDate(QDate.fromString(row[6], 'dd.MM.yyyy'))
            self.aciklama_input.setPlainText(row[7])
        conn.close()

    def addProduct(self):
        urun_adi = self.urun_adi_input.text().strip()
        barkod = self.barkod_input.text().strip()
        birim = self.birim_input.currentText()
        miktar = self.miktar_input.value()
        alis_fiyat = self.alis_fiyat_input.value()
        satis_fiyat = self.satis_fiyat_input.value()
        alis_tarihi = self.alis_tarihi_input.date().toString('dd.MM.yyyy')
        aciklama = self.aciklama_input.toPlainText().strip()
        if not urun_adi or not barkod:
            QMessageBox.warning(self, 'Uyarı', 'Ürün adı ve barkod zorunludur!')
            return
        if self.urun_id:
            # Güncelleme sorgusu
            conn = veritabani_baglan()
            cursor = conn.cursor()
            cursor.execute('UPDATE urunler SET urun_adi=?, barkod=?, birim=?, miktar=?, alis_fiyat=?, satis_fiyat=?, alis_tarihi=?, aciklama=? WHERE id=?',
                (urun_adi, barkod, birim, miktar, alis_fiyat, satis_fiyat, alis_tarihi, aciklama, self.urun_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Başarılı', 'Ürün güncellendi!')
            self.accept()
        else:
            # Normal ekleme işlemi
            conn = veritabani_baglan()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO urunler (urun_adi, barkod, birim, miktar, alis_fiyat, satis_fiyat, alis_tarihi, aciklama) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (urun_adi, barkod, birim, miktar, alis_fiyat, satis_fiyat, alis_tarihi, aciklama))
            conn.commit()
            conn.close()
            self.urun_adi_input.clear()
            self.barkod_input.clear()
            self.birim_input.setCurrentIndex(0)
            self.miktar_input.setValue(1)
            self.alis_fiyat_input.setValue(0)
            self.satis_fiyat_input.setValue(0)
            self.alis_tarihi_input.setDate(QDate.currentDate())
            self.aciklama_input.clear()
            QMessageBox.information(self, 'Başarılı', 'Ürün eklendi!') 