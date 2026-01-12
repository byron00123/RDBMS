from flask import Flask, render_template_string, request, redirect
from repl import db  # use the same Database instance from repl.py

app = Flask(__name__)

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Mini-RDBMS Dashboard</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: #f4f6f8;
      margin: 0;
      padding: 0;
    }
    header {
      background: #1976d2;
      color: white;
      padding: 20px;
      text-align: center;
      box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    h1, h2 { margin: 0 0 10px 0; }
    .container {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      padding: 20px;
      justify-content: center;
    }
    .card {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      flex: 1 1 300px;
      max-width: 450px;
    }
    .card h2 {
      font-size: 1.2em;
      margin-bottom: 15px;
      color: #1976d2;
    }
    .card table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 10px;
    }
    .card th, .card td {
      padding: 8px;
      border-bottom: 1px solid #ddd;
      text-align: left;
    }
    .card th {
      background: #e3f2fd;
      cursor: pointer;
    }
    .highlight { background: #fff9c4; }
    .card form { display: flex; flex-direction: column; gap: 10px; }
    input {
      padding: 8px;
      border: 1px solid #ccc;
      border-radius: 4px;
    }
    button {
      padding: 10px;
      border: none;
      border-radius: 4px;
      background: #1976d2;
      color: white;
      cursor: pointer;
      font-weight: bold;
    }
    button:hover { background: #1565c0; }
    a { color: #1976d2; text-decoration: none; font-weight: bold; }
    a:hover { text-decoration: underline; }
    .join-section {
      width: 100%;
      margin-top: 40px;
      padding: 20px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    @media (max-width: 900px) {
      .container { flex-direction: column; align-items: center; }
    }
  </style>
  <script>
    function searchTable(inputId, tableId) {
      const input = document.getElementById(inputId);
      const filter = input.value.toLowerCase();
      const table = document.getElementById(tableId);
      const tr = table.getElementsByTagName("tr");
      for (let i = 1; i < tr.length; i++) {
        let visible = false;
        const td = tr[i].getElementsByTagName("td");
        for (let j = 0; j < td.length; j++) {
          if (td[j].innerText.toLowerCase().indexOf(filter) > -1) visible = true;
        }
        tr[i].style.display = visible ? "" : "none";
      }
    }

    function sortTable(tableId, colIndex) {
      const table = document.getElementById(tableId);
      let rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
      switching = true; dir = "asc";
      while (switching) {
        switching = false;
        rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
          shouldSwitch = false;
          x = rows[i].getElementsByTagName("TD")[colIndex];
          y = rows[i + 1].getElementsByTagName("TD")[colIndex];
          if (dir == "asc") {
            if (x.innerText.toLowerCase() > y.innerText.toLowerCase()) { shouldSwitch = true; break; }
          } else if (dir == "desc") {
            if (x.innerText.toLowerCase() < y.innerText.toLowerCase()) { shouldSwitch = true; break; }
          }
        }
        if (shouldSwitch) {
          rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
          switching = true; switchcount++;
        } else {
          if (switchcount == 0 && dir == "asc") { dir = "desc"; switching = true; }
        }
      }
    }
  </script>
</head>
<body>
  <header><h1>Mini-RDBMS Dashboard</h1></header>

  <div class="container">
    <div class="card">
      <h2>Users</h2>
      <input type="text" id="userSearch" placeholder="Search Users..." onkeyup="searchTable('userSearch','usersTable')">
      <table id="usersTable">
        <tr>
          <th onclick="sortTable('usersTable',0)">ID</th>
          <th onclick="sortTable('usersTable',1)">Name</th>
          <th onclick="sortTable('usersTable',2)">Email</th>
          <th>Actions</th>
        </tr>
        {% for user in users %}
        <tr>
          <td>{{ user['id'] }}</td>
          <td>{{ user['name'] }}</td>
          <td>{{ user['email'] }}</td>
          <td>
            <a href="/edit_user/{{ user['id'] }}">Edit</a> |
            <a href="/delete_user/{{ user['id'] }}">Delete</a>
          </td>
        </tr>
        {% endfor %}
      </table>
      <h3>Add User</h3>
      <form method="POST" action="/add_user">
        <input name="name" placeholder="Name" required>
        <input name="email" placeholder="Email" required>
        <button type="submit">Add User</button>
      </form>
    </div>

    <div class="card">
      <h2>Orders</h2>
      <input type="text" id="orderSearch" placeholder="Search Orders..." onkeyup="searchTable('orderSearch','ordersTable')">
      <table id="ordersTable">
        <tr>
          <th onclick="sortTable('ordersTable',0)">ID</th>
          <th onclick="sortTable('ordersTable',1)">User ID</th>
          <th onclick="sortTable('ordersTable',2)">Item</th>
          <th>Actions</th>
        </tr>
        {% for order in orders %}
        <tr class="{{ 'highlight' if order['id'] > recent_threshold else '' }}">
          <td>{{ order['id'] }}</td>
          <td>{{ order['user_id'] }}</td>
          <td>{{ order['item'] }}</td>
          <td>
            <a href="/delete_order/{{ order['id'] }}">Delete</a>
          </td>
        </tr>
        {% endfor %}
      </table>
      <h3>Add Order</h3>
      <form method="POST" action="/add_order">
        <input name="user_id" placeholder="User ID" required>
        <input name="item" placeholder="Item" required>
        <button type="submit">Add Order</button>
      </form>
    </div>
  </div>

  <div class="join-section">
    <h2>Users + Orders (INNER JOIN)</h2>
    <table>
      <tr>
        <th>User ID</th>
        <th>Name</th>
        <th>Email</th>
        <th>Order ID</th>
        <th>Item</th>
      </tr>
      {% for row in join_rows %}
      <tr>
        <td>{{ row['users.id'] }}</td>
        <td>{{ row['users.name'] }}</td>
        <td>{{ row['users.email'] }}</td>
        <td>{{ row['orders.id'] }}</td>
        <td>{{ row['orders.item'] }}</td>
      </tr>
      {% endfor %}
    </table>
  </div>
</body>
</html>
"""

EDIT_USER_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Edit User</title>
  <style>
    body { font-family: Arial; margin: 20px; background: #f4f6f8; }
    form { background: white; padding: 20px; border-radius: 8px; max-width: 400px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    input { padding: 8px; margin: 10px 0; width: 100%; border-radius: 4px; border: 1px solid #ccc; }
    button { padding: 10px; width: 100%; border: none; border-radius: 4px; background: #1976d2; color: white; cursor: pointer; font-weight: bold; }
    button:hover { background: #1565c0; }
  </style>
</head>
<body>
<h1>Edit User</h1>
<form method="POST" action="/edit_user/{{ user['id'] }}">
  <input name="name" value="{{ user['name'] }}" required>
  <input name="email" value="{{ user['email'] }}" required>
  <button type="submit">Save Changes</button>
</form>
<a href="/">Back</a>
</body>
</html>
"""

# Ensure tables exist
if "users" not in db.tables:
    db.create_table("users", {"id": "INT", "name": "TEXT", "email": "TEXT"}, primary_key="id", unique_keys=["email"])
if "orders" not in db.tables:
    db.create_table("orders", {"id": "INT", "user_id": "INT", "item": "TEXT"}, primary_key="id")

def next_id(table_name):
    rows = db.select_all_from(table_name)
    return max([r["id"] for r in rows], default=0) + 1

@app.route("/")
def index():
    users = db.select_all_from("users")
    orders = db.select_all_from("orders")
    recent_threshold = max([o["id"] for o in orders], default=0) - 2
    join_rows = []
    for u in users:
        for o in orders:
            if u["id"] == o["user_id"]:
                combined = {f"users.{k}": v for k, v in u.items()}
                combined.update({f"orders.{k}": v for k, v in o.items()})
                join_rows.append(combined)
    return render_template_string(INDEX_HTML, users=users, orders=orders, join_rows=join_rows, recent_threshold=recent_threshold)

@app.route("/add_user", methods=["POST"])
def add_user():
    new_id = next_id("users")
    name = request.form["name"]
    email = request.form["email"]
    db.insert_into("users", [new_id, name, email])
    return redirect("/")

@app.route("/edit_user/<int:user_id>", methods=["GET","POST"])
def edit_user(user_id):
    users = db.select_all_from("users")
    user = next((u for u in users if u["id"] == user_id), None)
    if not user: return "User not found"
    if request.method == "POST":
        db.update("users", {"name": request.form["name"], "email": request.form["email"]}, where={"id": user_id})
        return redirect("/")
    return render_template_string(EDIT_USER_HTML, user=user)

@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    db.delete_from("users", where={"id": user_id})
    return redirect("/")

@app.route("/add_order", methods=["POST"])
def add_order():
    new_id = next_id("orders")
    db.insert_into("orders", [new_id, int(request.form["user_id"]), request.form["item"]])
    return redirect("/")

@app.route("/delete_order/<int:order_id>")
def delete_order(order_id):
    db.delete_from("orders", where={"id": order_id})
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
