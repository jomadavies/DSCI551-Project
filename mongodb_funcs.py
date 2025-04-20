import re
from pymongo import MongoClient
from openai import OpenAI
from pprint import pprint

def get_connection():
    return MongoClient("mongodb://3.143.17.46:27017")

def get_collections(database):
    try:
        client = get_connection()
        return client[database].list_collection_names()
    except Exception as e:
        print(f"Error fetching collections from {database}: {e}")
        return []

def get_schema(database, collection):
    try:
        client = get_connection()
        doc = client[database][collection].find_one()
        return list(doc.keys()) if doc else []
    except Exception as e:
        print(f"Error fetching schema for {collection}: {e}")
        return []

def get_sample_data(database, collection):
    try:
        client = get_connection()
        sample_data = client[database][collection].find().limit(1)
        pprint(list(sample_data))
    except Exception as e:
        print(f"Error fetching sample data: {e}")
        return []

def generate_query_or_modification(client, user_input, database):
    collections = get_collections(database)
    schemas = {col: get_schema(database, col) for col in collections}
    collection_info = "\n".join([f"{col}: {fields}" for col, fields in schemas.items()])

    completion = client.chat.completions.create(
        model="gemma-3-4B-it-QAT-Q4_0.gguf",
        messages=[
            {
                "role": "system",
                "content": f"""
                    You are a MongoDB expert. A user will describe a query they want to run.
                    Use the provided collection names and their sample fields to write a valid MongoDB find(), insert(), update(), or aggregate() query.
                    COLLECTIONS:\n{collection_info}
                """
            },
            {"role": "user", "content": user_input}
        ],
        temperature=0.7
    )

    return completion.choices[0].message.content

# Updated determine_func function that can infer the collection name from the user's input
def determine_func(client, input, database):
    completion = client.chat.completions.create(
        model="gemma-3-4B-it-QAT-Q4_0.gguf",
        messages=[
            {
                "role": "system",
                "content": f"""
                    You are a MongoDB assistant. If a user asks a question, determine which function should be executed in order to help them.
                    The functions you can use are:
                    - get_collections(): the arguments are the database name.
                    - get_schema(): the arguments are the database name and the collection name. The collection name will be provided in the user's question.
                    - get_sample_data(): the arguments are the database name and the collection name. The collection name will be provided in the user's question.
                    - generate_query_or_modification(): the arguments are [database]
                    
                    Based on the user's input, infer the collection name if it's missing, and generate the correct function call.
                    Once the user chooses the database, use the database name in the function call.
                    If collection name or context is missing, ask the user to clarify.
                    Respond only with the function call in plain text. Do not use backticks or markdown formatting.
                """
            },
            {"role": "user", "content": input}
        ],
        temperature=0.7
    )

    return completion.choices[0].message.content.strip()

def main():
    client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

    # Prompt the user to choose a database
    databases = ["steam_games", "covid_who", "gym_data"]
    print("Available databases:")
    for idx, db in enumerate(databases):
        print(f"{idx + 1}. {db}")

    db_choice = input("Choose a database by name or number: ").strip()
    if db_choice.isdigit():
        db_index = int(db_choice) - 1
        if 0 <= db_index < len(databases):
            database = databases[db_index]
        else:
            print("Invalid selection. Exiting.")
            return
    elif db_choice in databases:
        database = db_choice
    else:
        print("Invalid selection. Exiting.")
        return

    print(f"\nUsing database: {database}\n")

    while True:
        user_input = input("Ask a question (or type 'exit'): ")
        if user_input.lower() == "exit":
            break

        # Get the correct function to call based on user input
        func = determine_func(client, user_input, database)
        print(f"\nInterpreted function: {func}")

        try:
            # Use the function determined by the LLM
            if "get_collections" in func:
                print(get_collections(database))

            elif "get_schema" in func:
                # Extract collection name from LLM output and call get_schema
                match = re.search(r"get_schema\(\s*'([^']+)'", func)
                if match:
                    collection_name = match.group(1)
                    print(f"DEBUG - Collection to get schema: {collection_name}")
                    print(get_schema(database, collection_name))
                else:
                    print("Error: Could not infer collection name for schema.")

            elif "get_sample_data" in func:
                try:
                    # Use regex to extract collection name from the function call
                    match = re.search(r"get_sample_data\(\s*database=['\"]([^'\"]+)['\"],\s*collection=['\"]([^'\"]+)['\"]\)", func)
                    if match:
                        database_name = database
                        collection_name = match.group(2)
                        print(f"DEBUG - Database: {database_name}, Collection to get sample data: {collection_name}")
                        print(get_sample_data(database_name, collection_name))  # Call with correct collection
                    else:
                        print("Error: Could not infer database or collection name for sample data.")
                except Exception as e:
                    print(f"Error parsing collection for sample data: {e}")
                    print("Could not parse collection name from function output.")

            elif "generate_query_or_modification" in func:
                print(generate_query_or_modification(client, user_input, database))

            else:
                print(f"Unrecognized function output: {func}")

        except Exception as e:
            print(f"Error processing request: {e}")

if __name__ == "__main__":
    main()
