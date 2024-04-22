from mongoengine import Document, StringField, IntField

class RiceInformation(Document):
    id_rice = IntField()  # ไอดี
    Seed_RepDate = IntField()  # วันที่รายงานเมล็ดพันธุ์
    Seed_Year = IntField()  # ปีของเมล็ดพันธุ์
    Seeds_YearWeek = IntField()  # สัปดาห์ของปีของเมล็ดพันธุ์
    Seed_Variety = StringField()  # พันธุ์ข้าว
    Seed_RDCSD = StringField()  # รหัสข้าวพันธุ์
    Seed_Stock2Sale = IntField()  # ปริมาณเมล็ดพันธุ์ที่ขาย
    Seed_Season = StringField()  # ฤดูเพาะปลูก
    Seed_Crop_Year = StringField()  # ปีเก็บเกี่ยว
