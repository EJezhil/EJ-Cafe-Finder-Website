import datetime
import os

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Update, func
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

app = Flask(__name__)
ckeditor = CKEditor()
ckeditor.init_app(app)

app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)

# CONFIGURE TABLE
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///cafes.db")
app.app_context().push()

db = SQLAlchemy()
db.init_app(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.String(250), nullable=False)
    has_wifi = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.String(250), nullable=False)
    can_take_calls = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


db.create_all()


@app.route('/')
def show_cafes():
    success = request.args.get("success")
    search_found = request.args.get("search_found")
    color="green"

    result = db.session.execute(db.select(Cafe))
    results = result.scalars()

    rows = db.session.query(func.count(Cafe.id)).scalar()
    # print(rows)

    row_list = []
    for i in range(rows):
        row_list.append(i)
    # print(row_list)

    id = []
    names = []
    img = []
    location = []
    price = []
    seats = []
    plugs = []
    toilet = []
    wifi = []
    map = []
    can_take_calls = []
    for i in results:
        id.append(i.id)
        names.append(i.name)
        img.append(i.img_url)
        location.append(i.location)
        price.append(i.coffee_price)
        seats.append(i.seats)
        map.append(i.map_url)

        if i.has_sockets == "1":
            plugs.append("✅")
        else:
            plugs.append("❎")

        if i.has_toilet == "1":
            toilet.append("✅")
        else:
            toilet.append("❎")

        if i.has_wifi == "1":
            wifi.append("✅")
        else:
            wifi.append("❎")

        if i.can_take_calls == "1":
            can_take_calls.append("✅")
        else:
            can_take_calls.append("❎")

    half = round(len(row_list) / 2)
    len1 = []
    for i in range(half):
        len1.append(i)

    len2 = []
    for i in row_list[half:]:
        len2.append(i)
    not_found = request.args.get("not_found")
    # print(not_found)

    if not_found is None:
        not_found = ""
    if success is None:
        success = ""
    if search_found is None:
        search_found = ""
        color="black"

    return render_template("index.html", success=success, id=id, db_len=row_list, name=names, len1=len1, len2=len2,
                           img=img, location=location,
                           price=price, seats=seats, plugs=plugs, toilet=toilet, wifi=wifi, map=map,
                           not_found=not_found, can_take_calls=can_take_calls,search_found=search_found,color=color)


@app.route('/delete', methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        SECRET_KEY = "ej"
        key = request.form.get('key')
        if key == SECRET_KEY:
            delete_name = request.form.get('delete_name')
            # print(key)
            # print(delete_name)
            cafe_to_delete = db.session.execute(db.select(Cafe).where(Cafe.name == delete_name)).scalar()
            # print(cafe_to_delete)
            if cafe_to_delete is not None:
                db.session.delete(cafe_to_delete)
                db.session.commit()
                success = "Cafe Deleted Sucessfully"
                # print("cafe deleted")
                return redirect(url_for("show_cafes", success=success))
            else:
                success = "Cafe not deleted, right sceret key but wrong cafe name"
                # print("cafe not deleted ,right sceret key but wrong cafe name key")
                return redirect(url_for("show_cafes", success=success))
        else:
            success = "Cafe not deleted, wrong sceret key"
            # print("cafe not deleted , wrong sceret key")
            return redirect(url_for("show_cafes", success=success))


@app.route('/search', methods=["POST"])
def search():
    if request.method == "POST":
        cafe_name = request.form.get("search_name")
        cafe_to_search = db.session.execute(db.select(Cafe).where(Cafe.name == cafe_name)).scalar()

        if cafe_to_search is not None:
            search_result = f"{cafe_to_search.name}"
            return redirect(url_for("search_display", found=search_result))
        else:
            print("Not found")
            not_found = "🔍Search Not Found❌"
            return redirect(url_for("show_cafes", not_found=not_found))


@app.route('/found', methods=['GET'])
def search_display():
    found = request.args.get("found")
    print(found)
    return redirect(url_for("show_cafes",search_found=found))


@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    if request.method == "POST":
        name = request.form.get('name')
        map_url = request.form.get('map_url')
        img_url = request.form.get('img_url')
        location = request.form.get('location')
        seats = request.form.get('seats')
        has_toilet = request.form.get('has_toilet')
        has_wifi = request.form.get('has_wifi')
        has_sockets = request.form.get('has_sockets')
        can_take_calls = request.form.get('can_take_calls')
        coffee_price = f"£{request.form.get('coffee_price')}"

        new_cafe = Cafe(name=name, map_url=map_url, img_url=img_url, location=location, seats=seats,
                        has_toilet=has_toilet,
                        has_wifi=has_wifi, has_sockets=has_sockets, can_take_calls=can_take_calls,
                        coffee_price=coffee_price)
        db.session.add(new_cafe)
        db.session.commit()
        success = "Cafe Details Saved Successfully"
        return render_template("add.html", success=success)
    return render_template("add.html")


@app.route('/update', methods=["GET", "POST"])
def update_cafe():
    update_cafe_id = request.args.get('update_cafe_id')
    update_cafes = db.session.execute(db.select(Cafe).where(Cafe.id == update_cafe_id)).scalar()
    if request.method == "POST":
        name = request.form.get('name')
        map_url = request.form.get('map_url')
        img_url = request.form.get('img_url')
        location = request.form.get('location')
        seats = request.form.get('seats')
        has_toilet = request.form.get('has_toilet')
        has_wifi = request.form.get('has_wifi')
        has_sockets = request.form.get('has_sockets')
        can_take_calls = request.form.get('can_take_calls')
        coffee_price = request.form.get('coffee_price')
        db.session.execute(
            Update(Cafe).where(Cafe.name == name).values(map_url=map_url, img_url=img_url, location=location,
                                                                 seats=seats, has_toilet=has_toilet, has_wifi=has_wifi,
                                                                 has_sockets=has_sockets, coffee_price=coffee_price,
                                                                 can_take_calls=can_take_calls))
        db.session.commit()
        success = "Cafe Details Updated Successfully"
        return render_template("update.html", success=success, update_cafes=update_cafes)
    return render_template("update.html", update_cafes=update_cafes)


if __name__ == "__main__":
    app.run(debug=False)
