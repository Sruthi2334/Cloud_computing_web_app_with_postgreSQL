from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=os.environ.get("DB_PORT", "5432"),
        sslmode="require"
    )

# HOME PAGE
@app.route("/")
def home():
    return render_template("home.html")

# CREATE PAGE (Form)
@app.route("/create")
def create():
    return render_template("create.html")

# INSERT DATA
@app.route("/book", methods=["POST"])
def book():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO bookings (guest_name, email, room_type, check_in, check_out)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            request.form["guest_name"],
            request.form["email"],
            request.form["room_type"],
            request.form["check_in"],
            request.form["check_out"]
        )
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/bookings")

# READ PAGE
@app.route("/bookings")
def bookings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bookings ORDER BY id DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("bookings.html", bookings=data)

# EDIT PAGE
@app.route("/edit/<int:id>")
def edit(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bookings WHERE id=%s", (id,))
    booking = cur.fetchone()
    cur.close()
    conn.close()

    return render_template("edit.html", booking=booking)

# UPDATE DATA (3 columns)
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE bookings
        SET guest_name=%s,
            email=%s,
            room_type=%s
        WHERE id=%s
    """, (
        request.form["guest_name"],
        request.form["email"],
        request.form["room_type"],
        id
    ))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/bookings")

# DELETE CONFIRM PAGE
@app.route("/delete/<int:id>")
def delete_page(id):
    return render_template("delete.html", id=id)

# DELETE ACTION
@app.route("/delete_confirm/<int:id>")
def delete_confirm(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM bookings WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect("/bookings")

if __name__ == "__main__":
    app.run(debug=True)