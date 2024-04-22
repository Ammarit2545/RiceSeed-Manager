from mongoengine import Document, StringField, DateTimeField

class User(Document):
    username = StringField(required=True, unique=True)  # ชื่อผู้ใช้
    password = StringField(required=True)  # รหัสผ่าน
    email = StringField(required=True, unique=True)  # อีเมล
    token = StringField()  # โทเค็น
    tokenExpiresIn = DateTimeField()  # หมดอายุของโทเค็น
