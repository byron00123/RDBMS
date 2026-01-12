# repl.py
from rdbms import Database
import ast

db = Database()

def execute(command):
    cmd_lower = command.strip().lower()

    # CREATE TABLE
    if cmd_lower.startswith("create table"):
        try:
            parts = command.split("(")
            table_name = parts[0].split()[2].strip()
            cols_part = parts[1].split(")")[0]
            cols = {}
            primary_key = None
            unique_keys = []

            for col_def in cols_part.split(","):
                tokens = col_def.strip().split()
                col_name = tokens[0]
                col_type = tokens[1].upper()
                cols[col_name] = col_type
                if "PRIMARY" in col_def.upper():
                    primary_key = col_name
                if "UNIQUE" in col_def.upper():
                    unique_keys.append(col_name)

            if table_name in db.tables:
                print(f"Error: Table '{table_name}' already exists")
            else:
                db.create_table(table_name, cols, primary_key, unique_keys)
                print(f"Table '{table_name}' created successfully")

        except Exception as e:
            print("Error:", e)

    # INSERT INTO
    elif cmd_lower.startswith("insert into"):
        try:
            table_name = command.split()[2].strip()
            values_index = command.lower().find("values")
            if values_index == -1:
                raise ValueError("INSERT must have VALUES clause")

            values_part = command[values_index + len("values"):].strip()
            if values_part.endswith(";"):
                values_part = values_part[:-1]
            if values_part.startswith("(") and values_part.endswith(")"):
                values_part = values_part[1:-1].strip()

            values = ast.literal_eval(f"[{values_part}]")
            table_columns = list(db.tables[table_name].columns.keys())
            if len(values) != len(table_columns):
                raise ValueError(f"Column count mismatch. Expected {len(table_columns)}, got {len(values)}")

            db.insert_into(table_name, values)
            print("Row inserted successfully")

        except Exception as e:
            print("Error:", e)

    # SELECT * FROM
    elif cmd_lower.startswith("select * from"):
        try:
            parts = command.lower().split("where")
            table_name = parts[0].split()[3].strip(";")
            rows = db.select_all_from(table_name)

            if len(parts) > 1:
                condition = parts[1].strip().strip(";")
                if "=" not in condition:
                    raise ValueError("Only equality conditions supported")
                col, val = condition.split("=")
                col = col.strip()
                val = val.strip().strip("'").strip('"')
                rows = [row for row in rows if str(row.get(col)) == val]

            for row in rows:
                print(row)

        except Exception as e:
            print("Error:", e)

    # UPDATE
    elif cmd_lower.startswith("update"):
        try:
            # Parse table name
            set_index = cmd_lower.find("set")
            table_name = command[6:set_index].strip()

            # Parse SET and optional WHERE
            where_index = cmd_lower.find("where", set_index)
            if where_index == -1:
                set_part = command[set_index + 3:].strip().strip(";")
                where_part = None
            else:
                set_part = command[set_index + 3:where_index].strip()
                where_part = command[where_index + 5:].strip().strip(";")

            # Parse updates
            updates = {}
            for assignment in set_part.split(","):
                k, v = assignment.split("=")
                updates[k.strip()] = v.strip().strip("'").strip('"')

            rows = db.select_all_from(table_name)
            if where_part:
                if "=" not in where_part:
                    raise ValueError("Only equality WHERE supported")
                w_col, w_val = where_part.split("=")
                w_col = w_col.strip()
                w_val = w_val.strip().strip("'").strip('"')
                rows = [row for row in rows if str(row.get(w_col)) == w_val]

            for row in rows:
                for k, v in updates.items():
                    row[k] = v

            print(f"{len(rows)} row(s) updated")

        except Exception as e:
            print("Error:", e)

    # DELETE
    elif cmd_lower.startswith("delete from"):
        try:
            table_name = command.split()[2].strip()
            where_index = cmd_lower.find("where")
            rows = db.select_all_from(table_name)

            if where_index == -1:
                to_delete = rows[:]
            else:
                where_part = command[where_index + 5:].strip().strip(";")
                if "=" not in where_part:
                    raise ValueError("Only equality WHERE supported")
                col, val = where_part.split("=")
                col = col.strip()
                val = val.strip().strip("'").strip('"')
                to_delete = [row for row in rows if str(row.get(col)) == val]

            for row in to_delete:
                rows.remove(row)

            print(f"{len(to_delete)} row(s) deleted")

        except Exception as e:
            print("Error:", e)

    # EXIT
    elif cmd_lower in ["exit", "quit"]:
        print("Exiting REPL...")
        exit(0)

    else:
        print("Command not recognized.")


def start_repl():
    print("Welcome to Mini-RDBMS REPL. Type 'exit' to quit.")
    buffer = ""
    while True:
        line = input("db> ")
        if line.lower() in ["exit", "quit"]:
            print("Exiting REPL...")
            break

        buffer += " " + line.strip()
        if ";" in buffer:
            commands = buffer.split(";")
            for cmd in commands[:-1]:
                if cmd.strip():
                    execute(cmd.strip())
            buffer = commands[-1]


if __name__ == "__main__":
    start_repl()
