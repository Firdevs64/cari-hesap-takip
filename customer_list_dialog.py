from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
from db import veritabani_baglan
from customer_update_dialog import CustomerUpdateDialog
from customer_dialog import CustomerDialog
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout

class CustomerListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Müşteri Listesi')
        self.setMinimumWidth(900)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initTable()
        self.initButtons()
        self.loadCustomers()
        self.table.cellDoubleClicked.connect(self.showCustomerDetails)

    def initTable(self):
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['ID', 'Ad', 'Soyad', 'Telefon', 'E-posta', 'Adres', 'Kayıt Tarihi', 'Açıklama'])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.layout.addWidget(self.table)

    def initButtons(self):
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.guncelle_btn = QPushButton('Müşteriyi Güncelle')
        self.guncelle_btn.clicked.connect(self.updateCustomer)
        btn_layout.addWidget(self.guncelle_btn)
        self.sil_btn = QPushButton('Müşteriyi Sil')
        self.sil_btn.clicked.connect(self.deleteCustomer)
        btn_layout.addWidget(self.sil_btn)
        self.layout.addLayout(btn_layout)

    def loadCustomers(self):
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM musteriler')
        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(self.table.columnCount() - 1, QHeaderView.Stretch)
        for i in range(self.table.columnCount() - 1):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        conn.close()

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

    def updateCustomer(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen güncellemek için bir müşteri seçin!')
            return
        musteri_id = self.table.item(selected, 0).text()
        dialog = CustomerDialog(self, musteri_id=musteri_id)
        if dialog.exec_():
            self.loadCustomers()

    def showCustomerDetails(self, row, col):
        musteri_id = self.table.item(row, 0).text()
        dialog = QDialog(self)
        dialog.setWindowTitle('Müşteri Detayları')
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(400)  # Pencereyi biraz daha büyük başlat
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        # Müşteri bilgileri
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('SELECT ad, soyad, telefon, eposta, adres, kayit_tarihi, aciklama FROM musteriler WHERE id=?', (musteri_id,))
        customer = cursor.fetchone()
        info_group = QGroupBox('Müşteri Bilgileri')
        form = QFormLayout()
        form.addRow('Ad:', QLabel(customer[0]))
        form.addRow('Soyad:', QLabel(customer[1]))
        form.addRow('Telefon:', QLabel(customer[2]))
        form.addRow('E-posta:', QLabel(customer[3]))
        form.addRow('Adres:', QLabel(customer[4]))
        form.addRow('Kayıt Tarihi:', QLabel(customer[5]))
        form.addRow('Açıklama:', QLabel(customer[6]))
        info_group.setLayout(form)
        layout.addWidget(info_group)
        # Vadeli satışlar
        cursor.execute('SELECT is_, fiyat, miktar, birim, islem_turu, tarih, borc, alacak, bakiye, vade_tarihi, aciklama FROM vadeli_satislar WHERE musteri_id=?', (musteri_id,))
        sales = cursor.fetchall()
        sales_table = QTableWidget()
        sales_table.setColumnCount(11)
        sales_table.setHorizontalHeaderLabels(['Yapılan İş', 'Fiyat', 'Miktar', 'Birim', 'İşlem Türü', 'Tarih', 'Borç', 'Alacak', 'Bakiye', 'Vade Tarihi', 'Açıklama'])
        sales_table.setRowCount(len(sales))
        for row_idx, row in enumerate(sales):
            for col_idx, value in enumerate(row):
                sales_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        sales_table.resizeColumnsToContents()
        sales_table.setMinimumHeight(200)  # Tabloyu daha büyük başlat
        sales_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Düzenlemeyi engelle
        sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Yana doğru tam doldur
        layout.addWidget(sales_table)
        # Toplam bakiye
        toplam_bakiye = sum([float(row[8]) for row in sales]) if sales else 0.0
        toplam_bakiye_label = QLabel(f'Toplam Bakiye: {toplam_bakiye:.2f}')
        toplam_bakiye_label.setStyleSheet('font-weight: bold; font-size: 14px; margin-top: 8px;')
        layout.addWidget(toplam_bakiye_label)
        # Stretch ayarları
        layout.setStretch(0, 0)  # info_group
        layout.setStretch(1, 1)  # sales_table
        layout.setStretch(2, 0)  # toplam_bakiye_label
        conn.close()
        dialog.exec_()