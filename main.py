# Package
import csv
from flask import Flask, request, jsonify
from pymongo import MongoClient
import mongoengine
from datetime import datetime, timedelta
import json
from flasgger import Swagger
#from flask_jwt_extended import create_access_token

#Model
from models.rice_informations import RiceInformation
from models.user import User
from pytz import timezone
import jwt  # Import jwt module for JWT functionality


app = Flask(__name__)
Swagger(app)

# Database connection
mongoengine.connect("Softnix2024", host="localhost", port=27017)

# กำหนด timezone ของประเทศไทย
thailand_timezone = timezone('Asia/Bangkok')

# หาเวลาปัจจุบัน (UTC)
utc_now = datetime.utcnow()

# แปลงเวลา UTC เป็นเวลาในประเทศไทย
thailand_now = utc_now.astimezone(thailand_timezone)

# พิมพ์ผลลัพธ์
print("UTC Now:", utc_now)
print("Thailand Now:", thailand_now)

# Check if the database exists, if not, create it
if "Softnix2024" not in MongoClient().list_database_names():
    db = MongoClient()["Softnix2024"]

    def import_csv_to_list(csv_file_path):
        data_list = []
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                data_list.append(row)
        return data_list

    def import_csv_to_mongodb(csv_file_path):
        data = import_csv_to_list(csv_file_path)
        for i in range(len(data)):
            try:
                n = int(data[i][6].replace(',', ''))
                rice_info = RiceInformation(
                    id_rice=data[i][0],
                    Seed_RepDate=data[i][1],
                    Seed_Year=data[i][2],
                    Seeds_YearWeek=data[i][3],
                    Seed_Variety=data[i][4],
                    Seed_RDCSD=data[i][5],
                    Seed_Stock2Sale=n,
                    Seed_Season=data[i][7],
                    Seed_Crop_Year=data[i][8]
                )
                rice_info.save()
            except Exception as e:
                print(f"Error occurred in row {i+1}: {e}")

        user = User(
            username="admin",
            password="1234",
            email="admin@gmail.com",
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwidXNlcklkIjoiNjYyNTBkMjBjOTZlNmUyMDY1NTZhYTU5IiwiaWF0IjoxNzEzNzEzMTc1LCJleHAiOjE3MTM3MTY3NzV9.njd0XGUHyq9QGRtu8WAS2h8PnE4a_a04GGTwNiNojz0",
            tokenExpiresIn=datetime.utcnow() + timedelta(days=0, hours=8)
        )
        user.save()

