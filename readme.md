# Projekt: Správce úkolů s MySQL

Tento projekt je **jednoduchý správce úkolů** (_Task Manager_), který využívá databázi **MySQL** pro ukládání dat. Níže naleznete podrobné kroky, jak zprovoznit MySQL, nastavit virtuální prostředí a nainstalovat závislosti.

---

## Požadavky

Před spuštěním projektu se ujistěte, že máte nainstalované následující:

* **Python 3.8** nebo novější
* **MySQL Server**
* Doporučeno: **Virtuální prostředí** (`venv`)

---

## Instalace a Nastavení MySQL

### 1. Instalace MySQL Serveru

Vyberte příslušný příkaz pro váš operační systém:

* **MacOS (pomocí Homebrew)**:
    ```bash
    brew install mysql
    ```
* **Linux (např. Ubuntu)**:
    ```bash
    sudo apt update
    sudo apt install mysql-server
    ```
* **Windows**:
    Stáhněte a nainstalujte **MySQL Community Server** z [oficiálních stránek](https://dev.mysql.com/downloads/installer/).

### 2. Spuštění MySQL Serveru

* **MacOS**:
    ```bash
    brew services start mysql
    ```
* **Linux**:
    ```bash
    sudo systemctl start mysql
    ```
* **Windows**:
    Spusťte službu MySQL z **`Services`** (Služby) nebo pomocí **MySQL Workbench**.

### 3. Vytvoření Databáze a Uživatele

Přihlaste se do MySQL serveru (nahraďte `asdf` za vaše skutečné heslo, které nastavíte):

```bash
mysql -u root -p

Po přihlášení spusťte následující SQL příkazy pro vytvoření produkční a testovací databáze a nového uživatele s oprávněními:

CREATE DATABASE task_manager;
CREATE DATABASE task_manager_test;
CREATE USER 'db_manager'@'localhost' IDENTIFIED BY 'asdf';
GRANT ALL PRIVILEGES ON task_manager.* TO 'db_manager'@'localhost';
GRANT ALL PRIVILEGES ON task_manager_test.* TO 'db_manager'@'localhost';
FLUSH PRIVILEGES;

Virtuální Prostředí a Závislosti
Pro izolaci projektu doporučujeme použít virtuální prostředí.

**MacOS/Linux**

# Vytvoření virtuálního prostředí
python3 -m venv venv

# Aktivace virtuálního prostředí
source venv/bin/activate

# Instalace závislostí z requirements.txt
pip install -r requirements.txt

# Kontrola nainstalovaných balíčků
pip list

echo "Virtuální prostředí bylo vytvořeno a závislosti byly nainstalovány."

**Windows**

# Vytvoření virtuálního prostředí
python -m venv venv

# Aktivace virtuálního prostředí
.\venv\Scripts\activate

# Instalace závislostí z requirements.txt
pip install -r requirements.txt

# Kontrola nainstalovaných balíčků
pip list

echo "Virtuální prostředí bylo vytvořeno a závislosti byly nainstalovány."

## Spuštění Testů
Po nastavení MySQL a instalaci závislostí můžete spustit testy pomocí pytest.

pytest -v
