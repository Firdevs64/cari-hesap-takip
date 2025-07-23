from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from db import veritabani_baglan
from product_add_dialog import ProductAddDialog

class ProductListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Ürün Listesi')
        self.setMinimumWidth(700)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initTable()
        self.initButtons()
        self.loadProducts()

    def initTable(self):
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['Ürün Adı', 'Barkod', 'Birim', 'Miktar', 'Alış Fiyatı', 'Satış Fiyatı', 'Alış Tarihi', 'Açıklama'])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(self.table.horizontalHeader().Stretch)
        self.layout.addWidget(self.table)

    def initButtons(self):
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.guncelle_btn = QPushButton('Ürünü Güncelle')
        self.guncelle_btn.clicked.connect(self.updateProduct)
        btn_layout.addWidget(self.guncelle_btn)
        self.sil_btn = QPushButton('Ürünü Sil')
        self.sil_btn.clicked.connect(self.deleteProduct)
        btn_layout.addWidget(self.sil_btn)
        self.layout.addLayout(btn_layout)

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

    def updateProduct(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen güncellemek için bir ürün seçin!')
            return
        urun_id = self.table.item(selected, 0).text()
        dialog = ProductAddDialog(self, urun_id=urun_id)
        if dialog.exec_():
            self.loadProducts()
