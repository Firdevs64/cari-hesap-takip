from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QHeaderView
from db import veritabani_baglan
from vadeli_satis_update_dialog import VadeliSatisUpdateDialog

class VadeliSatisListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Vadeli Satışları Listele')
        self.setMinimumWidth(900)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initTable()
        self.initButtons()
        self.loadSales()

    def initTable(self):
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels(['ID', 'Müşteri', 'Yapılan İş', 'Fiyat', 'Miktar', 'Birim', 'İşlem Türü', 'Tarih', 'Borç', 'Alacak', 'Bakiye', 'Vade Tarihi', 'Açıklama'])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(12, QHeaderView.Stretch)
        for i in range(self.table.columnCount()):
            if i != 12:
                self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.table.cellDoubleClicked.connect(self.showFullDescription)
        self.layout.addWidget(self.table)

    def initButtons(self):
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.guncelle_btn = QPushButton('Satışı Güncelle')
        self.guncelle_btn.clicked.connect(self.updateSale)
        btn_layout.addWidget(self.guncelle_btn)
        self.sil_btn = QPushButton('Satışı Sil')
        self.sil_btn.clicked.connect(self.deleteSale)
        btn_layout.addWidget(self.sil_btn)
        self.layout.addLayout(btn_layout)

    def loadSales(self):
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.id, m.ad || ' ' || m.soyad, v.is_, v.fiyat, v.miktar, v.birim, v.islem_turu, v.tarih, v.borc, v.alacak, v.bakiye, v.vade_tarihi, v.aciklama
            FROM vadeli_satislar v
            LEFT JOIN musteriler m ON v.musteri_id = m.id
        ''')
        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                if value is None:
                    value = ""
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        conn.close()

    def deleteSale(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek için bir satış seçin!')
            return
        satis_id = self.table.item(selected, 0).text()
        musteri = self.table.item(selected, 1).text()
        cevap = QMessageBox.question(self, 'Onay', f"{musteri} müşterisinin bu vadeli satış kaydını silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            conn = veritabani_baglan()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM vadeli_satislar WHERE id = ?', (satis_id,))
            conn.commit()
            conn.close()
            self.loadSales()
            QMessageBox.information(self, 'Başarılı', 'Satış kaydı silindi!') 

    def updateSale(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen güncellemek için bir satış seçin!')
            return
        satis_id = self.table.item(selected, 0).text()
        dialog = VadeliSatisUpdateDialog(satis_id, self)
        if dialog.exec_():
            self.loadSales()

    def showFullDescription(self, row, col):
        if col == 12:  # Açıklama sütunu
            aciklama = self.table.item(row, col).text()
            QMessageBox.information(self, "Açıklama", aciklama) 