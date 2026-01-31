import csv
import os
from datetime import datetime

def save_to_csv(csv_file_path, current_time, prompt1, prompt2, first_frame_image=""):
    # Required header fields (including FirstFrameImage)
    required_headers = ["CurrentTime", "PromptSuggestion", "LineGeneration", "FirstFrameImage"]
    # Prepare new row data
    new_row = {
        "CurrentTime": current_time,
        "PromptSuggestion": prompt1,
        "LineGeneration": prompt2,
        "FirstFrameImage": first_frame_image
    }
    
    # Check if CSV file exists
    file_exists = os.path.exists(csv_file_path)
    
    if not file_exists:
        # Create new file with headers and new row
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=required_headers)
            writer.writeheader()
            writer.writerow(new_row)
        print(f"✅ Created new CSV: {csv_file_path}")
        print(f"✅ Added initial data: {new_row}")
    else:
        # Read existing file and handle empty file case
        existing_data = []
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            existing_headers = reader.fieldnames or []
            # Check missing required headers
            missing_headers = [h for h in required_headers if h not in existing_headers]
            # Merge headers (keep existing + add missing required)
            updated_headers = existing_headers + missing_headers

            # Read existing rows and add empty values for missing headers
            for row in reader:
                for header in missing_headers:
                    row[header] = ""
                existing_data.append(row)
        
        # Add empty values for extra headers in new row
        for header in updated_headers:
            if header not in new_row:
                new_row[header] = ""
        
        # Write back updated data + new row
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=updated_headers)
            writer.writeheader()
            writer.writerows(existing_data)
            writer.writerow(new_row)
        print(f"✅ Updated CSV: {csv_file_path}")
        print(f"✅ Added new row: {new_row}")
# ------------------- Usage Example -------------------
if __name__ == "__main__":
    # Replace with your CSV file path (e.g., "./data.csv" or "C:/files/output.csv")
    csv_path = "ScriptsLists\generated_lines.csv"
    
    # Example inputs (replace with your actual prompt1 and prompt2)
    sample_prompt1 = "Suggest a morning greeting"
    sample_prompt2 = "Good morning! Hope you have a great day ahead."
    
    # Call the function
    save_to_csv(csv_path, sample_prompt1, sample_prompt2)