@app.route("/allproducts", methods=["GET"])
def get_productsall(id=None):
    """
    Retrieve all rice products or a specific rice product by ID.
    ---
    parameters:
      - name: token
        in: query
        type: string
        description: User token for authentication (optional)
    responses:
      200:
        description: A list of rice products or a single rice product.
        schema:
          type: object
          properties:
            id_rice:
              type: string
              description: The ID of the rice product.
            Seed_RepDate:
              type: string
              description: The representation date of the rice product.
            Seed_Year:
              type: string
              description: The year of the rice product.
            Seeds_YearWeek:
              type: string
              description: The year and week of the rice product.
            Seed_Variety:
              type: string
              description: The variety of the rice product.
            Seed_RDCSD:
              type: string
              description: The RDCSD of the rice product.
            Seed_Stock2Sale:
              type: integer
              description: The stock available for sale of the rice product.
            Seed_Season:
              type: string
              description: The season of the rice product.
            Seed_Crop_Year:
              type: string
              description: The crop year of the rice product.
      404:
        description: Product not found.
    """
    try:
        token = request.args.get("token")  # Get token from query string

        #--------------------------------------------------------------------------
        # Check if token is provided
        if not token:
            return jsonify({"error": "Unauthorized - Token missing"}), 401

        
        # Check if token is valid and not expired
        user = User.objects(token=token).first()
        Token_check = False
        import pytz
        # ที่ส่วนของ timezone ของประเทศไทย
        thailand_timezone = pytz.timezone('Asia/Bangkok')   
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)  # เวลาปัจจุบันในรูปแบบ UTC
        thailand_now = utc_now.astimezone(thailand_timezone)  # เวลาปัจจุบันในรูปแบบของประเทศไทย

        token_expires_in_utc = user.tokenExpiresIn
        formatted_token_expires_in_utc = token_expires_in_utc.strftime("%Y-%m-%d %H:%M:%S")
        formatted_thailand_now = thailand_now.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\ttokenExpiresIns : {formatted_token_expires_in_utc} --- TH : {formatted_thailand_now}")

        if formatted_token_expires_in_utc > formatted_thailand_now:
            print("\n----- Token Can uSe \n")
            Token_check = True

        
        if not user:
            return jsonify({"error": "Unauthorized - Token expired or invalid"}), 401
        #--------------------------------------------------------------------------
        if id and Token_check == True:
            product = RiceInformation.objects(id_rice=id).first()
            if product:
                product_json = json.loads(product.to_json())
                product_json["_id"] = str(product_json["_id"])
                product_json["Seed_Variety"] = product_json["Seed_Variety"]
                product_json["Seed_RDCSD"] = product_json["Seed_RDCSD"]
                return jsonify(product_json), 200
            else:
                return jsonify({"message": "Product not found"}), 404
        elif Token_check == True:
            products = RiceInformation.objects().all()
            product_list = []
            for product in products:
                product_dict = json.loads(product.to_json())
                product_dict["_id"] = str(product_dict["_id"])
                product_dict["Seed_Variety"] = product_dict["Seed_Variety"]
                product_dict["Seed_RDCSD"] = product_dict["Seed_RDCSD"]
                product_list.append(product_dict)
            return jsonify(product_list), 200
        else :
            return jsonify({"error": "Unauthorized - Token expired or invalid"}), 401
            
    except Exception as e:
        print("An error occurred while retrieving products:", e)
        return jsonify({"error": "An error occurred while retrieving products"}), 500
@app.route("/products", methods=["GET"])
def get_products():
    """
    Retrieve all rice products or a specific rice product by ID.
    ---
    parameters:
      - name: id
        in: query
        type: string
        description: ID of the rice product to retrieve (optional)
      - name: token
        in: query
        type: string
        description: User token for authentication (optional)
    responses:
      200:
        description: A list of rice products or a single rice product.
        schema:
          type: object
          properties:
            id_rice:
              type: string
              description: The ID of the rice product.
            Seed_RepDate:
              type: string
              description: The representation date of the rice product.
            Seed_Year:
              type: string
              description: The year of the rice product.
            Seeds_YearWeek:
              type: string
              description: The year and week of the rice product.
            Seed_Variety:
              type: string
              description: The variety of the rice product.
            Seed_RDCSD:
              type: string
              description: The RDCSD of the rice product.
            Seed_Stock2Sale:
              type: integer
              description: The stock available for sale of the rice product.
            Seed_Season:
              type: string
              description: The season of the rice product.
            Seed_Crop_Year:
              type: string
              description: The crop year of the rice product.
      401:
        description: Unauthorized - Token missing or expired.
      404:
        description: Product not found.
    """
    try:
        id = request.args.get("id")  # Get ID from query string
        token = request.args.get("token")  # Get token from query string

        #--------------------------------------------------------------------------
        # Check if token is provided
        if not token:
            return jsonify({"error": "Unauthorized - Token missing"}), 401

        
        # Check if token is valid and not expired
        user = User.objects(token=token).first()
        Token_check = False
        import pytz
        # ที่ส่วนของ timezone ของประเทศไทย
        thailand_timezone = pytz.timezone('Asia/Bangkok')   
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)  # เวลาปัจจุบันในรูปแบบ UTC
        thailand_now = utc_now.astimezone(thailand_timezone)  # เวลาปัจจุบันในรูปแบบของประเทศไทย

        token_expires_in_utc = user.tokenExpiresIn
        formatted_token_expires_in_utc = token_expires_in_utc.strftime("%Y-%m-%d %H:%M:%S")
        formatted_thailand_now = thailand_now.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\ttokenExpiresIns : {formatted_token_expires_in_utc} --- TH : {formatted_thailand_now}")

        if formatted_token_expires_in_utc > formatted_thailand_now:
            print("\n----- Token Can uSe \n")
            Token_check = True

        
        if not user:
            return jsonify({"error": "Unauthorized - Token expired or invalid"}), 401
        #--------------------------------------------------------------------------

        if not id:
            # If ID is not provided in query string, try to get it from request body
            data = request.get_json()
            if data and "id" in data:
                id = data["id"]

        if id and Token_check == True:
            product = RiceInformation.objects(id_rice=id).first()
            if product:
                product_json = json.loads(product.to_json())
                product_json["_id"] = str(product_json["_id"])
                product_json["Seed_Variety"] = product_json["Seed_Variety"]
                product_json["Seed_RDCSD"] = product_json["Seed_RDCSD"]
                return jsonify(product_json), 200
            else:
                return jsonify({"message": "Product not found"}), 404
        elif Token_check == True:
            products = RiceInformation.objects().all()
            product_list = []
            for product in products:
                product_dict = json.loads(product.to_json())
                product_dict["_id"] = str(product_dict["_id"])
                product_dict["Seed_Variety"] = product_dict["Seed_Variety"]
                product_dict["Seed_RDCSD"] = product_dict["Seed_RDCSD"]
                product_list.append(product_dict)
            return jsonify({"message": "Product not found"}), 404
        else :
            return jsonify({"error": "Unauthorized - Token expired or invalid"}), 401
    except Exception as e:
        print("An error occurred while retrieving products:", e)
        return jsonify({"error": "An error occurred while retrieving products"}), 500


