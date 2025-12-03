import pytest
from main import pripojeni_db, vytvoreni_tabulky, pridat_ukol, aktualizovat_ukol, odstranit_ukol, zobrazit_ukoly
import mysql.connector
from mysql.connector import Error
from unittest.mock import patch

# Zde jsou ponechány beze změny: test_db, clean_db, mock_input, mock_print

@pytest.fixture(scope="module")
def test_db():
    # Připojení k testovací databázi
    connection = pripojeni_db(test=True)
    if not connection:
        pytest.fail("Nepodařilo se připojit k testovací databázi.")
    cursor = connection.cursor()
    # Vytvoření testovací tabulky
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(255) NOT NULL,
            popis TEXT NOT NULL,
            stav ENUM('Nezahájeno', 'Probíhá', 'Hotovo') DEFAULT 'Nezahájeno',
            datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.commit()
    yield connection  # Předání připojení testům
    # Po testech: Smazání testovací tabulky
    cursor.execute("DROP TABLE IF EXISTS ukoly")
    connection.commit()
    cursor.close()
    connection.close()


@pytest.fixture
def clean_db(test_db):
    # Vyčištění tabulky před každým testem
    print("Čištění tabulky 'ukoly' před testem...")
    cursor = test_db.cursor()
    cursor.execute("DELETE FROM ukoly")
    test_db.commit()
    yield cursor
    cursor.close()

@pytest.fixture
def mock_input(monkeypatch):
    # Fixture pro mockování vstupu (input)
    inputs = []

    def mock_input_func(prompt=""):
        if inputs:
            print(f"Simulovaný vstup: {inputs[0]}")  # Ladicí výpis
            return inputs.pop(0)
        raise ValueError("Nebyl poskytnut žádný vstup.")

    monkeypatch.setattr("builtins.input", mock_input_func)
    return inputs

@pytest.fixture
def mock_print(monkeypatch):
    printed = []

    def mock_print_func(*args, **kwargs):
        # Přeskočí standardní výpisy z pripojeni_db
        output = " ".join(str(a) for a in args)
        if "Připojení k databázi" not in output:
             printed.append(output)

    monkeypatch.setattr("builtins.print", mock_print_func)
    return printed


def test_pridat_ukol_pozitivni(clean_db, test_db, mock_input):
    print("Spouštím test_pridat_ukol_pozitivni...")

    # Kontrola obsahu tabulky před testem

    # *** 1. EXPLICITNÍ VYČIŠTĚNÍ ***
    cursor_clean = test_db.cursor()
    cursor_clean.execute("DELETE FROM ukoly")
    test_db.commit()
    cursor_clean.close()

    cursor_pre = test_db.cursor(dictionary=True)
    try:
        cursor_pre.execute("SELECT * FROM ukoly")
        rows = cursor_pre.fetchall()
        print(f"Obsah tabulky před testem: {rows}")
        assert len(rows) == 0, f"Tabulka 'ukoly' není prázdná před testem, obsahuje {len(rows)} záznamů."
        cursor_pre.close() # UZAVŘÍT PŮVODNÍ KURZOR

        # Simulace vstupů pro pridat_ukol
        mock_input.extend(["Testovací úkol", "Popis úkolu", "n"])
        print("Volám pridat_ukol...")
        pridat_ukol(connection=test_db) # Volání funkce, která již v sobě uzavírá připojení
        print("Úkol přidán, kontroluji databázi...")

        # OTEVŘÍT ZNOVU KURZOR PRO KONTROLU DATABÁZE
        cursor_po = test_db.cursor(dictionary=True)
        
        # Kontrola obsahu tabulky po vložení
        cursor_po.execute("SELECT COUNT(*) AS pocet FROM ukoly")
        result = cursor_po.fetchone()
        assert result is not None, "Dotaz nevrátil žádné výsledky. Zkontrolujte, zda byla data správně vložena."
        print(f"Dotaz vrátil: {result}, typ: {type(result)}")

        # Ověření, že byl přidán jeden úkol
        assert result["pocet"] == 1, f"Očekávaný počet úkolů je 1, ale bylo nalezeno {result['pocet']}."

        # Kontrola detailů vloženého úkolu
        cursor_po.execute("SELECT * FROM ukoly")
        rows = cursor_po.fetchall()
        print(f"Obsah tabulky po vložení: {rows}")
        assert len(rows) == 1, f"Tabulka 'ukoly' by měla obsahovat 1 záznam, ale obsahuje {len(rows)}."
        assert rows[0]["nazev"] == "Testovací úkol", f"Název úkolu neodpovídá. Očekáváno: 'Testovací úkol', nalezeno: {rows[0]['nazev']}."
        assert rows[0]["popis"] == "Popis úkolu", f"Popis úkolu neodpovídá. Očekáváno: 'Popis úkolu', nalezeno: {rows[0]['popis']}."
        assert rows[0]["stav"] == "Nezahájeno", f"Stav úkolu neodpovídá. Očekáváno: 'Nezahájeno', nalezeno: {rows[0]['stav']}."
    finally:
        # Uzavření kurzoru
        cursor_po.close()
        

