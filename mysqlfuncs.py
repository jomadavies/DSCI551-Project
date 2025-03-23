import pymysql
import os
from openai import OpenAI

def get_connection():
    return pymysql.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSERNAME"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE")
    )

def get_databases():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                return [db[0] for db in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching databases: {e}")
        return []

def get_tables(database):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"USE {database}")
                cursor.execute("SHOW TABLES")
                return [table[0] for table in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching tables from {database}: {e}")
        return []
    
def get_schema(table):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DESCRIBE {table}")
                return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching schema for table {table}: {e}")
        return
    
def get_sample_data(table):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching sample data for table {table}: {e}")
        return []
    
def generate_query_or_modification(client, input):
    table_completion = client.chat.completions.create(
        model="model-identifier",
        messages=[
            {"role": "system", 
            "content": f"""
                        You are an expert at writing MYSQL queries. 
                        Based on user input determine the table to generate a query or update statement from.
                        In the case of queries, the user may ask for a query that utilizes multiple tables.
                        In this case, output the name of both tables as a list: [table1, table2].
                        If the user does not provide enough context, such as not specifying the table, respond with "Insufficient context".
                        """,},
            {"role": "user", "content": f"{input}"}
        ],
        temperature=0.7,
        )
    table = table_completion.choices[0].message['content']

    if table == "Insufficient context":
        return "Please provide more context."
    
    if isinstance(table, list):
        schemas = [get_schema(t) for t in table]
        schema_str = "\n".join(schemas)
    else:
        schema_str = get_schema(table)

    completion = client.chat.completions.create(
        model="model-identifier",
        messages=[
            {"role": "system", 
            "content": f"""
                        You are an expert at writing MYSQL queries. Based on the schema of the table(s) and user input, 
                        generate a query. The user may also be requesting to modify data in the table such as an insert, update, or delete statement.
                        Here is the schema of the table(s):
                        {schema_str}
                        """,},
            {"role": "user", "content": f"{input}"}
        ],
        temperature=0.7,
        )
    
    return completion.choices[0].message['content']

def execute_query(query):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()
                return cursor.fetchall()
    except Exception as e:
        print(f"Error executing query: {e}")
        return []
    
def determine_func(client, input):
    completion = client.chat.completions.create(
        model="model-identifier",
        messages=[
            {"role": "system", 
            "content": """
                        You are a MySQL assistant. If a user asks a question, determine which function should be executed in order to help them.
                        The functions you can use are:
                        - get_databases(): Returns a list of all databases.
                        - get_tables(): Returns a list of all tables in the specified database.
                        - get_schema(): Returns the schema of the specified table.
                        - get_sample_data(): Returns a sample of data from the specified table.
                        - generate_query_or_modification(): Generates a query or statement to modify data from a specified table(s) based on user input.

                        If the user asks a question that does not require a function, respond with "I cannot help you with that."
                        Respond with only the name of the function to execute and if applicable the name of the database and table, and nothing else:
                        - "get_databases()"
                        - "[get_tables(), database]"
                        - "[get_schema(), database, table]"
                        - "[get_sample_data(), database, table]"
                        - "[generate_query_or_modification(), database"

                        If they do not provide enough context, such as not specifying the database or table, respond with "Please provide more context."
                        """,},
            {"role": "user", "content": f"{input}"}
        ],
        temperature=0.7,
        )
    
    return completion.choices[0].message['content']

def main():
    client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

    while True:
        user_input = input("Ask a question: ")
        if user_input == "exit":
            break
        func = determine_func(client, user_input)

        if func == "get_databases()":
            print(get_databases())
        elif func.startswith("get_tables"):
            database = func.split(",")[1].strip(" ")
            print(get_tables(database))
        elif func.startswith("get_schema"):
            database = func.split(",")[1].strip(" ")
            table = func.split(",")[2].strip(" ")
            print(get_schema(table))
        elif func.startswith("get_sample_data"):
            database = func.split(",")[1].strip(" ")
            table = func.split(",")[2].strip(" ")
            print(get_sample_data(table))
        elif func.startswith("generate_query_or_modification"):
            database = func.split(",")[1].strip(" ")
            print(generate_query_or_modification(client, input))
        else:
            print(func)

if __name__ == "__main__":
    main()