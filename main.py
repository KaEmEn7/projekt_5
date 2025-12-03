import mysql.connector
from mysql.connector import Error

"""
main.py: Pátý projekt do Engeto Online Python Akademie - vylepšený správce úkolů s MySQL db

author: Kamil Mach
email: kamil.machuj@gmail.com

"""

# Globální seznam pro ukoly
ukoly = []

connection = None # Globální proměnná pro případné sdílení připojení (pouze pro zavření)

def pripojeni_db(test: bool = False):
    """Vrací připojení k DB. Pokud již existuje globální připojení, vrátí je.
    Pokud neexistuje, vytvoří nové (a uloží do globální proměnné `connection`).
    """
    global connection
    try:
        if connection and getattr(connection, "is_connected", lambda: False)() :
            return connection

        db_name = "task_manager_test" if test else "task_manager"
        print(f"\n--- Připojení k databázi '{db_name}' ---")
        connection = mysql.connector.connect(
            host="localhost",
            user="db_manager",
            password="asdf",
            database=db_name,
        )
        print(f"Připojení k databázi '{db_name}' bylo úspěšné.")
        return connection
    except Error as e:
        print(f"Chyba při připojení k databázi: {e}")
        return None


def vytvoreni_tabulky(connection=None, test: bool = False):
    """Vytvoří tabulku ukoly. Pokud není předané connection, vytvoří vlastní a případně jej uzavře."""
    close_conn = False
    if connection is None:
        connection = pripojeni_db(test=test)
        close_conn = True

    if not connection:
        print("Chyba: Připojení k databázi nebylo navázáno.")
        return

    cursor = None
    try:
        cursor = connection.cursor()
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
        print("Tabulka 'ukoly' byla vytvořena nebo již existuje.")
    except Error as e:
        print(f"Chyba při vytváření tabulky: {e}")
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if close_conn and connection:
            try:
                connection.close()
            except Exception:
                pass


def drop_tabulka(connection=None, test: bool = False):
    close_conn = False
    if connection is None:
        connection = pripojeni_db(test=test)
        close_conn = True

    if not connection:
        print("Chyba: Připojení k databázi nebylo navázáno.")
        return

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS ukoly")
        connection.commit()
        print("Tabulka 'ukoly' byla úspěšně odstraněna.")
    except Error as e:
        print(f"Chyba při odstraňování tabulky: {e}")
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if close_conn and connection:
            try:
                connection.close()
            except Exception:
                pass


def pridat_ukol(connection=None, test: bool = False):
    """Pridá nový úkol. Pokud je predané connection, použije ho (neuzavírá jej)."""
    print("\n--- Přidání nového úkolu ---")

    close_conn = False
    if connection is None:
        connection = pripojeni_db(test=test)
        close_conn = True

    if not connection:
        print("Chyba: Připojení k databazi nebylo navazano.")
        return

    # --- VSTUPY ---
    nazev = input(
        "Zadejte název nového úkolu: \t\t Pro návrat do hlavního menu kdykoliv vyberte 0\n"
    ).strip()
    if not nazev or nazev == "0":
        print("Název nesmí být prázdný - úkol nebude vytvořen.")
        return

    popis = input(
        "Zadejte popis úkolu:\t\tPro návrat do hlavního menu kdykoliv vyberte 0\n"
    ).strip()
    if not popis or popis == "0":
        print("Úkol nebude vytvořen.")
        return

    stav_raw = input(
        "Zadejte stav úkolu\t\tPro návrat do hlavního menu kdykoliv vyberte 0\n"
        "n - nezahájeno\n"
        "h - hotovo\n"
        "p - probíhá): "
    ).strip().lower()

    if stav_raw == "n" or stav_raw == "":
        stav = "Nezahájeno"
    elif stav_raw == "h":
        stav = "Hotovo"
    elif stav_raw == "p":
        stav = "Probíhá"
    else:
        print("Neplatný stav. Použito 'Nezahájeno'.")
        stav = "Nezahájeno"

    # --- AŽ TED vytvoříme kurzor ---
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO ukoly (nazev, popis, stav) VALUES (%s, %s, %s)",
            (nazev, popis, stav)
        )
        connection.commit()
        print(f"Úkol '{nazev}' byl úspěšně vytvořen.")

    except Error as e:
        print(f"Chyba při přidávání úkolu: {e}")

    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass

        if close_conn and connection:
            try:
                connection.close()
            except:
                pass




