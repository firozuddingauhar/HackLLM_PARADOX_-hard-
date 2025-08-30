import json
import csv

def convert_jsonl_to_csv(jsonl_file_path, csv_file_path):
    """
    Reads data from a JSONL file and writes it to a CSV file.

    Each line in the JSONL file is treated as a separate JSON object.
    The script automatically determines headers from the keys of the first
    JSON object. It handles nested lists by joining them into a single
    comma-separated string.

    Args:
        jsonl_file_path (str): The path to the input JSONL file.
        csv_file_path (str): The path for the output CSV file.
    """
    try:
        with open(jsonl_file_path, 'r', encoding='utf-8') as jsonl_file:
            # Read all lines from the file at once
            lines = jsonl_file.readlines()
            if not lines:
                print("JSONL file is empty. No CSV file will be created.")
                return

            # --- Process the data ---
            data = [json.loads(line) for line in lines]

            # Get headers from the first object's keys
            headers = list(data[0].keys())

            # --- Write to CSV ---
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=headers)
                writer.writeheader()

                for item in data:
                    # Create a copy to modify for CSV writing
                    row_to_write = {}
                    for key, value in item.items():
                        # If a value is a list, join it into a single string
                        if isinstance(value, list):
                            # Convert all items in the list to string before joining
                            row_to_write[key] = ', '.join(map(str, value))
                        else:
                            row_to_write[key] = value
                    
                    # Ensure all headers are present in the row, even if empty
                    # This handles cases where some JSON objects might be missing keys
                    full_row = {header: row_to_write.get(header, '') for header in headers}
                    writer.writerow(full_row)

            print(f"Successfully converted '{jsonl_file_path}' to '{csv_file_path}'")

    except FileNotFoundError:
        print(f"Error: The file '{jsonl_file_path}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # Define the input and output file names.
    input_filename = 'data/train.jsonl'
    output_filename = 'train.csv'

    # Call the conversion function
    convert_jsonl_to_csv(input_filename, output_filename)