@app.route("/products", methods=["POST"])
def post_product():
    """
    Insert a rice product by ID.
    ---
    parameters:
      - name : Seed_RepDate
        in: query
        type: string
        description: Seed_RepDate of the rice product to Insert
        required: true
      - name : Seed_Year
        in: query
        type: string
        description: Seed_Year of the rice product to Insert
        required: true
      - name : Seeds_YearWeek
        in: query
        type: string
        description: Seeds_YearWeek of the rice product to Insert
        required: true
      - name : Seed_Variety
        in: query
        type: string
        description: Seed_Variety of the rice product to Insert
        required: true
      - name : Seed_RDCSD
        in: query
        type: string
        description: Seed_RDCSD of the rice product to Insert
        required: true
      - name : Seed_Stock2Sale
        in: query
        type: string
        description: Seed_Stock2Sale of the rice product to Insert
        required: true
      - name : Seed_Season
        in: query
        type: string
        description: Seed_Season of the rice product to Insert
        required: true
      - name : Seed_Crop_Year
        in: query
        type: string
        description: Seed_Crop_Year of the rice product to Insert
        required: true

      - name: token
        in: query
        type: string
        description: User token for authentication (optional)
     
    responses:
      200:
        description: Product Insert successfully.
      404:
        description: Product not found.
      500:
        description: An error occurred while deleting product.
      401:
        description: Unauthorized - Token missing or expired.

    """
    try:
        Seed_RepDate = request.args.get("Seed_RepDate")  # Get ID from query string
        Seed_Year = request.args.get("Seed_Year")  # Get ID from query string
        Seeds_YearWeek = request.args.get("Seeds_YearWeek")  # Get ID from query string
        Seed_Variety = request.args.get("Seed_Variety")  # Get ID from query string
        Seed_RDCSD = request.args.get("Seed_RDCSD")  # Get ID from query string
        Seed_Stock2Sale = request.args.get("Seed_Stock2Sale")  # Get ID from query string
        Seed_Season = request.args.get("Seed_Season")  # Get ID from query string
        Seed_Crop_Year = request.args.get("Seed_Crop_Year")  # Get ID from query string
        token = request.args.get("token")  # Get token from query string
        
        print("\t --- Token : ", token)
        print("Seed_RepDate:", Seed_RepDate)
        print("Seed_Year:", Seed_Year)
        print("Seeds_YearWeek:", Seeds_YearWeek)
        print("Seed_Variety:", Seed_Variety)
        print("Seed_RDCSD:", Seed_RDCSD)
        print("Seed_Stock2Sale:", Seed_Stock2Sale)
        print("Seed_Season:", Seed_Season)
        print("Seed_Crop_Year:", Seed_Crop_Year)


        # Check if the rice information already exists in the database
        existing_info = RiceInformation.objects(
            Seed_RepDate=int(Seed_RepDate),
            Seed_Year=int(Seed_Year),
            Seeds_YearWeek=int(Seeds_YearWeek),
            Seed_Variety=f"{Seed_Variety}",
            Seed_RDCSD=f"{Seed_RDCSD}",
            Seed_Season=f"{Seed_Season}",
            Seed_Crop_Year=f"{Seed_Crop_Year}"
        ).first()

        
        #--------------------------------------------------------------------------
        # Check if token is provided
        if not token:
            return jsonify({"error": "Unauthorized - Token missing"}), 401

        # Check if token is valid and not expired
        user = User.objects(token=token).first()
        if not user:
            return jsonify({"error": "Unauthorized - Token expired or invalid"}), 401

        import pytz
        from datetime import datetime

        latest_product = RiceInformation.objects.order_by('-id_rice').first()
        latest_id = False
        if latest_product:
            latest_id = latest_product.id_rice
            latest_id += 1
            print("\nAdd New ID:", latest_id,"\n")
        else:
            print("No data found")

        # ที่ส่วนของ timezone ของประเทศไทย
        thailand_timezone = pytz.timezone('Asia/Bangkok')   
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)  # เวลาปัจจุบันในรูปแบบ UTC
        thailand_now = utc_now.astimezone(thailand_timezone)  # เวลาปัจจุบันในรูปแบบของประเทศไทย

        token_expires_in_utc = user.tokenExpiresIn
        formatted_token_expires_in_utc = token_expires_in_utc.strftime("%Y-%m-%d %H:%M:%S")
        formatted_thailand_now = thailand_now.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\ttokenExpiresIns : {formatted_token_expires_in_utc} --- TH : {formatted_thailand_now}")
        if existing_info:
            print("Already Have Information:", existing_info)
            return jsonify({"error": "Already Have Information"}), 401
        else:
            print("No existing information found")
            if formatted_token_expires_in_utc > formatted_thailand_now:
                print("\n----- Token Can uSe \n")
                # Insert rice product information into the database here
                data = [latest_id,Seed_RepDate,Seed_Year,Seeds_YearWeek,f"{Seed_Variety}",f"{Seed_RDCSD}",Seed_Stock2Sale,f"{Seed_Season}",f"{Seed_Crop_Year}"]
                rice_info = RiceInformation(
                        id_rice=data[0],
                        Seed_RepDate=data[1],
                        Seed_Year=data[2],
                        Seeds_YearWeek=data[3],
                        Seed_Variety=data[4],
                        Seed_RDCSD=data[5],
                        Seed_Stock2Sale=data[5],
                        Seed_Season=data[7],
                        Seed_Crop_Year=data[8]
                    )
                rice_info.save()
                return jsonify({"message": "Product Insert successfully."}), 200
            else:
                return jsonify({"error": "Unauthorized - Token expired"}), 401
        
    except Exception as e:
        print("An error occurred:", e)
        return jsonify({"error": "An error occurred while inserting product"}), 500

