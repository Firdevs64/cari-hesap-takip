from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QMessageBox
from PyQt5.QtCore import QDate
from db import veritabani_baglan

class VadeliSatisDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Vadeli Satış')
        self.setMinimumWidth(500)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initForm()
        self.loadCustomers()

    def initForm(self):
        form_layout = QFormLayout()
        self.musteri_combo = QComboBox()
        self.is_input = QComboBox()  # QLineEdit yerine QComboBox
        self.is_input.currentIndexChanged.connect(self.urunSecildi)  # Ürün seçilince fiyatı doldur
        self.fiyat_input = QDoubleSpinBox()
        self.fiyat_input.setDecimals(2)
        self.fiyat_input.setMinimum(0)
        self.fiyat_input.setMaximum(1000000)
        self.miktar_input = QDoubleSpinBox()
        self.miktar_input.setDecimals(2)
        self.miktar_input.setMinimum(0)
        self.miktar_input.setMaximum(999999)
        self.birim_input = QComboBox()
        self.birim_input.addItems(['Adet', 'cm', 'metre', 'metrekare', 'gram', 'kilo', 'koli'])
        self.islem_turu_input = QComboBox()
        self.islem_turu_input.addItems(['Nakit', 'Kart', 'Havale/EFT'])
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
        self.kaydet_btn.clicked.connect(self.saveSale)
        # Bakiye otomatik hesaplama
        self.borc_input.valueChanged.connect(self.updateBakiye)
        self.alacak_input.valueChanged.connect(self.updateBakiye)
        self.fiyat_input.valueChanged.connect(self.updateBorc)
        self.miktar_input.valueChanged.connect(self.updateBorc)
        form_layout.addRow('Müşteri:', self.musteri_combo)
        form_layout.addRow('Yapılan İş:', self.is_input)
        form_layout.addRow('Fiyat:', self.fiyat_input)
        form_layout.addRow('Miktar:', self.miktar_input)
        form_layout.addRow('Birim:', self.birim_input)
        form_layout.addRow('İşlem Türü:', self.islem_turu_input)
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
        self.loadProducts()  # Ürünleri de yükle

    def loadProducts(self):
        conn = veritabani_baglan()
        cursor = conn.cursor()
        cursor.execute('SELECT urun_adi, satis_fiyat FROM urunler')
        self.products = cursor.fetchall()
        self.is_input.clear()  # Varsayılan seçenek
        for p in self.products:
            self.is_input.addItem(p[0], p[1])  # Ürün adı görünür, satış fiyatı veri olarak saklanır
        conn.close()

    def urunSecildi(self, index):
        if index > 0:  # 0 = "Ürün Seçin..." seçeneği
            fiyat = self.is_input.currentData()  # Seçilen ürünün fiyatı
            if fiyat is not None:
                self.fiyat_input.setValue(float(fiyat))

    def updateBakiye(self):
        borc = self.borc_input.value()
        alacak = self.alacak_input.value()
        self.bakiye_input.setText(f"{borc - alacak:.2f}")

    def updateBorc(self):
        fiyat = self.fiyat_input.value()
        miktar = self.miktar_input.value()
        self.borc_input.setValue(fiyat * miktar)

    def saveSale(self):
        musteri_id = self.musteri_combo.currentData()
        is_ = self.is_input.currentText()  # Seçilen ürünün adı
        if is_ == "Ürün Seçin...":
            QMessageBox.warning(self, 'Uyarı', 'Lütfen bir ürün seçin!')
            return
        fiyat = self.fiyat_input.value()
        miktar = self.miktar_input.value()
        birim = self.birim_input.currentText()
        islem_turu = self.islem_turu_input.currentText()
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vadeli_satislar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musteri_id INTEGER,
                is_ TEXT,
                fiyat REAL,
                miktar REAL,
                birim TEXT,
                islem_turu TEXT,
                tarih TEXT,
                borc REAL,
                alacak REAL,
                bakiye REAL,
                vade_tarihi TEXT,
                aciklama TEXT
            )
        ''')
        cursor.execute('''INSERT INTO vadeli_satislar (musteri_id, is_, fiyat, miktar, birim, islem_turu, tarih, borc, alacak, bakiye, vade_tarihi, aciklama) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (musteri_id, is_, fiyat, miktar, birim, islem_turu, tarih, borc, alacak, bakiye, vade_tarihi, aciklama))
        conn.commit()
        conn.close()
        QMessageBox.information(self, 'Başarılı', 'Vadeli satış kaydedildi!')
        self.close() 