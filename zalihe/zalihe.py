from datetime import datetime

def getAllItems(cursor):
    cursor.execute("""
        SELECT a.*, 
               COALESCE((SELECT SUM(kolicina) FROM StanjeZalihe s WHERE s.artiklId = a.id), 0) AS trenutno_stanje
        FROM ARTIKLZALIHE a
        ORDER BY a.naziv
    """)
    return [dict(row) for row in cursor.fetchall()]

def getItemById(cursor, artiklId):
    cursor.execute("SELECT * FROM ARTIKLZALIHE WHERE id = ?", (artiklId,))
    row = cursor.fetchone()
    return dict(row) if row else None

def addItem(cursor, conn, data):
    """
    data: dict with keys sku, naziv, opis, kategorija, jedinica, nabavnaCijena, prodajnaCijena,
          minimalnaKolicina, idealnaKolicina, lokacija, dobavljacId, napomene
    """
    try:
        cursor.execute("""
            INSERT INTO ARTIKLZALIHE (sku, naziv, opis, kategorija, jedinica, nabavnaCijena, prodajnaCijena,
                                      minimalnaKolicina, idealnaKolicina, lokacija, dobavljacId, napomene)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('sku'),
            data.get('naziv'),
            data.get('opis'),
            data.get('kategorija'),
            data.get('jedinica'),
            float(data.get('nabavnaCijena') or 0),
            float(data.get('prodajnaCijena') or 0),
            int(data.get('minimalnaKolicina') or 0),
            int(data.get('idealnaKolicina') or 0),
            data.get('lokacija'),
            data.get('dobavljacId'),
            data.get('napomene')
        ))
        conn.commit()
        return True, "Artikl uspješno dodan."
    except Exception as e:
        return False, f"Pogreška prilikom dodavanja artikla: {e}"

def editItem(cursor, conn, artiklId, data):
    try:
        cursor.execute("""
            UPDATE ARTIKLZALIHE SET
                sku = ?, naziv = ?, opis = ?, kategorija = ?, jedinica = ?,
                nabavnaCijena = ?, prodajnaCijena = ?, minimalnaKolicina = ?, idealnaKolicina = ?,
                lokacija = ?, dobavljacId = ?, napomene = ?, zadnjeAzuriranje = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            data.get('sku'),
            data.get('naziv'),
            data.get('opis'),
            data.get('kategorija'),
            data.get('jedinica'),
            float(data.get('nabavnaCijena') or 0),
            float(data.get('prodajnaCijena') or 0),
            int(data.get('minimalnaKolicina') or 0),
            int(data.get('idealnaKolicina') or 0),
            data.get('lokacija'),
            data.get('dobavljacId'),
            data.get('napomene'),
            artiklId
        ))
        conn.commit()
        return True, "Artikl uspješno ažuriran."
    except Exception as e:
        return False, f"Pogreška prilikom ažuriranja artikla: {e}"

def deleteItem(cursor, conn, artiklId):
    # provjera povezanih transakcija / stanja
    cursor.execute("SELECT COUNT(*) as c FROM ZALIHATRANSAKCIJA WHERE artiklId = ?", (artiklId,))
    if cursor.fetchone()['c'] > 0:
        return False, "Ne možete izbrisati artikl koji ima zabilježene transakcije zaliha."
    cursor.execute("SELECT COUNT(*) as c FROM StanjeZalihe WHERE artiklId = ?", (artiklId,))
    if cursor.fetchone()['c'] > 0:
        return False, "Ne možete izbrisati artikl koji ima stanje na skladištu."
    try:
        cursor.execute("DELETE FROM ARTIKLZALIHE WHERE id = ?", (artiklId,))
        conn.commit()
        return True, "Artikl izbrisan."
    except Exception as e:
        return False, f"Pogreška prilikom brisanja artikla: {e}"

# STANJE ZALIHA
def getStockEntries(cursor, artiklId):
    cursor.execute("SELECT * FROM StanjeZalihe WHERE artiklId = ? ORDER BY datumKreiranja DESC", (artiklId,))
    return [dict(r) for r in cursor.fetchall()]