@app.route("/products", methods=["DELETE"])
def delete_product():
    """
    Delete a rice product by ID.
    ---
    parameters:
      - name: id
        in: query
        type: string
        description: ID of the rice product to delete
        required: true
      - name: token
        in: query
        type: string
        description: User token for authentication (optional)

    responses:
      200:
        description: Product deleted successfully.
      404:
        description: Product not found.
      500:
        description: An error occurred while deleting product.
      401:
        description: Unauthorized - Token missing or expired.

    """
    
    try:
        id = request.args.get("id")  # Get ID from query string
        token = request.args.get("token")  # Get token from query string

        #--------------------------------------------------------------------------
        # Check if token is provided
        if not token:
            return jsonify({"error": "Unauthorized - Token missing"}), 401

        
        # Check if token is valid and not expired
        user = User.objects(token=token).first()
        Token_check = False
        import pytz
        # ที่ส่วนของ timezone ของประเทศไทย
        thailand_timezone = pytz.timezone('Asia/Bangkok')   
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)  # เวลาปัจจุบันในรูปแบบ UTC
        thailand_now = utc_now.astimezone(thailand_timezone)  # เวลาปัจจุบันในรูปแบบของประเทศไทย

        token_expires_in_utc = user.tokenExpiresIn
        formatted_token_expires_in_utc = token_expires_in_utc.strftime("%Y-%m-%d %H:%M:%S")
        formatted_thailand_now = thailand_now.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\ttokenExpiresIns : {formatted_token_expires_in_utc} --- TH : {formatted_thailand_now}")

        if formatted_token_expires_in_utc > formatted_thailand_now:
            print("\n----- Token Can uSe \n")
            Token_check = True

        
        if not user:
            return jsonify({"error": "Unauthorized - Token expired or invalid"}), 401
        #--------------------------------------------------------------------------
        if not id:
            # If ID is not provided in query string, try to get it from request body
            data = request.get_json()
            if not data or "id" not in data:
                return jsonify({"error": "No or invalid data provided"}), 400
            id = data["id"]

        product = RiceInformation.objects(id_rice=id).first()

        if product and Token_check == True:
            product.delete()
            return jsonify({"message": "Product deleted successfully"}), 200
        elif Token_check == False:
            return jsonify({"error": "Unauthorized - Token expired or invalid"}), 401
        else:
            return jsonify({"message": "Product not found"}), 404
    except Exception as e:
        print("An error occurred while deleting product:", e)
        return jsonify({"error": "An error occurred while deleting product"}), 500

