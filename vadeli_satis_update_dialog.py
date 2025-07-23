from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QMessageBox
from PyQt5.QtCore import QDate
from db import veritabani_baglan

class VadeliSatisUpdateDialog(QDialog):
    def __init__(self, satis_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Vadeli Satış Güncelle')
        self.setMinimumWidth(500)
        self.satis_id = satis_id
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initForm()
        self.loadCustomers()
        self.loadSale()

    def initForm(self):
        form_layout = QFormLayout()
        self.musteri_combo = QComboBox()
        self.is_input = QLineEdit()
        self.fiyat_input = QDoubleSpinBox()
        self.fiyat_input.setDecimals(2)
        self.fiyat_input.setMinimum(0)
        self.fiyat_input.setMaximum(1000000)
        self.miktar_input = QSpinBox()
        self.miktar_input.setMinimum(1)
        self.birim_input = QComboBox()
        self.birim_input.addItems(['Adet', 'cm', 'metre', 'metrekare', 'gram', 'kilo', 'koli'])
        self.tarih_input = QDateEdit()
        self.tarih_input.setDisplayFormat('dd.MM.yyyy')
        self.tarih_input.setDate(QDate.currentDate())
        self.tarih_input.setCalendarPopup(True)
        self.borc_input = QDoubleSpinBox()
        self.borc_input.setDecimals(2)
        self.borc_input.setMinimum(0)
        self.borc_input.setMaximum(1000000)
        self.alacak_input = QDoubleSpinBox()
        self.alacak_input.setDecimals(2)
        self.alacak_input.setMinimum(0)
        self.alacak_input.setMaximum(1000000)
        self.bakiye_input = QLineEdit()
        self.bakiye_input.setReadOnly(True)
        self.vade_tarihi_input = QDateEdit()
        self.vade_tarihi_input.setDisplayFormat('dd.MM.yyyy')
        self.vade_tarihi_input.setDate(QDate.currentDate())
        self.vade_tarihi_input.setCalendarPopup(True)
        self.aciklama_input = QTextEdit()
        self.kaydet_btn = QPushButton('Kaydet')
        self.kaydet_btn.clicked.connect(self.updateSale)
        self.borc_input.valueChanged.connect(self.updateBakiye)
        self.alacak_input.valueChanged.connect(self.updateBakiye)
        form_layout.addRow('Müşteri:', self.musteri_combo)
        form_layout.addRow('Yapılan İş:', self.is_input)
        form_layout.addRow('Fiyat:', self.fiyat_input)
        form_layout.addRow('Miktar:', self.miktar_input)
        form_layout.addRow('Birim:', self.birim_input)
        form_layout.addRow('Tarih:', self.tarih_input)
        form_layout.addRow('Borç:', self.borc_input)
        form_layout.addRow('Alacak:', self.alacak_input)
        form_layout.addRow('Bakiye:', self.bakiye_input)
        form_layout.addRow('Vade Tarihi:', self.vade_tarihi_input)
        form_layout.addRow('Açıklama:', self.aciklama_input)
        form_layout.addRow(self.kaydet_btn)
        self.layout.addLayout(form_layout)

    def loadCustomers(self):
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('SELECT id, ad, soyad FROM musteriler')
        self.customers = cursor.fetchall()
        self.musteri_combo.clear()
        for c in self.customers:
            self.musteri_combo.addItem(f"{c[1]} {c[2]}", c[0])
        conn.close()

    def loadSale(self):
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('SELECT musteri_id, is_, fiyat, miktar, birim, tarih, borc, alacak, bakiye, vade_tarihi, aciklama FROM vadeli_satislar WHERE id=?', (self.satis_id,))
        row = cursor.fetchone()
        if row:
            musteri_id, is_, fiyat, miktar, birim, tarih, borc, alacak, bakiye, vade_tarihi, aciklama = row
            idx = self.musteri_combo.findData(musteri_id)
            if idx >= 0:
                self.musteri_combo.setCurrentIndex(idx)
            self.is_input.setText(is_)
            self.fiyat_input.setValue(fiyat)
            self.miktar_input.setValue(miktar)
            birim_idx = self.birim_input.findText(birim)
            if birim_idx >= 0:
                self.birim_input.setCurrentIndex(birim_idx)
            tarih_dt = QDate.fromString(tarih, 'dd.MM.yyyy')
            if tarih_dt.isValid():
                self.tarih_input.setDate(tarih_dt)
            self.borc_input.setValue(borc)
            self.alacak_input.setValue(alacak)
            self.bakiye_input.setText(f"{bakiye:.2f}")
            vade_dt = QDate.fromString(vade_tarihi, 'dd.MM.yyyy')
            if vade_dt.isValid():
                self.vade_tarihi_input.setDate(vade_dt)
            self.aciklama_input.setText(aciklama)
        conn.close()

    def updateBakiye(self):
        borc = self.borc_input.value()
        alacak = self.alacak_input.value()
        self.bakiye_input.setText(f"{borc - alacak:.2f}")

    def updateSale(self):
        musteri_id = self.musteri_combo.currentData()
        is_ = self.is_input.text().strip()
        fiyat = self.fiyat_input.value()
        miktar = self.miktar_input.value()
        birim = self.birim_input.currentText()
        tarih = self.tarih_input.date().toString('dd.MM.yyyy')
        borc = self.borc_input.value()
        alacak = self.alacak_input.value()
        bakiye = borc - alacak
        vade_tarihi = self.vade_tarihi_input.date().toString('dd.MM.yyyy')
        aciklama = self.aciklama_input.toPlainText().strip()
        if not musteri_id or not is_:
            QMessageBox.warning(self, 'Uyarı', 'Müşteri ve yapılan iş zorunludur!')
            return
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('''UPDATE vadeli_satislar SET musteri_id=?, is_=?, fiyat=?, miktar=?, birim=?, tarih=?, borc=?, alacak=?, bakiye=?, vade_tarihi=?, aciklama=? WHERE id=?''',
                       (musteri_id, is_, fiyat, miktar, birim, tarih, borc, alacak, bakiye, vade_tarihi, aciklama, self.satis_id))
        conn.commit()
        conn.close()
        QMessageBox.information(self, 'Başarılı', 'Vadeli satış güncellendi!')
        self.accept() 