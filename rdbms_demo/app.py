from flask import Flask, render_template_string, request, redirect
from repl import db  # use the same Database instance from repl.py

app = Flask(__name__)

# Styled HTML templates
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Mini-RDBMS Web App</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 20px;
      background: #f9f9f9;
    }
    h1, h2, h3 {
      color: #333;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
      background: #fff;
      box-shadow: 0 0 5px rgba(0,0,0,0.1);
    }
    th, td {
      padding: 8px 12px;
      border: 1px solid #ddd;
      text-align: left;
    }
    th {
      background-color: #4CAF50;
      color: white;
    }
    tr:nth-child(even) {
      background-color: #f2f2f2;
    }
    form {
      margin-bottom: 30px;
      padding: 10px;
      background: #fff;
      box-shadow: 0 0 5px rgba(0,0,0,0.1);
      width: fit-content;
    }
    input {
      padding: 5px;
      margin: 5px;
    }
    button {
      padding: 5px 10px;
      background-color: #4CAF50;
      color: white;
      border: none;
      cursor: pointer;
    }
    button:hover {
      background-color: #45a049;
    }
    a {
      text-decoration: none;
      color: #2196F3;
    }
    a:hover {
      text-decoration: underline;
    }
    .container {
      display: flex;
      flex-wrap: wrap;
      gap: 40px;
    }
    .section {
      flex: 1 1 400px;
    }
  </style>
</head>
<body>
<h1>Mini-RDBMS Web App</h1>

<div class="container">
  <div class="section">
    <h2>Users</h2>
    <table>
      <tr><th>ID</th><th>Name</th><th>Email</th><th>Actions</th></tr>
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
      Name: <input name="name" required>
      Email: <input name="email" required>
      <button type="submit">Add</button>
    </form>
  </div>

  <div class="section">
    <h2>Orders</h2>
    <table>
      <tr><th>ID</th><th>User ID</th><th>Item</th><th>Actions</th></tr>
      {% for order in orders %}
      <tr>
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
      User ID: <input name="user_id" required>
      Item: <input name="item" required>
      <button type="submit">Add</button>
    </form>
  </div>
</div>

<h2>Users + Orders (INNER JOIN)</h2>
<table>
<tr><th>User ID</th><th>Name</th><th>Email</th><th>Order ID</th><th>Item</th></tr>
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
</body>
</html>
"""

EDIT_USER_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Edit User</title>
  <style>
    body { font-family: Arial; margin: 20px; }
    form { background: #f9f9f9; padding: 10px; width: fit-content; }
    input { padding: 5px; margin: 5px; }
    button { padding: 5px 10px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
    button:hover { background-color: #45a049; }
  </style>
</head>
<body>
<h1>Edit User</h1>
<form method="POST" action="/edit_user/{{ user['id'] }}">
  Name: <input name="name" value="{{ user['name'] }}" required>
  Email: <input name="email" value="{{ user['email'] }}" required>
  <button type="submit">Save</button>
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

# Auto-increment helpers
def next_id(table_name):
    rows = db.select_all_from(table_name)
    return max([r["id"] for r in rows], default=0) + 1

# Routes
@app.route("/")
def index():
    users = db.select_all_from("users")
    orders = db.select_all_from("orders")

    # INNER JOIN users.id = orders.user_id
    join_rows = []
    for u in users:
        for o in orders:
            if u["id"] == o["user_id"]:
                combined = {f"users.{k}": v for k, v in u.items()}
                combined.update({f"orders.{k}": v for k, v in o.items()})
                join_rows.append(combined)

    return render_template_string(INDEX_HTML, users=users, orders=orders, join_rows=join_rows)

@app.route("/add_user", methods=["POST"])
def add_user():
    new_id = next_id("users")
    name = request.form["name"]
    email = request.form["email"]
    try:
        db.insert_into("users", [new_id, name, email])
    except Exception as e:
        return f"Error adding user: {e}"
    return redirect("/")

@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    users = db.select_all_from("users")
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return "User not found"
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        try:
            db.update("users", {"name": name, "email": email}, where={"id": user_id})
        except Exception as e:
            return f"Error updating user: {e}"
        return redirect("/")
    return render_template_string(EDIT_USER_HTML, user=user)

@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    db.delete_from("users", where={"id": user_id})
    return redirect("/")

@app.route("/add_order", methods=["POST"])
def add_order():
    new_id = next_id("orders")
    user_id = int(request.form["user_id"])
    item = request.form["item"]
    try:
        db.insert_into("orders", [new_id, user_id, item])
    except Exception as e:
        return f"Error adding order: {e}"
    return redirect("/")

@app.route("/delete_order/<int:order_id>")
def delete_order(order_id):
    db.delete_from("orders", where={"id": order_id})
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
