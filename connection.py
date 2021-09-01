import database_data_manager
import csv
import os
import bcrypt

IMG_DIR = "static/images/"


def return_table_headers(table_name):
    return [header["column_name"] for header in database_data_manager.get_headers(table_name)]


def create_new_record(headers):
    new_record = dict.fromkeys(headers)
    new_record["image"] = "NULL"
    return new_record


def save_photo(data_from_form, image):
    data_from_form["image"] = None
    if image:
        image.save(os.path.join(IMG_DIR, image.filename))
        image_to_import = f"images/{image.filename}"
        data_from_form["image"] = image_to_import
    return data_from_form


def hash_password(raw_password):
    hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def check_password(plain_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_bytes_password)
