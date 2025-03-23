import pymysql
import os

# Function to establish connection to the database
def get_connection():
    return pymysql.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSERNAME"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE")
    )

# Function to perform SELECT query
def select_data():
    table_name = input("Enter table name to SELECT data from: ").strip()
    query = f"SELECT * FROM {table_name}"
    
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            for row in result:
                print(row)
        connection.close()
    except Exception as e:
        print(f"Error: {e}")

# Function to perform INSERT query
def insert_data():
    table_name = input("Enter table name to INSERT data into: ").strip()
    columns = input("Enter columns to insert (comma-separated): ").strip()
    values = input("Enter values to insert (comma-separated): ").strip()

    query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
    
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
            print(f"Data inserted into {table_name} successfully.")
        connection.close()
    except Exception as e:
        print(f"Error: {e}")

# Function to perform UPDATE query
def update_data():
    table_name = input("Enter table name to UPDATE data in: ").strip()
    update_values = input("Enter the columns and values to update (e.g., 'column1=value1, column2=value2'): ").strip()
    condition = input("Enter condition for update (e.g., 'id=1'): ").strip()

    query = f"UPDATE {table_name} SET {update_values} WHERE {condition}"
    
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
            print(f"Data updated in {table_name} successfully.")
        connection.close()
    except Exception as e:
        print(f"Error: {e}")

# Function to perform DELETE query
def delete_data():
    table_name = input("Enter table name to DELETE data from: ").strip()
    condition = input("Enter condition for deletion (e.g., 'id=1'): ").strip()

    query = f"DELETE FROM {table_name} WHERE {condition}"
    
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
            print(f"Data deleted from {table_name} successfully.")
        connection.close()
    except Exception as e:
        print(f"Error: {e}")

# Function to print all tables and their attributes (columns)
def print_tables_and_attributes():
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                print(f"\nTable: {table_name}")
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")  # Column name and type
        connection.close()
    except Exception as e:
        print(f"Error: {e}")

# Main function to interact with the user
def main():
    while True:
        print("\nDatabase Operations Menu:")
        print("1. Select data")
        print("2. Insert data")
        print("3. Update data")
        print("4. Delete data")
        print("5. Print tables and attributes")
        print("6. Exit")
        
        choice = input("Choose an option: ").strip()
        
        if choice == "1":
            select_data()
        elif choice == "2":
            insert_data()
        elif choice == "3":
            update_data()
        elif choice == "4":
            delete_data()
        elif choice == "5":
            print_tables_and_attributes()
        elif choice == "6":
            print("Exiting program.")
            break
        else:
            print("Invalid option, please try again.")

# Run the script
if __name__ == "__main__":
    main()
