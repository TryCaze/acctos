import sqlite3
from datetime import datetime
import pandas as pd

class Database:
    def __init__(self, dbName="acctos.db"):
        self.conn = sqlite3.connect(dbName)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.createTables()

    def createTables(self):
        #RACUNI
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ACCTOSRACUNI (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv TEXT NOT NULL UNIQUE,
            vrsta TEXT NOT NULL DEFAULT 'tekući',
            brojRacuna TEXT,
            imeBanke TEXT,
            pocetniIznos, REAL DEFAULT 0,
            trenutacniIznos REAL DEFAULT 0,
            biljeska TEXT,
            kreiranDatuma TEXT DEFAULT CURRENT_TIMESTAMP
        )

        """)

        #KATEGORIJE
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ACCTOSKATEGORIJE (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ime TEXT NOT NULL UNIQUE,
            vrsta TEXT NOT NULL CHECK(vrsta IN('prihod', 'rashod')),
            poreznoPriznato BOOLEAN DEFAULT 1,
            opis TEXT
        )

        """)

        #TRANSAKCIJE
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ACCTOSTRANSAKCIJE (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datum TEXT NOT NULL,
            brojRacuna TEXT,
            dobavljacKlijent TEXT,
            opis TEXT,
            iznos REAL NOT NULL,
            vrsta TEXT NOT NULL CHECK(vrsta IN('prihod', 'rashod')),
            racunId INTEGER,
            kategorijaId INTEGER,
            uskladeno BOOLEAN DEFAULT 0,
            iznosPoreza REAL DEFAULT 0,
            napomene TEXT,
            FOREIGN KEY(racunId) REFERENCES ACCTOSRACUNI(id),
            FOREIGN KEY(kategorijaId)  REFERENCES ACCTOSKATEGORIJE(id)
        )

        """)

        #USKLADENJE
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ACCTOSUSKLADENJE (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            racunId INTEGER,
            datumIzvitaka TEXT,
            stanjeIzvitaka REAL,
            datumUskladenja TEXT,
            napomene TEXT,
            FOREIGN KEY(racunId) REFERENCES ACCTOSRACUNI(id)
        )
                            
        """)

        #ZALIHE ARTIKALA
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ARTIKLZALIHE (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT NOT NULL UNIQUE,
            naziv TEXT NOT NULL,
            opis TEXT,
            kategorija TEXT,
            jedinica TEXT DEFAULT 'komad',
            nabavnaCijena REAL NOT NULL DEFAULT 0,
            prodajnaCijena REAL NOT NULL DEFAULT 0,
            minimalnaKolicina INTEGER DEFAULT 10,
            idealnaKolicina INTEGER DEFAULT 50,
            lokacija TEXT,
            dobavljacId INTEGER,
            napomene TEXT,
            datumKreiranja TEXT DEFAULT CURRENT_TIMESTAMP,
            zadnjeAzuriranje TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(dobavljacId) REFERENCES ACCTOSRACUNI(id)
        )
                            
        """)

        #ZALIHE STANJE
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS StanjeZalihe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artiklId INTEGER NOT NULL,
            lokacija TEXT,
            brojSerije TEXT,
            kolicina INTEGER NOT NULL DEFAULT 0,
            rokTrajanja TEXT,
            nabavnaCijena REAL,
            napomene TEXT,
            datumKreiranja TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(artiklId) REFERENCES ARTIKLZALIHE(id)
        )
                            
        """)

        #ZALIHE TRANSAKCIJE
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ZALIHATRANSAKCIJA (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datum TEXT NOT NULL,
            tipTransakcije TEXT NOT NULL CHECK(tipTransakcije IN ('nabava','prodaja','ispravak','povrat','premjestanje','otpis')),
            artiklId INTEGER NOT NULL,
            kolicina INTEGER NOT NULL,
            jedinicnaCijena REAL NOT NULL,
            ukupanIznos REAL NOT NULL,
            povezaniTransakcijaId INTEGER,
            referentniBroj TEXT,
            dobavljacKupac TEXT,
            izLokacije TEXT,
            uLokaciju TEXT,
            napomene TEXT,
            datumKreiranja TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(artiklId) REFERENCES ArtikliZalihe(id),
            FOREIGN KEY(povezaniTransakcijaId) REFERENCES ACCTOSTRANSAKCIJE (id)
        )

        """)

        #DOBAVLJACI
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS DOBAVLJACI (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            racunId INTEGER NOT NULL,
            kontaktOsoba TEXT,
            telefon TEXT,
            email TEXT,
            uvjetiPlacanja TEXT DEFAULT 'Net 30',
            rokIsporuke INTEGER DEFAULT 7,
            ocjena INTEGER DEFAULT 5,
            napomene TEXT,
            FOREIGN KEY(racunId) REFERENCES ACCTOSRACUNI(id)
        )
                            
        """)

        self.conn.commit()