@app.route("/products", methods=["PUT"])
def put_product():
    """
    Update a rice product by ID.
    ---
    parameters:
      - name : id
        in: query
        type: string
        description: ID of the rice product to update
        required: true
      - name : Seed_RepDate
        in: query
        type: string
        description: Seed_RepDate of the rice product to update
        required: true
      - name : Seed_Year
        in: query
        type: string
        description: Seed_Year of the rice product to update
        required: true
      - name : Seeds_YearWeek
        in: query
        type: string
        description: Seeds_YearWeek of the rice product to update
        required: true
      - name : Seed_Variety
        in: query
        type: string
        description: Seed_Variety of the rice product to update
        required: true
      - name : Seed_RDCSD
        in: query
        type: string
        description: Seed_RDCSD of the rice product to update
        required: true
      - name : Seed_Stock2Sale
        in: query
        type: string
        description: Seed_Stock2Sale of the rice product to update
        required: true
      - name : Seed_Season
        in: query
        type: string
        description: Seed_Season of the rice product to update
        required: true
      - name : Seed_Crop_Year
        in: query
        type: string
        description: Seed_Crop_Year of the rice product to update
        required: true
      - name: token
        in: query
        type: string
        description: User token for authentication (optional)
      
    responses:
      200:
        description: Product updated successfully.
      404:
        description: Product not found.
      500:
        description: An error occurred while updating product.
      401:
        description: Unauthorized - Token missing or expired.
    """
    try:
        # Check if token is provided
        token = request.args.get("token")  # Get token from query string

        #--------------------------------------------------------------------------
        # Check if token is provided
        if not token:
            return jsonify({"error": "Unauthorized - Token missing"}), 401

        
        # Check if token is valid and not expired
        user = User.objects(token=token).first()
        Token_check = False
        import pytz
        # ที่ส่วนของ timezone ของประเทศไทย
        thailand_timezone = pytz.timezone('Asia/Bangkok')   
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)  # เวลาปัจจุบันในรูปแบบ UTC
        thailand_now = utc_now.astimezone(thailand_timezone)  # เวลาปัจจุบันในรูปแบบของประเทศไทย

        token_expires_in_utc = user.tokenExpiresIn
        formatted_token_expires_in_utc = token_expires_in_utc.strftime("%Y-%m-%d %H:%M:%S")
        formatted_thailand_now = thailand_now.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\ttokenExpiresIns : {formatted_token_expires_in_utc} --- TH : {formatted_thailand_now}")

        if formatted_token_expires_in_utc > formatted_thailand_now:
            print("\n----- Token Can uSe \n")
            Token_check = True

        
        if not user:
            return jsonify({"error": "Unauthorized - Token expired or invalid"}), 401
        #--------------------------------------------------------------------------

        if not token:
            return jsonify({"error": "Unauthorized - Token missing"}), 401

        # Get product ID from query string
        id_rice = request.args.get("id")
        if not id_rice:
            return jsonify({"error": "Product ID missing"}), 400

        # Check if the product exists
        product = RiceInformation.objects(id_rice=id_rice).first()
        if not product:
            return jsonify({"error": "Product not found"}), 404
        if Token_check :
            # Update product information
            product.Seed_RepDate = request.args.get("Seed_RepDate")
            product.Seed_Year = request.args.get("Seed_Year")
            product.Seeds_YearWeek = request.args.get("Seeds_YearWeek")
            product.Seed_Variety = request.args.get("Seed_Variety")
            product.Seed_RDCSD = request.args.get("Seed_RDCSD")
            product.Seed_Stock2Sale = request.args.get("Seed_Stock2Sale")
            product.Seed_Season = request.args.get("Seed_Season")
            product.Seed_Crop_Year = request.args.get("Seed_Crop_Year")
            product.save()

            return jsonify({"message": "Product updated successfully."}), 200
        else:
            return jsonify({"error": "Unauthorized - Token expired or invalid"}), 401
    except Exception as e:
        print("An error occurred:", e)
        return jsonify({"error": "An error occurred while updating product"}), 500

