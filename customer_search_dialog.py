from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QGroupBox, QFormLayout
from db import veritabani_baglan

class CustomerSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Müşteri Ara')
        self.setMinimumWidth(800)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initSearch()
        self.info_group = None
        self.sales_table = None

    def initSearch(self):
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Ad veya Soyad girin...')
        self.search_btn = QPushButton('Ara')
        self.search_btn.clicked.connect(self.searchCustomer)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        self.layout.addLayout(search_layout)

    def searchCustomer(self):
        name = self.search_input.text().strip().lower()
        if not name:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen ad veya soyad girin!')
            return
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, ad, soyad, telefon, eposta, adres, kayit_tarihi, aciklama FROM musteriler WHERE LOWER(ad) LIKE ? OR LOWER(soyad) LIKE ?",
            (f"%{name.lower()}%", f"%{name.lower()}%")
        )
        customer = cursor.fetchone()
        if not customer:
            QMessageBox.information(self, 'Sonuç', 'Müşteri bulunamadı!')
            conn.close()
            return
        self.showCustomerInfo(customer)
        # Vadeli satışları getir
        cursor.execute("SELECT is_, fiyat, miktar, birim, islem_turu, tarih, borc, alacak, bakiye, vade_tarihi, aciklama FROM vadeli_satislar WHERE musteri_id=?", (customer[0],))
        sales = cursor.fetchall()
        self.showSales(sales)
        conn.close()

    def showCustomerInfo(self, customer):
        if self.info_group:
            self.layout.removeWidget(self.info_group)
            self.info_group.deleteLater()
        self.info_group = QGroupBox('Müşteri Bilgileri')
        form = QFormLayout()
        form.addRow('Ad:', QLabel(customer[1]))
        form.addRow('Soyad:', QLabel(customer[2]))
        form.addRow('Telefon:', QLabel(customer[3]))
        form.addRow('E-posta:', QLabel(customer[4]))
        form.addRow('Adres:', QLabel(customer[5]))
        form.addRow('Kayıt Tarihi:', QLabel(customer[6]))
        form.addRow('Açıklama:', QLabel(customer[7]))
        self.info_group.setLayout(form)
        self.layout.addWidget(self.info_group)

    def showSales(self, sales):
        if self.sales_table:
            self.layout.removeWidget(self.sales_table)
            self.sales_table.deleteLater()
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(11)
        self.sales_table.setHorizontalHeaderLabels(['Yapılan İş', 'Fiyat', 'Miktar', 'Birim', 'İşlem Türü', 'Tarih', 'Borç', 'Alacak', 'Bakiye', 'Vade Tarihi', 'Açıklama'])
        self.sales_table.setRowCount(len(sales))
        for row_idx, row in enumerate(sales):
            for col_idx, value in enumerate(row):
                self.sales_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        self.sales_table.resizeColumnsToContents()
        self.layout.addWidget(self.sales_table) 