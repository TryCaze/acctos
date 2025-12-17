from datetime import datetime
import tkinter.messagebox as messagebox

def getAllTransactions(cursor, filters=None):
    """
    Get all transactions with optional filters
    filters = {
        'start_date': '2024-01-01',
        'end_date': '2024-01-31',
        'vrsta': 'prihod' or 'rashod',
        'racunId': 1,
        'kategorijaId': 2,
        'uskladeno': 0 or 1
    }
    """
    query = """
        SELECT t.*, r.naziv as racunNaziv, k.ime as kategorijaNaziv 
        FROM ACCTOSTRANSAKCIJE t
        LEFT JOIN ACCTOSRACUNI r ON t.racunId = r.id
        LEFT JOIN ACCTOSKATEGORIJE k ON t.kategorijaId = k.id
        WHERE 1=1
    """
    params = []
    
    if filters:
        if filters.get('start_date'):
            query += " AND t.datum >= ?"
            params.append(filters['start_date'])
        if filters.get('end_date'):
            query += " AND t.datum <= ?"
            params.append(filters['end_date'])
        if filters.get('vrsta'):
            query += " AND t.vrsta = ?"
            params.append(filters['vrsta'])
        if filters.get('racunId'):
            query += " AND t.racunId = ?"
            params.append(filters['racunId'])
        if filters.get('kategorijaId'):
            query += " AND t.kategorijaId = ?"
            params.append(filters['kategorijaId'])
        if filters.get('uskladeno') is not None:
            query += " AND t.uskladeno = ?"
            params.append(filters['uskladeno'])
    
    query += " ORDER BY t.datum DESC, t.id DESC"
    
    cursor.execute(query, params)
    return cursor.fetchall()

