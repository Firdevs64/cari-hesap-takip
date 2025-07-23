from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTextEdit, QDateEdit, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDate
from db import veritabani_baglan

class CustomerUpdateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Müşteri Güncelle / Sil')
        self.setMinimumWidth(700)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initForm()
        self.initTable()
        self.loadCustomers()

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
        btn_layout = QHBoxLayout()
        self.guncelle_btn = QPushButton('Güncelle')
        self.guncelle_btn.clicked.connect(self.updateCustomer)
        self.sil_btn = QPushButton('Sil')
        self.sil_btn.clicked.connect(self.deleteCustomer)
        btn_layout.addWidget(self.guncelle_btn)
        btn_layout.addWidget(self.sil_btn)
        form_layout.addRow('Adı:', self.ad_input)
        form_layout.addRow('Soyadı:', self.soyad_input)
        form_layout.addRow('Telefon:', self.tel_input)
        form_layout.addRow('E-posta:', self.eposta_input)
        form_layout.addRow('Adres:', self.adres_input)
        form_layout.addRow('Kayıt Tarihi:', self.tarih_input)
        form_layout.addRow('Açıklama:', self.aciklama_input)
        form_layout.addRow(btn_layout)
        self.layout.addLayout(form_layout)

    def initTable(self):
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['ID', 'Ad', 'Soyad', 'Telefon', 'E-posta', 'Adres', 'Kayıt Tarihi', 'Açıklama'])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.cellClicked.connect(self.fillFormFromTable)
        self.table.horizontalHeader().setSectionResizeMode(self.table.horizontalHeader().Stretch)
        self.layout.addWidget(self.table)

    def loadCustomers(self):
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('SELECT id, ad, soyad, telefon, eposta, adres, kayit_tarihi, aciklama FROM musteriler')
        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        conn.close()

    def fillFormFromTable(self, row, col):
        self.ad_input.setText(self.table.item(row, 1).text())
        self.soyad_input.setText(self.table.item(row, 2).text())
        self.tel_input.setText(self.table.item(row, 3).text())
        self.eposta_input.setText(self.table.item(row, 4).text())
        self.adres_input.setText(self.table.item(row, 5).text())
        tarih = QDate.fromString(self.table.item(row, 6).text(), 'dd.MM.yyyy')
        if tarih.isValid():
            self.tarih_input.setDate(tarih)
        else:
            self.tarih_input.setDate(QDate.currentDate())
        self.aciklama_input.setText(self.table.item(row, 7).text())

    def updateCustomer(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen güncellemek için bir müşteri seçin!')
            return
        ad = self.ad_input.text().strip()
        soyad = self.soyad_input.text().strip()
        telefon = self.tel_input.text().strip()
        eposta = self.eposta_input.text().strip()
        adres = self.adres_input.text().strip()
        kayit_tarihi = self.tarih_input.date().toString('dd.MM.yyyy')
        aciklama = self.aciklama_input.toPlainText().strip()
        musteri_id = self.table.item(selected, 0).text()
        if not ad or not soyad:
            QMessageBox.warning(self, 'Uyarı', 'Ad ve Soyad zorunludur!')
            return
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('''UPDATE musteriler SET ad=?, soyad=?, telefon=?, eposta=?, adres=?, kayit_tarihi=?, aciklama=? WHERE id=?''',
                       (ad, soyad, telefon, eposta, adres, kayit_tarihi, aciklama, musteri_id))
        conn.commit()
        conn.close()
        self.loadCustomers()
        QMessageBox.information(self, 'Başarılı', 'Müşteri güncellendi!')

    def deleteCustomer(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek için bir müşteri seçin!')
            return
        musteri_id = self.table.item(selected, 0).text()
        ad = self.table.item(selected, 1).text()
        soyad = self.table.item(selected, 2).text()
        cevap = QMessageBox.question(self, 'Onay', f"{ad} {soyad} isimli müşteriyi silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            conn = veritabani_baglan()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM musteriler WHERE id = ?', (musteri_id,))
            conn.commit()
            conn.close()
            self.loadCustomers()
            QMessageBox.information(self, 'Başarılı', 'Müşteri silindi!') 