def test_pridat_ukol_negativni(clean_db, mock_input, test_db, mock_print):
    # Kontrola obsahu tabulky před testem
    cursor = test_db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM ukoly")
        rows = cursor.fetchall()
        print(f"Obsah tabulky před testem: {rows}")

        print("Spouštím test_pridat_ukol_negativni...")
        # Simulace neplatného vstupu (prázdný název)
        # Názvy: 0, Popis: Popis úkolu, Stav: n
        mock_input.extend(["0"]) 
        pridat_ukol(connection=test_db)
        # Assert, že úkol nebyl vytvořen
        cursor.execute("SELECT COUNT(*) AS pocet FROM ukoly")
        result = cursor.fetchone()
        assert result["pocet"] == 0, f"Úkol byl vytvořen, očekáváno 0, nalezeno {result['pocet']}."
    finally:
        cursor.close()


def test_aktualizovat_ukol_pozitivni(clean_db, test_db, mock_input):
    # Přidání testovacího úkolu přímo do DB
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO ukoly (id, nazev, popis, stav) VALUES (1, 'Test', 'Popis', 'Nezahájeno')")
    test_db.commit()
    cursor.close()

    print("Spouštím test_aktualizovat_ukol_pozitivni...")
    # Simulace vstupů pro aktualizaci (zobrazit_ukoly se zavolá uvnitř aktualizovat_ukol)
    mock_input.extend(["1", "h"]) # ID 1, nový stav Hotovo (h)
    
    aktualizovat_ukol(connection=test_db)
    
    # Kontrola v DB po aktualizaci
    cursor = test_db.cursor(dictionary=True)
    cursor.execute("SELECT id, nazev, stav FROM ukoly WHERE id = 1")
    result = cursor.fetchone()
    
    print(f"Stav po aktualizaci: {result['stav']}")
    assert result["stav"] == "Hotovo"
    cursor.close()


def test_aktualizovat_ukol_negativni(clean_db, test_db, mock_input, mock_print):

    # Přidání testovacího úkolu
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO ukoly (id, nazev, popis, stav) VALUES (1, 'Test', 'Popis', 'Nezahájeno')")
    test_db.commit()
    cursor.close()

    print("Spouštím test_aktualizovat_ukol_negativni...")
    mock_input.extend(["1", "x"])  # Existující ID 1 a neplatný stav 'x'
    aktualizovat_ukol(connection=test_db)
    
    # Ověření, že stav nebyl změněn
    cursor = test_db.cursor(dictionary=True)
    cursor.execute("SELECT stav FROM ukoly WHERE id = 1")
    result = cursor.fetchone()
    assert result["stav"] == "Nezahájeno"  # Stav by mel zustat nezměněn

    # Ověření, že byla vypsána chybová zpráva
    # assert "Zadali jste neplatný stav pro aktualizaci" v mock_print je spravný
    assert any("Zadali jste neplatný stav pro aktualizaci" in p for p in mock_print)
    cursor.close()


def test_odstranit_ukol_pozitivni(clean_db, test_db, mock_input):

    # pridání úkolu do databáze
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO ukoly (id, nazev, popis, stav) VALUES (1, 'Test', 'Popis', 'Nezahájeno')")
    test_db.commit()
    cursor.close()

    print("Spouštím test_odstranit_ukol_pozitivni...")
    # Simulace vstupu pro odstranění
    mock_input.extend(["1"])
    odstranit_ukol(connection=test_db)
    
    # Kontorla
    cursor = test_db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS pocet FROM ukoly")
    result = cursor.fetchone()
    assert result["pocet"] == 0
    cursor.close()


def test_odstranit_ukol_negativni(clean_db, test_db, mock_input, mock_print):

    # přidání testovacího úkolu
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO ukoly (id, nazev, popis, stav) VALUES (1, 'Test', 'Popis', 'Nezahájeno')")
    test_db.commit()
    cursor.close()

    print("Spouštím test_odstranit_ukol_negativni...")
    # Simulace neexistujicího ID
    mock_input.extend(["999"]) 
    odstranit_ukol(connection=test_db)

    # overeni, že úkol NEBYL odstraněn
    cursor = test_db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS pocet FROM ukoly")
    result = cursor.fetchone()
    assert result["pocet"] == 1  # Úkol by měl stále existovat
    
    # overeni, že bla vypsana chybová zpráva
    assert any("Úkol s ID '999' nenalezen" in p for p in mock_print) 
    cursor.close()