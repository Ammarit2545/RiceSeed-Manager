from pymongo import MongoClient

# เชื่อมต่อกับ MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Softnix2024']

# ค้นหาข้อมูลล่าสุดของแถว
latest_data = db.rice_informations.find().sort([('_id', -1)]).limit(1)

# ถ้ามีข้อมูล
if latest_data.count() > 0:
    latest_id = latest_data[0]['_id']
    print("Latest ID:", latest_id)
else:
    print("No data found")
