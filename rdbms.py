# rdbms.py
class Table:
    def __init__(self, name, columns, primary_key=None, unique_keys=None):
        self.name = name
        self.columns = columns
        self.primary_key = primary_key
        self.unique_keys = unique_keys or []
        self.rows = []
        self.indexes = {}

        if primary_key:
            self.indexes[primary_key] = {}
        for key in self.unique_keys:
            if key != primary_key:
                self.indexes[key] = {}

    def insert(self, values):
        if len(values) != len(self.columns):
            raise ValueError("Column count does not match")

        row = dict(zip(self.columns.keys(), values))

        if self.primary_key:
            pk_val = row[self.primary_key]
            if pk_val in self.indexes[self.primary_key]:
                raise ValueError("Primary key violation")
            self.indexes[self.primary_key][pk_val] = row

        for key in self.unique_keys:
            val = row[key]
            if key in self.indexes and val in self.indexes[key]:
                raise ValueError(f"Unique key violation: {key}")
            self.indexes[key][val] = row

        self.rows.append(row)

    def select_all(self):
        return self.rows


class Database:
    def __init__(self):
        self.tables = {}

    def create_table(self, name, columns, primary_key=None, unique_keys=None):
        if name in self.tables:
            raise ValueError(f"Table {name} already exists")
        self.tables[name] = Table(name, columns, primary_key, unique_keys)

    def insert_into(self, table_name, values):
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        self.tables[table_name].insert(values)

    def select_all_from(self, table_name):
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        return self.tables[table_name].select_all()
