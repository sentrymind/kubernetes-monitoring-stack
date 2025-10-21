"""
Модуль для работы с SQLite базой данных
"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os


class SupplementsDB:
    """Класс для работы с базой данных приема БАДов"""

    def __init__(self, db_path: str = "data/supplements.db"):
        """
        Инициализация подключения к базе данных

        Args:
            db_path: Путь к файлу базы данных
        """
        # Создаем директорию если её нет
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        """Создание таблиц в базе данных"""
        cursor = self.conn.cursor()

        # Таблица ежедневных записей о приеме БАДов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_intake (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                omega3_dose REAL,
                omega3_taken INTEGER DEFAULT 0,
                d3_dose REAL,
                d3_taken INTEGER DEFAULT 0,
                k2_dose REAL,
                k2_taken INTEGER DEFAULT 0,
                energy_level INTEGER,
                sleep_quality INTEGER,
                mood_level INTEGER,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица результатов анализов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lab_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                vitamin_d_level REAL,
                omega3_index REAL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица стоимости БАДов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supplement_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplement_name TEXT NOT NULL,
                purchase_date TEXT NOT NULL,
                cost REAL NOT NULL,
                quantity INTEGER NOT NULL,
                dose_per_unit REAL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def add_daily_intake(self, data: Dict[str, Any]) -> bool:
        """
        Добавление записи о ежедневном приеме

        Args:
            data: Словарь с данными о приеме

        Returns:
            True если успешно, False при ошибке
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO daily_intake
                (date, omega3_dose, omega3_taken, d3_dose, d3_taken, k2_dose, k2_taken,
                 energy_level, sleep_quality, mood_level, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('date'),
                data.get('omega3_dose'),
                data.get('omega3_taken', 0),
                data.get('d3_dose'),
                data.get('d3_taken', 0),
                data.get('k2_dose'),
                data.get('k2_taken', 0),
                data.get('energy_level'),
                data.get('sleep_quality'),
                data.get('mood_level'),
                data.get('notes', '')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении записи: {e}")
            return False

    def add_lab_result(self, data: Dict[str, Any]) -> bool:
        """
        Добавление результатов анализов

        Args:
            data: Словарь с результатами анализов

        Returns:
            True если успешно, False при ошибке
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO lab_results
                (date, vitamin_d_level, omega3_index, notes)
                VALUES (?, ?, ?, ?)
            """, (
                data.get('date'),
                data.get('vitamin_d_level'),
                data.get('omega3_index'),
                data.get('notes', '')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении результатов анализов: {e}")
            return False

    def add_supplement_cost(self, data: Dict[str, Any]) -> bool:
        """
        Добавление информации о стоимости БАДов

        Args:
            data: Словарь с данными о покупке

        Returns:
            True если успешно, False при ошибке
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO supplement_costs
                (supplement_name, purchase_date, cost, quantity, dose_per_unit, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data.get('supplement_name'),
                data.get('purchase_date'),
                data.get('cost'),
                data.get('quantity'),
                data.get('dose_per_unit'),
                data.get('notes', '')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении стоимости: {e}")
            return False

    def get_daily_intake(self, start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Получение данных о ежедневном приеме

        Args:
            start_date: Начальная дата (YYYY-MM-DD)
            end_date: Конечная дата (YYYY-MM-DD)

        Returns:
            DataFrame с данными
        """
        query = "SELECT * FROM daily_intake"

        if start_date and end_date:
            query += f" WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        elif start_date:
            query += f" WHERE date >= '{start_date}'"
        elif end_date:
            query += f" WHERE date <= '{end_date}'"

        query += " ORDER BY date"

        return pd.read_sql_query(query, self.conn)

    def get_lab_results(self) -> pd.DataFrame:
        """Получение всех результатов анализов"""
        return pd.read_sql_query(
            "SELECT * FROM lab_results ORDER BY date",
            self.conn
        )

    def get_supplement_costs(self, start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Получение данных о стоимости БАДов

        Args:
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            DataFrame с данными о стоимости
        """
        query = "SELECT * FROM supplement_costs"

        if start_date and end_date:
            query += f" WHERE purchase_date BETWEEN '{start_date}' AND '{end_date}'"
        elif start_date:
            query += f" WHERE purchase_date >= '{start_date}'"
        elif end_date:
            query += f" WHERE purchase_date <= '{end_date}'"

        query += " ORDER BY purchase_date"

        return pd.read_sql_query(query, self.conn)

    def import_from_csv(self, csv_path: str, table_name: str) -> bool:
        """
        Импорт данных из CSV файла

        Args:
            csv_path: Путь к CSV файлу
            table_name: Название таблицы (daily_intake, lab_results, supplement_costs)

        Returns:
            True если успешно, False при ошибке
        """
        try:
            df = pd.read_csv(csv_path)
            df.to_sql(table_name, self.conn, if_exists='append', index=False)
            return True
        except Exception as e:
            print(f"Ошибка при импорте из CSV: {e}")
            return False

    def export_to_csv(self, table_name: str, output_path: str) -> bool:
        """
        Экспорт данных в CSV файл

        Args:
            table_name: Название таблицы
            output_path: Путь для сохранения CSV

        Returns:
            True если успешно, False при ошибке
        """
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)
            df.to_csv(output_path, index=False)
            return True
        except Exception as e:
            print(f"Ошибка при экспорте в CSV: {e}")
            return False

    def get_next_lab_test_date(self) -> Optional[str]:
        """
        Расчет даты следующего анализа (через 3 месяца после последнего)

        Returns:
            Дата в формате YYYY-MM-DD или None
        """
        df = self.get_lab_results()

        if df.empty:
            return None

        last_test_date = pd.to_datetime(df['date'].max())
        next_test_date = last_test_date + timedelta(days=90)

        return next_test_date.strftime('%Y-%m-%d')

    def close(self):
        """Закрытие соединения с базой данных"""
        self.conn.close()