def addStockEntry(cursor, conn, artiklId, data):
    """
    data: dict with keys lokacija, brojSerije, kolicina, rokTrajanja, nabavnaCijena, napomene
    Also creates a ZALIHATRANSAKCIJA of tip 'nabava' or 'ispravak' depending on whether positive/negative.
    """
    try:
        kolicina = int(data.get('kolicina', 0))
        cursor.execute("""
            INSERT INTO StanjeZalihe (artiklId, lokacija, brojSerije, kolicina, rokTrajanja, nabavnaCijena, napomene)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            artiklId,
            data.get('lokacija'),
            data.get('brojSerije'),
            kolicina,
            data.get('rokTrajanja'),
            float(data.get('nabavnaCijena') or 0),
            data.get('napomene')
        ))
        # dodaj transakciju zaliha
        tip = 'nabava' if kolicina > 0 else 'ispravak'
        jedinicna = float(data.get('nabavnaCijena') or 0)
        ukupan = jedinicna * abs(kolicina)
        cursor.execute("""
            INSERT INTO ZALIHATRANSAKCIJA (datum, tipTransakcije, artiklId, kolicina, jedinicnaCijena, ukupanIznos,
                                          dobavljacKupac, izLokacije, uLokaciju, napomene, datumKreiranja)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            datetime.now().isoformat(),
            tip,
            artiklId,
            kolicina,
            jedinicna,
            ukupan,
            data.get('dobavljacKupac'),
            data.get('izLokacije'),
            data.get('uLokaciju'),
            data.get('napomene'),
        ))
        conn.commit()
        return True, "Stanje zaliha uspješno dodano."
    except Exception as e:
        return False, f"Pogreška prilikom dodavanja stanja: {e}"

def getInventoryTransactions(cursor, artiklId=None, limit=500):
    if artiklId:
        cursor.execute("SELECT * FROM ZALIHATRANSAKCIJA WHERE artiklId = ? ORDER BY datumKreiranja DESC LIMIT ?", (artiklId, limit))
    else:
        cursor.execute("SELECT * FROM ZALIHATRANSAKCIJA ORDER BY datumKreiranja DESC LIMIT ?", (limit,))
    return [dict(r) for r in cursor.fetchall()]

# DOBAVLJACI
def getSuppliers(cursor):
    cursor.execute("""
        SELECT d.*, r.naziv as racunNaziv FROM DOBAVLJACI d
        LEFT JOIN ACCTOSRACUNI r ON r.id = d.racunId
        ORDER BY r.naziv
    """)
    return [dict(r) for r in cursor.fetchall()]

def addSupplier(cursor, conn, data):
    try:
        cursor.execute("""
            INSERT INTO DOBAVLJACI (racunId, kontaktOsoba, telefon, email, uvjetiPlacanja, rokIsporuke, ocjena, napomene)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('racunId'),
            data.get('kontaktOsoba'),
            data.get('telefon'),
            data.get('email'),
            data.get('uvjetiPlacanja'),
            data.get('rokIsporuke'),
            data.get('ocjena'),
            data.get('napomene'),
        ))
        conn.commit()
        return True, "Dobavljač dodan."
    except Exception as e:
        return False, f"Pogreška pri dodavanju dobavljača: {e}"

# STATISTIKA
def getInventoryStatistics(cursor):
    # total artikli, artikli ispod minimalne, ukupna vrijednost zaliha (procjena)
    cursor.execute("SELECT COUNT(*) as ukupno FROM ARTIKLZALIHE")
    ukupno = cursor.fetchone()['ukupno'] or 0

    cursor.execute("""
        SELECT COUNT(*) as ispod FROM ARTIKLZALIHE a
        WHERE COALESCE((SELECT SUM(kolicina) FROM StanjeZalihe s WHERE s.artiklId = a.id),0) < a.minimalnaKolicina
    """)
    ispod = cursor.fetchone()['ispod'] or 0

    cursor.execute("""
        SELECT COALESCE(SUM(s.kolicina * COALESCE(s.nabavnaCijena, a.nabavnaCijena,0)),0) as vrijednost
        FROM StanjeZalihe s
        LEFT JOIN ARTIKLZALIHE a ON a.id = s.artiklId
    """)
    vrijednost = cursor.fetchone()['vrijednost'] or 0.0

    return {
        "ukupno_artikala": ukupno,
        "ispod_minimalne": ispod,
        "procijenjena_vrijednost": vrijednost
    }