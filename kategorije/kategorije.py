# kategorije/kategorije.py
import tkinter.messagebox as messagebox

def getAllCategories(cursor):
    """Get all categories"""
    cursor.execute("SELECT * FROM ACCTOSKATEGORIJE ORDER BY vrsta, ime")
    return cursor.fetchall()

def getCategoryById(cursor, category_id):
    """Get a single category by ID"""
    cursor.execute("SELECT * FROM ACCTOSKATEGORIJE WHERE id = ?", (category_id,))
    return cursor.fetchone()

def addCategory(cursor, conn, ime, vrsta, poreznoPriznato=True, opis=None):
    """Add a new category"""
    try:
        cursor.execute("""
            INSERT INTO ACCTOSKATEGORIJE (ime, vrsta, poreznoPriznato, opis)
            VALUES (?, ?, ?, ?)
        """, (ime, vrsta, 1 if poreznoPriznato else 0, opis))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error adding category: {e}")
        return None

def updateCategory(cursor, conn, category_id, ime=None, vrsta=None, poreznoPriznato=None, opis=None):
    """Update a category"""
    updates = []
    params = []
    
    if ime:
        updates.append("ime = ?")
        params.append(ime)
    if vrsta:
        updates.append("vrsta = ?")
        params.append(vrsta)
    if poreznoPriznato is not None:
        updates.append("poreznoPriznato = ?")
        params.append(1 if poreznoPriznato else 0)
    if opis is not None:
        updates.append("opis = ?")
        params.append(opis)
    
    if updates:
        query = f"UPDATE ACCTOSKATEGORIJE SET {', '.join(updates)} WHERE id = ?"
        params.append(category_id)
        cursor.execute(query, tuple(params))
        conn.commit()
        return True
    return False

def deleteCategory(cursor, conn, category_id):
    """Delete a category"""
    try:
        # Check if category is used in transactions
        cursor.execute("SELECT COUNT(*) as count FROM ACCTOSTRANSAKCIJE WHERE kategorijaId = ?", (category_id,))
        result = cursor.fetchone()
        
        if result['count'] > 0:
            return False, "Kategorija se koristi u transakcijama i ne može se izbrisati!"
        
        cursor.execute("DELETE FROM ACCTOSKATEGORIJE WHERE id = ?", (category_id,))
        conn.commit()
        return True, "Kategorija uspješno izbrisana!"
    except Exception as e:
        print(f"Error deleting category: {e}")
        return False, f"Greška pri brisanju: {e}"

def getCategoriesByType(cursor, vrsta):
    """Get categories by type (prihod/rashod)"""
    cursor.execute("SELECT * FROM ACCTOSKATEGORIJE WHERE vrsta = ? ORDER BY ime", (vrsta,))
    return cursor.fetchall()

def getCategoryStatistics(cursor):
    """Get statistics about categories"""
    cursor.execute("""
        SELECT k.ime, k.vrsta, COUNT(t.id) as transaction_count, 
               COALESCE(SUM(t.iznos), 0) as total_amount
        FROM ACCTOSKATEGORIJE k
        LEFT JOIN ACCTOSTRANSAKCIJE t ON k.id = t.kategorijaId
        GROUP BY k.id
        ORDER BY k.vrsta, transaction_count DESC
    """)
    return cursor.fetchall()