@app.route("/login", methods=["POST"])
def logincheck():
    """
    Check user credentials for login.
    ---
    parameters:
      - name: username
        in: query
        type: string
        description: Username for login
        required: true
      - name: password
        in: query
        type: string
        description: Password for login
        required: true
    responses:
      200:
        description: User successfully authenticated.
      401:
        description: Unauthorized - Invalid credentials.
      500:
        description: An error occurred while processing the request.
    """
    try:
        username = request.args.get("username")  # Get username from query string
        password = request.args.get("password")  # Get password from query string
        
        print(f"Username : {username} , Password : {password}")

        user = User.objects(username=username, password=password).first()
        if user:
            token = "asdasdasd"
            # Generate JWT token with expiry time
            token_expiry = datetime.utcnow() + timedelta(hours=8)
            

            # Secret key for signing the token (replace with your own secure key)
            secret_key = 'Softnix'

            # Generate JWT token with expiry
            token_expiry = datetime.utcnow() + timedelta(hours=8)
            payload = {'user': username, 'exp': token_expiry}
            token = jwt.encode(payload, secret_key, algorithm='HS256')

            userToken = User.objects(username=username).first()
            userToken.token = token
            userToken.tokenExpiresIn = token_expiry
            userToken.save()
            print("token_expiry : ",token_expiry)
            return jsonify({"message": "User successfully authenticated.","token_expiry":token_expiry, "token": token}), 200
        else:
            return jsonify({"error": "Unauthorized - Invalid credentials"}), 401
            
    except Exception as e:
        print("An error occurred:", e)
        return jsonify({"error": "An error occurred while processing the request"}), 500


if __name__ == "__main__":
    csv_file_path = r"C:\Users\armm4\OneDrive\เดสก์ท็อป\rice-api-python\CSV\37176ff3-dd70-4f1f-8e1d-83eda3cf77e4.csv"
    try :
        import_csv_to_mongodb(csv_file_path)
    except:
        print("Error CSV - Insert Successfully!!!")
    app.run(debug=True)
