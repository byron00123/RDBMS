# Mini-RDBMS with Web Dashboard

A simple **Relational Database Management System (RDBMS)** implemented in Python, complete with an **interactive REPL** and a **web dashboard** for CRUD operations. Built to demonstrate database design principles, including tables, primary/unique keys, and joins.

---

## Features

### Database (RDBMS)
- Create tables with a few data types (`INT`, `TEXT`).
- Primary key and unique key enforcement.
- CRUD operations:
  - `INSERT`, `SELECT`, `UPDATE`, `DELETE`
- Basic indexing using primary and unique keys.
- Support for `INNER JOIN` (and can extend to `LEFT JOIN`).
- Interactive REPL mode with SQL-like commands.

### Web Dashboard (Flask)
- View **Users** and **Orders** in tables.
- Add, edit, delete users.
- Add and delete orders.
- Display joined table (`Users + Orders`) using INNER JOIN.
- Interactive features:
  - Sort columns by clicking headers.
  - Search/filter table entries.
- Modern CSS dashboard with cards and responsive layout.

---

## Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd rdbms_demo


Create a virtual environment (optional but recommended):
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows


Install dependencies:
pip install flask


Run the web app:
python app.py


Open your browser at http://127.0.0.1:5000 to interact with the dashboard.