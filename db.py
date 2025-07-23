import sqlite3
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def veritabani_baglan():
    conn = sqlite3.connect(resource_path('cari_hesap.db'))
    return conn

def musteri_tablosu_olustur():
    conn = veritabani_baglan()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS musteriler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT NOT NULL,
            soyad TEXT NOT NULL,
            telefon TEXT,
            eposta TEXT,
            adres TEXT,
            kayit_tarihi TEXT,
            aciklama TEXT
        )
    ''')
    conn.commit()
    conn.close()

def urun_tablosu_olustur():
    conn = veritabani_baglan()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urunler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            urun_adi TEXT NOT NULL,
            barkod TEXT NOT NULL,
            birim TEXT,
            miktar INTEGER,
            alis_fiyat REAL,
            satis_fiyat REAL,
            alis_tarihi TEXT,
            aciklama TEXT
        )
    ''')
    conn.commit()
    conn.close()

def vadeli_satislar_tablosu_olustur():
    conn = veritabani_baglan()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vadeli_satislar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            musteri_id INTEGER,
            is_ TEXT,
            fiyat REAL,
            miktar INTEGER,
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
    conn.commit()
    conn.close()

if __name__ == '__main__':
    musteri_tablosu_olustur()
    urun_tablosu_olustur()
    vadeli_satislar_tablosu_olustur() 