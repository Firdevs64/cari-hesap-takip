from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTextEdit, QDateEdit, QMessageBox
from PyQt5.QtCore import QDate
from db import veritabani_baglan

class CustomerDialog(QDialog):
    def __init__(self, parent=None, musteri_id=None):
        super().__init__(parent)
        self.musteri_id = musteri_id
        self.setWindowTitle('Müşteri Ekle')
        self.setMinimumWidth(400)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initForm()
        if self.musteri_id:
            self.setWindowTitle('Müşteriyi Güncelle')
            self.ekle_btn.setText('Güncelle')
            self.loadCustomer()

    def initForm(self):
        form_layout = QFormLayout()
        self.ad_input = QLineEdit()
        self.soyad_input = QLineEdit()
        self.tel_input = QLineEdit()
        self.eposta_input = QLineEdit()
        self.adres_input = QLineEdit()
        self.tarih_input = QDateEdit()
        self.tarih_input.setDisplayFormat('dd.MM.yyyy')
        self.tarih_input.setDate(QDate.currentDate())
        self.tarih_input.setCalendarPopup(True)
        self.aciklama_input = QTextEdit()
        self.ekle_btn = QPushButton('Ekle')
        self.ekle_btn.clicked.connect(self.addCustomer)
        form_layout.addRow('Adı:', self.ad_input)
        form_layout.addRow('Soyadı:', self.soyad_input)
        form_layout.addRow('Telefon:', self.tel_input)
        form_layout.addRow('E-posta:', self.eposta_input)
        form_layout.addRow('Adres:', self.adres_input)
        form_layout.addRow('Kayıt Tarihi:', self.tarih_input)
        form_layout.addRow('Açıklama:', self.aciklama_input)
        form_layout.addRow(self.ekle_btn)
        self.layout.addLayout(form_layout)

    def loadCustomer(self):
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('SELECT ad, soyad, telefon, eposta, adres, kayit_tarihi, aciklama FROM musteriler WHERE id=?', (self.musteri_id,))
        row = cursor.fetchone()
        if row:
            self.ad_input.setText(row[0])
            self.soyad_input.setText(row[1])
            self.tel_input.setText(row[2])
            self.eposta_input.setText(row[3])
            self.adres_input.setText(row[4])
            self.tarih_input.setDate(QDate.fromString(row[5], 'dd.MM.yyyy'))
            self.aciklama_input.setPlainText(row[6])
        conn.close()

    def addCustomer(self):
        ad = self.ad_input.text().strip()
        soyad = self.soyad_input.text().strip()
        telefon = self.tel_input.text().strip()
        eposta = self.eposta_input.text().strip()
        adres = self.adres_input.text().strip()
        kayit_tarihi = self.tarih_input.date().toString('dd.MM.yyyy')
        aciklama = self.aciklama_input.toPlainText().strip()
        if not ad or not soyad:
            QMessageBox.warning(self, 'Uyarı', 'Ad ve Soyad zorunludur!')
            return
        if self.musteri_id:
            # Güncelleme sorgusu
            conn = veritabani_baglan()
            cursor = conn.cursor()
            cursor.execute('UPDATE musteriler SET ad=?, soyad=?, telefon=?, eposta=?, adres=?, kayit_tarihi=?, aciklama=? WHERE id=?',
                (ad, soyad, telefon, eposta, adres, kayit_tarihi, aciklama, self.musteri_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Başarılı', 'Müşteri güncellendi!')
            self.accept()
        else:
            # Normal ekleme işlemi
            conn = veritabani_baglan()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO musteriler (ad, soyad, telefon, eposta, adres, kayit_tarihi, aciklama) VALUES (?, ?, ?, ?, ?, ?, ?)', (ad, soyad, telefon, eposta, adres, kayit_tarihi, aciklama))
            conn.commit()
            conn.close()
            self.ad_input.clear()
            self.soyad_input.clear()
            self.tel_input.clear()
            self.eposta_input.clear()
            self.adres_input.clear()
            self.tarih_input.setDate(QDate.currentDate())
            self.aciklama_input.clear()
            QMessageBox.information(self, 'Başarılı', 'Müşteri eklendi!') 