def zobrazit_ukoly(connection=None, test: bool = False):
    close_conn = False
    if connection is None:
        connection = pripojeni_db(test=test)
        close_conn = True

    if not connection:
        print("Chyba: Připojení k databázi nebylo navázáno.")
        return

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nazev, popis, stav FROM ukoly 
            WHERE stav IN ('Nezahájeno', 'Probíhá')
        """)
        ukoly = cursor.fetchall()

        if not ukoly:
            print("\nSeznam úkolů je prázdný.")
        else:
            print("\n--- Seznam úkolů ---")
            for ukol in ukoly:
                print(f"{ukol['id']}. {ukol['nazev']} - {ukol['popis']} ({ukol['stav']})")

    except Error as e:
        print(f"Chyba při zobrazování úkolů: {e}")
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if close_conn and connection:
            try:
                connection.close()
            except Exception:
                pass


def aktualizovat_ukol(connection=None, test: bool = False):
    """Aktualizuje stav ukolu v databázi podle ID.
       Pokud je předané connection, pouzije ho (neuzavíra ho)."""

    print("\n--- Aktualizace úkolu ---")

    close_conn = False
    if connection is None:
        connection = pripojeni_db(test=test)
        close_conn = True

    if not connection:
        print("Chyba: Připojení k databázi nebylo navazano.")
        return

    try:
        zobrazit_ukoly(connection=connection, test=test) # Zobrazit aktuální úkoly
        id_ukolu = input("Zadejte ID úkolu, který chcete aktualizovat:\n").strip() # Načtení ID úkolu

        if not id_ukolu.isdigit():
            print("Neplatné ID. Musí být číslo.")
            return
        id_ukolu = int(id_ukolu)

        novy_stav_input = input( # Nový stav
            "Zadejte nový stav:\n"
            "p - Probíhá\n"
            "h - Hotovo\n"
            "n - Nezahájeno\n"
        ).strip().lower()

        stav_map = {
            "p": "Probíhá",
            "h": "Hotovo",
            "n": "Nezahájeno"
        }

        if novy_stav_input not in stav_map:
            print("Zadali jste neplatný stav pro aktualizaci:", novy_stav_input)
            return

        novy_stav = stav_map[novy_stav_input]

        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT COUNT(*) AS pocet FROM ukoly WHERE id = %s", (id_ukolu,)) # Zkontrolovat, zda úkol s ID existuje

            if cursor.fetchone()["pocet"] == 0:
                print(f"Úkol s ID '{id_ukolu}' nenalezen.")
                return

            cursor.execute( # aktualizace stavu
                "UPDATE ukoly SET stav = %s WHERE id = %s",
                (novy_stav, id_ukolu)
            )
            connection.commit()
            print(f"Úkol s ID {id_ukolu} byl úspěšně aktualizován.")

    except Error as e:
        print(f"Chyba při aktualizaci úkolu: {e}")

    finally:
        if close_conn and connection:
            try:
                connection.close()
            except Exception:
                pass


# Umožňuje uživateli odstranit úkol ze seznamu úkolů podle jeho ID.
def odstranit_ukol(connection=None, test: bool = False):
    """Odstraní úkol z databáze podle ID."""

    close_conn = False
    if connection is None:
        connection = pripojeni_db(test=test)
        close_conn = True

    if not connection:
        print("Chyba: Připojení k databázi nebylo navázáno.")
        return

    try:
        cursor = connection.cursor(dictionary=True) # Kontrola počtu úkolů

        try:
            cursor.execute("SELECT COUNT(*) AS pocet FROM ukoly")
            row = cursor.fetchone()
            pocet = int(row["pocet"]) if row else 0
        finally:
            try:
                cursor.close()
            except Exception:
                pass

        if pocet == 0:
            print("\nSeznam úkolů je prázdný, není co mazat. Zpět do hl. menu.\n")
            return

        zobrazit_ukoly(connection=connection)

        id_ukolu = input( # Načtení ID
            "Zadejte ID úkolu, který chcete odstranit:"
            "\nPro návrat do hlavního menu zadejte 0\n"
        ).strip()

        if not id_ukolu.isdigit():
            print("\nZadané ID musí být číslo.\n")
            return

        id_ukolu = int(id_ukolu)

        if id_ukolu == 0:
            return

        cursor = connection.cursor() # Odstranění úkolu
        try:
            cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
            connection.commit()
            if cursor.rowcount == 0:
                print(f"Úkol s ID '{id_ukolu}' nenalezen.")
            else:
                print("Úkol byl úspěšně odstraněn.")
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    except Error as e:
        print(f"Chyba při odstraňování úkolu: {e}")
    finally:
        if close_conn and connection:
            try:
                connection.close()
            except Exception:
                pass


def zavrit_pripojeni():
    global connection
    try:
        if connection and getattr(connection, "is_connected", lambda: False)():
            connection.close()
            print("Připojení k databázi bylo uzavřeno.")
    except Exception as e:
        print(f"Chyba při uzavírání připojení: {e}")


def hlavni_menu():
    # Vytvoříme sdílené připojení pro celou relaci
    conn = pripojeni_db()
    try:
        while True:
            print("\n--- Hlavní menu ---")
            print("1. Přidání nového úkolu")
            print("2. Zobrazit všechny úkoly")
            print("3. Aktualizovat úkol")
            print("4. Odstranění úkolu")
            print("5. Konec programu")

            volba = input("Vyberte možnost 1-5: ")
            if volba == "1":
                pridat_ukol(connection=conn)
            elif volba == "2":
                zobrazit_ukoly(connection=conn)
            elif volba == "3":
                aktualizovat_ukol(connection=conn)
            elif volba == "4":
                odstranit_ukol(connection=conn)
            elif volba == "5":
                print("Program ukončen.\n")
                break
            else:
                print("\n", volba, "Je neplatná volba, zkuste to znovu.\n")
    finally:
        zavrit_pripojeni() # Zaver sdílené připojení



if __name__ == "__main__":
    try:
        vytvoreni_tabulky()
        hlavni_menu()
    finally:
        zavrit_pripojeni()
