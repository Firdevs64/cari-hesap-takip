import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenuBar, QMessageBox, QLabel, QHeaderView, QDialog
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from db import musteri_tablosu_olustur, urun_tablosu_olustur, vadeli_satislar_tablosu_olustur
from customer_dialog import CustomerDialog
from customer_list_dialog import CustomerListDialog
from product_dialog import ProductDialog
from product_add_dialog import ProductAddDialog
from product_update_dialog import ProductUpdateDialog
from product_list_dialog import ProductListDialog
from customer_update_dialog import CustomerUpdateDialog
from vadelisatis_dialog import VadeliSatisDialog
from vadeli_satis_list_dialog import VadeliSatisListDialog
from customer_search_dialog import CustomerSearchDialog

def resource_path(relative_path):
    """PyInstaller ile çalışırken dosya yolunu bulmak için kullanılır."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cari Hesap Takip Programı')
        self.setGeometry(100, 100, 900, 600)
        self.initUI()
        self.show_logo()

    def initUI(self):
        self.setStyleSheet("""
QMenuBar {
    font-size: 20px;
}
QMenuBar::item {
    padding: 7px 22px;    /* Menü başlıkları arası boşluk */
}
QMenu {
    font-size: 14px;
}
QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit, QPushButton, QSpinBox, QDoubleSpinBox {
    font-size: 13px;
    min-height: 26px;
}
QPushButton {
    font-size: 14px;
    min-height: 28px;
}
""")
        menubar = self.menuBar()
        # Müşteri Menüsü
        musteri_menu = menubar.addMenu('Müşteri İşlemleri')
        tick_icon = QIcon(resource_path("tick.png"))  # Dosya adını doğru yaz

        musteri_ekle = QAction(tick_icon, 'Müşteri Ekle', self)
        musteri_ekle.triggered.connect(self.musteri_ekle)
        musteri_menu.addAction(musteri_ekle)

        musteri_listele = QAction(tick_icon, 'Müşterileri Listele', self)
        musteri_listele.triggered.connect(self.musteri_listele)
        musteri_menu.addAction(musteri_listele)
        # Ürün Menüsü
        urun_menu = menubar.addMenu('Ürün İşlemleri')
        urun_ekle = QAction(tick_icon, 'Ürün Ekle', self)
        urun_ekle.triggered.connect(self.urun_ekle)
        urun_menu.addAction(urun_ekle)
        urun_listele = QAction(tick_icon, 'Ürünleri Listele', self)
        urun_listele.triggered.connect(self.urun_listele)
        urun_menu.addAction(urun_listele)
        # Hesap Menüsü
        hesap_menu = menubar.addMenu('Hesap İşlemleri')
        vadeli_satis = QAction(tick_icon, 'Vadeli Satış', self)
        vadeli_satis.triggered.connect(self.vadeli_satis_ac)
        hesap_menu.addAction(vadeli_satis)
        vadeli_satis_listele = QAction(tick_icon, 'Vadeli Satışları Listele', self)
        vadeli_satis_listele.triggered.connect(self.vadeli_satis_listele)
        hesap_menu.addAction(vadeli_satis_listele)

    def musteri_ekle(self):
        dialog = CustomerDialog(self)
        dialog.exec_()

    def musteri_listele(self):
        dialog = CustomerListDialog(self)
        dialog.exec_()

    def urun_ekle(self):
        dialog = ProductAddDialog(self)
        dialog.exec_()
    
    def urun_guncelle(self):
        dialog = ProductUpdateDialog(self)
        dialog.exec_()
    
    def urun_listele(self):
        dialog = ProductListDialog(self)
        dialog.exec_()

    def musteri_guncelle(self):
        dialog = CustomerUpdateDialog(self)
        dialog.exec_()

    def vadeli_satis_ac(self):
        dialog = VadeliSatisDialog(self)
        dialog.exec_()

    def vadeli_satis_listele(self):
        dialog = VadeliSatisListDialog(self)
        dialog.exec_()

    def show_logo(self):
        label = QLabel(self)
        pixmap = QPixmap(resource_path("grafixajans.jpg"))
        
        # Ana pencere boyutunu al
        window_size = self.size()
        
        # Pixmap'i ana pencere boyutuna uygun şekilde ölçeklendir
        # Tam ekranı kaplayacak şekilde ölçeklendirme
        scaled_pixmap = pixmap.scaled(
            window_size.width(),  # Tam genişlik
            window_size.height() - 30,  # Menü barı için 30px boşluk bırak
            Qt.KeepAspectRatio,  # Oranları koru
            Qt.SmoothTransformation  # Kaliteli ölçeklendirme
        )
        
        label.setPixmap(scaled_pixmap)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("background-color: white;")  # Arka plan rengi ekle
        self.setCentralWidget(label)

    def resizeEvent(self, event):
        """Pencere boyutu değiştiğinde logoyu yeniden boyutlandır"""
        super().resizeEvent(event)
        if hasattr(self, 'centralWidget') and self.centralWidget():
            self.show_logo()

if __name__ == '__main__':
    musteri_tablosu_olustur()
    urun_tablosu_olustur()
    vadeli_satislar_tablosu_olustur()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())