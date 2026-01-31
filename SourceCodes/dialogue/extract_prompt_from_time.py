import csv
from datetime import datetime

def read_prompt_by_time(csv_file_path):
    """
    Read corresponding prompt from CSV based on current time period
    
    Time division:
    - Night: 00:00 - 05:59 → Row 5
    - Morning: 06:00 - 11:59 → Row 2
    - Noon: 12:00 - 13:59 → Row 3
    - Evening: 14:00 - 23:59 → Row 4
    
    Args:
        csv_file_path: Path to the CSV file
    
    Returns:
        Corresponding prompt string or error message
    """
    current_hour = datetime.now().hour
    
    # Determine target row index (0-based) and time period
    if 0 <= current_hour < 6:
        target_row = 3
        time_period = "night"
    elif 6 <= current_hour < 12:
        target_row = 0
        time_period = "morning"
    elif 12 <= current_hour < 14:
        target_row = 1
        time_period = "noon"
    else:
        target_row = 2
        time_period = "evening"
    
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            rows = list(csv_reader)
            
            if target_row < len(rows):
                prompt = rows[target_row]['Prompts']
                print(f"Current time period: {time_period} ({current_hour}:00), reading row {target_row} prompt:")
                return prompt
            else:
                return f"Error: No row {target_row} in CSV (file has only {len(rows)} rows including header)"
    
    except FileNotFoundError:
        return f"Error: File not found - {csv_file_path}"
    except KeyError:
        return "Error: 'prompts' column not found in CSV header"
    except Exception as e:
        return f"Error: {str(e)}"

def get_rowidx_from_time():
    current_hour = datetime.now().hour
    print(f" Current Hour: {current_hour}")
    # Determine target row index (0-based) and time period
    if 0 <= current_hour < 6:
        target_row = 3
    elif 6 <= current_hour < 12:
        target_row = 0
    elif 12 <= current_hour < 14:
        target_row = 1
    else:
        target_row = 2
    print(f" Mapped Row Index: {target_row}")
    return target_row

# Usage example
if __name__ == "__main__":
    csv_path = "ScriptsLists\prompts.csv"  # Replace with your actual CSV path
    # result = read_prompt_by_time(csv_path)
    target_row = get_rowidx_from_time()

    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            rows = list(csv_reader)
            
            if target_row < len(rows):
                prompt = rows[target_row]['Prompts']
                time = rows[target_row]['Time']
                location = rows[target_row]['Location']
                print(f"Prompt from row {target_row}: {prompt}: Time: {time}, Location: {location}")
            else:
                print(f"Error: No row {target_row} in CSV (file has only {len(rows)} rows including header)")
    except Exception as e:
        pass
    # print(result)