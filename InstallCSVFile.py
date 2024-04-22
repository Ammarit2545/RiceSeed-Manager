# import pandas as pd
# import mongoengine
# from pymongo import MongoClient
# from models.rice_informations import RiceInformation
# from models.user import User

# # Database connection
# client = MongoClient("localhost", 27017)
# db = client["Softnix2024"]


# mongoengine.connect("mongodb://localhost:27017/Softnix2024")


# def import_csv_to_mongodb(csv_file_path):
#     try:
#         # Read CSV file
#         df = pd.read_csv(csv_file_path, delimiter='\t')

#         # Create a list to store dictionaries of each row
#         data = []

#         # Iterate through each row in the DataFrame
#         for _, row in df.iterrows():
#             # Convert each row to dictionary
#             row_dict = {}
#             # Split the data based on comma and create key-value pairs
#             data_parts = row['_id,Seed_RepDate,Seed_Year,Seeds_YearWeek,Seed_Varity,Seed_RDCSD,Seed_Stock2Sale,Seed_Season,Seed_Crop _Year'].split(',')
#             # Assign key-value pairs to the dictionary
#             row_dict['_id'] = data_parts[0]
#             row_dict['Seed_RepDate'] = data_parts[1]
#             row_dict['Seed_Year'] = data_parts[2]
#             row_dict['Seeds_YearWeek'] = data_parts[3]
#             row_dict['Seed_Varity'] = data_parts[4]
#             row_dict['Seed_RDCSD'] = data_parts[5]
#             row_dict['Seed_Stock2Sale'] = data_parts[6]
#             row_dict['Seed_Season'] = data_parts[7]
#             row_dict['Seed_Crop_Year'] = data_parts[8]

#             # Append the dictionary to the list
#             data.append(row_dict)

        
#         for i in range(len(data)):
#             print("_id : ",data[i]['_id'])
#             print("Seed_RepDate : ", data[i]['Seed_RepDate'], "\n")
            
#             # Create a RiceInformation document
#             rice_info = RiceInformation(
#                 Seed_RepDate=20240101,
#                 Seed_Year=2024,
#                 Seeds_YearWeek=202401,
#                 Seed_Variety="Example Variety",
#                 Seed_RDCSD="Example RDCSD",
#                 Seed_Stock2Sale=100,
#                 Seed_Season="Example Season",
#                 Seed_Crop_Year="2024"
#             )
#             rice_info.save()  # Save the document to the database
#         # Print data
#         print("Len : ",len(data))
#         print("First row: ", data[0]['_id'])  # Print the first row

#         print("Successfully imported data from CSV to MongoDB.")
#     except Exception as e:
#         print(f"Error importing data to MongoDB: {str(e)}")


# if __name__ == "__main__":
#     csv_file_path = r"C:\Users\armm4\OneDrive\เดสก์ท็อป\rice-api-python\CSV\37176ff3-dd70-4f1f-8e1d-83eda3cf77e4.csv"  # ระบุที่อยู่ของไฟล์ CSV ของคุณที่นี่
#     import_csv_to_mongodb(csv_file_path)
