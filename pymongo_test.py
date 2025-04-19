from pymongo import MongoClient
import json

# Function to connect to MongoDB
def get_connection():
    return MongoClient("mongodb://3.22.81.16:27017")

# Function to find data
def find_data():
    db = get_connection().world  # Use the 'world' database
    collection_name = input("Enter collection name to find data from: ").strip()
    query_str = input("Enter query as JSON (e.g., {} or {'name': 'Alice'}): ").strip()
    
    try:
        query = json.loads(query_str.replace("'", '"'))  # Convert input to JSON format
        collection = db[collection_name]
        results = collection.find(query)
        if results.count() == 0:
            print("No results found.")
        for doc in results:
            print(doc)
    except Exception as e:
        print(f"Error: {e}")

# Function to insert data
def insert_data():
    db = get_connection().world  # Use the 'world' database
    collection_name = input("Enter collection name to insert into: ").strip()
    data_str = input("Enter data as JSON (e.g., {'name': 'Alice', 'age': 25}): ").strip()
    
    try:
        data = json.loads(data_str.replace("'", '"'))
        collection = db[collection_name]
        collection.insert_one(data)
        print("Document inserted successfully.")
    except Exception as e:
        print(f"Error: {e}")

# Function to update data
def update_data():
    db = get_connection().world  # Use the 'world' database
    collection_name = input("Enter collection name to update: ").strip()
    filter_str = input("Enter filter as JSON (e.g., {'name': 'Alice'}): ").strip()
    update_str = input("Enter update as JSON (e.g., {'$set': {'age': 26}}): ").strip()
    
    try:
        filter_doc = json.loads(filter_str.replace("'", '"'))
        update_doc = json.loads(update_str.replace("'", '"'))
        collection = db[collection_name]
        result = collection.update_many(filter_doc, update_doc)
        print(f"Updated {result.modified_count} documents.")
    except Exception as e:
        print(f"Error: {e}")

# Function to delete data
def delete_data():
    db = get_connection().world  # Use the 'world' database
    collection_name = input("Enter collection name to delete from: ").strip()
    filter_str = input("Enter filter as JSON (e.g., {'name': 'Alice'}): ").strip()

    try:
        filter_doc = json.loads(filter_str.replace("'", '"'))
        collection = db[collection_name]
        result = collection.delete_many(filter_doc)
        print(f"Deleted {result.deleted_count} documents.")
    except Exception as e:
        print(f"Error: {e}")

# Function to print collections and sample fields
def print_collections_and_fields():
    db = get_connection().world  # Use the 'world' database
    try:
        collections = db.list_collection_names()  # Get list of collections
        if not collections:
            print("No collections found.")
        for col in collections:
            print(f"\nCollection: {col}")
            sample_doc = db[col].find_one()  # Fetch sample document to get fields
            if sample_doc:
                print("Sample Fields:")
                for key in sample_doc.keys():
                    print(f"  - {key}")
            else:
                print("  (No documents yet)")
    except Exception as e:
        print(f"Error: {e}")

# Main menu
def main():
    while True:
        print("\nMongoDB Operations Menu:")
        print("1. Find documents")
        print("2. Insert a document")
        print("3. Update documents")
        print("4. Delete documents")
        print("5. Show collections and fields")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            find_data()
        elif choice == "2":
            insert_data()
        elif choice == "3":
            update_data()
        elif choice == "4":
            delete_data()
        elif choice == "5":
            print_collections_and_fields()
        elif choice == "6":
            print("Exiting program.")
            break
        else:
            print("Invalid option, try again.")

# Run
if __name__ == "__main__":
    main()