def addTransaction(cursor, conn, datum, iznos, vrsta, racunId, dobavljacKlijent=None, opis=None, kategorijaId=None, brojRacuna=None, uskladeno=0, iznosPoreza=0, napomene=None):
    try:
        cursor.execute("""
            INSERT INTO ACCTOSTRANSAKCIJE 
            (datum, brojRacuna, dobavljacKlijent, opis, iznos, vrsta, 
             racunId, kategorijaId, uskladeno, iznosPoreza, napomene)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (datum, brojRacuna, dobavljacKlijent, opis, iznos, vrsta,
              racunId, kategorijaId, uskladeno, iznosPoreza, napomene))
        
        # Update account balance
        if vrsta == 'prihod':
            cursor.execute("""
                UPDATE ACCTOSRACUNI 
                SET trenutacniIznos = trenutacniIznos + ? 
                WHERE id = ?
            """, (iznos, racunId))
        else:  # rashod
            cursor.execute("""
                UPDATE ACCTOSRACUNI 
                SET trenutacniIznos = trenutacniIznos - ? 
                WHERE id = ?
            """, (iznos, racunId))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error adding transaction: {e}")
        return None
    
def updateTransaction(cursor, conn, transakcijaId, **kwargs):
    try:
        # Get original transaction
        cursor.execute("SELECT * FROM ACCTOSTRANSAKCIJE WHERE id = ?", (transakcijaId,))
        original = cursor.fetchone()
        
        if not original:
            return False
        
        # Revert original balance change
        if original['vrsta'] == 'prihod':
            cursor.execute("""
                UPDATE ACCTOSRACUNI 
                SET trenutacniIznos = trenutacniIznos - ? 
                WHERE id = ?
            """, (original['iznos'], original['racunId']))
        else:  # rashod
            cursor.execute("""
                UPDATE ACCTOSRACUNI 
                SET trenutacniIznos = trenutacniIznos + ? 
                WHERE id = ?
            """, (original['iznos'], original['racunId']))
        
        # Build update query
        updates = []
        params = []
        
        allowed_fields = ['datum', 'brojRacuna', 'dobavljacKlijent', 'opis', 
                         'iznos', 'vrsta', 'racunId', 'kategorijaId', 
                         'uskladeno', 'iznosPoreza', 'napomene']
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if updates:
            query = f"UPDATE ACCTOSTRANSAKCIJE SET {', '.join(updates)} WHERE id = ?"
            params.append(transakcijaId)
            cursor.execute(query, tuple(params))
        
        # Get updated values (or original if not changed)
        updated_values = kwargs.copy()
        for field in allowed_fields:
            if field not in updated_values:
                updated_values[field] = original[field]
        
        # Apply new balance change
        if updated_values['vrsta'] == 'prihod':
            cursor.execute("""
                UPDATE ACCTOSRACUNI 
                SET trenutacniIznos = trenutacniIznos + ? 
                WHERE id = ?
            """, (updated_values['iznos'], updated_values['racunId']))
        else:  # rashod
            cursor.execute("""
                UPDATE ACCTOSRACUNI 
                SET trenutacniIznos = trenutacniIznos - ? 
                WHERE id = ?
            """, (updated_values['iznos'], updated_values['racunId']))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error updating transaction: {e}")
        conn.rollback()
        return False

def getTransactionById(cursor, transakcijaId):
    cursor.execute("""
        SELECT t.*, r.naziv as racunNaziv, k.ime as kategorijaNaziv 
        FROM ACCTOSTRANSAKCIJE t
        LEFT JOIN ACCTOSRACUNI r ON t.racunId = r.id
        LEFT JOIN ACCTOSKATEGORIJE k ON t.kategorijaId = k.id
        WHERE t.id = ?
    """, (transakcijaId,))
    return cursor.fetchone()

def deleteTransaction(cursor, conn, transakcijaId):
    try:
        # First get transaction details
        cursor.execute("SELECT * FROM ACCTOSTRANSAKCIJE WHERE id = ?", (transakcijaId,))
        trans = cursor.fetchone()
        
        if not trans:
            return False
        
        # Revert the balance change
        if trans['vrsta'] == 'prihod':
            cursor.execute("""
                UPDATE ACCTOSRACUNI 
                SET trenutacniIznos = trenutacniIznos - ? 
                WHERE id = ?
            """, (trans['iznos'], trans['racunId']))
        else:  # rashod
            cursor.execute("""
                UPDATE ACCTOSRACUNI 
                SET trenutacniIznos = trenutacniIznos + ? 
                WHERE id = ?
            """, (trans['iznos'], trans['racunId']))
        
        # Delete the transaction
        cursor.execute("DELETE FROM ACCTOSTRANSAKCIJE WHERE id = ?", (transakcijaId,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting transaction: {e}")
        return False

def toggleReconciliation(cursor, conn, transakcijaId):
    try:
        cursor.execute("""
            UPDATE ACCTOSTRANSAKCIJE 
            SET uskladeno = NOT uskladeno 
            WHERE id = ?
        """, (transakcijaId,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error toggling reconciliation: {e}")
        return False

def getAccounts(cursor):
    cursor.execute("SELECT id, naziv FROM ACCTOSRACUNI ORDER BY naziv")
    return cursor.fetchall()

def getCategories(cursor, vrsta=None):
    query = "SELECT id, ime FROM ACCTOSKATEGORIJE"
    params = []
    if vrsta:
        query += " WHERE vrsta = ?"
        params.append(vrsta)
    query += " ORDER BY ime"
    
    cursor.execute(query, params)
    return cursor.fetchall()

def getTransactionSummary(cursor, filters=None):
    transactions = getAllTransactions(cursor, filters)
    
    total_prihod = sum(t['iznos'] for t in transactions if t['vrsta'] == 'prihod')
    total_rashod = sum(t['iznos'] for t in transactions if t['vrsta'] == 'rashod')
    neto = total_prihod - total_rashod
    
    return {
        'total_prihod': total_prihod,
        'total_rashod': total_rashod,
        'neto': neto,
        'count': len(transactions)
    }