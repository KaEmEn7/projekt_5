Spuštění testů:

`pytest -v`

# Projekt: Správce úkolů s MySQL

Tento projekt je jednoduchý správce úkolů, který využívá databázi MySQL pro ukládání dat. Níže naleznete kroky, jak zprovoznit MySQL, nainstalovat závislosti a spustit projekt.

---

## Požadavky

Před spuštěním projektu se ujistěte, že máte nainstalované následující:
- Python 3.8 nebo novější
- MySQL Server
- Virtuální prostředí (doporučeno)

---

## Instalace MySQL

1. **Nainstalujte MySQL Server**:
   - Na **MacOS**:
     ```bash
     brew install mysql
     ```
   - Na **Linuxu** (např. Ubuntu):
     ```bash
     sudo apt update
     sudo apt install mysql-server
     ```
   - Na **Windows**:
     Stáhněte a nainstalujte MySQL Community Server z [oficiálních stránek](https://dev.mysql.com/downloads/installer/).

2. **Spusťte MySQL Server**:
   - Na **MacOS**:
     ```bash
     brew services start mysql
     ```
   - Na **Linuxu**:
     ```bash
     sudo systemctl start mysql
     ```
   - Na **Windows**:
     Spusťte službu MySQL z `Services` nebo pomocí MySQL Workbench.

3. **Přihlaste se do MySQL**:
   ```bash
   mysql -u root -p

MYSQL:

CREATE DATABASE task_manager;
CREATE DATABASE task_manager_test;
CREATE USER 'db_manager'@'localhost' IDENTIFIED BY 'asdf';
GRANT ALL PRIVILEGES ON task_manager.* TO 'db_manager'@'localhost';
GRANT ALL PRIVILEGES ON task_manager_test.* TO 'db_manager'@'localhost';
FLUSH PRIVILEGES;

venv:

macos/linux

# Vytvoření virtuálního prostředí
python3 -m venv venv

# Aktivace virtuálního prostředí
source venv/bin/activate

# Instalace závislostí z requirements.txt
pip install -r requirements.txt

# Kontrola nainstalovaných balíčků
pip list

echo "Virtuální prostředí bylo vytvořeno a závislosti byly nainstalovány."

windows

# Vytvoření virtuálního prostředí
python -m venv venv

# Aktivace virtuálního prostředí
.\venv\Scripts\activate

# Instalace závislostí z requirements.txt
pip install -r requirements.txt

# Kontrola nainstalovaných balíčků
pip list

echo "Virtuální prostředí bylo vytvořeno a závislosti byly nainstalovány."
