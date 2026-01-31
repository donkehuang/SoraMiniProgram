import csv
import datetime
import os
from openai import OpenAI
from openai.types import Video
import re

client = OpenAI()


def save_video_to_csv(video: Video, current_time: str, filename: str = "video_status.csv"):
    """
    Save Video object data to an existing CSV (with 3 original headers: CurrentTime, PromptSuggestion, LineGeneration).
    - current_time is passed from external (matches "CurrentTime" in CSV for row matching)
    - Add Video-related columns if they don't exist.
    - Match target row by "CurrentTime" and fill Video data.
    - Append new row if no matching time found.
    
    Parameters:
        video: OpenAI Video type object to be saved
        current_time: External input time string (format: "YYYY-MM-DD HH:MM:SS", must match CSV's "CurrentTime" format)
        filename: Output file name, default is "video_status.csv"
    """
    # Validate current_time format (expected: YYYY-MM-DD HH:MM:SS)
    time_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}_\d{2}_\d{2}$'
    if not re.match(time_pattern, current_time):
        raise ValueError(f"Invalid current_time format! Expected 'YYYY-MM-DD HH_MM_SS', got '{current_time}'")
    
    # Define Video-related attributes (will be added as new columns)
    video_attributes = [
        "id", "object", "model", "status", 
        "progress", "created_at", "size", "seconds", "quality"
    ]
    
    # Original headers with "CurrentTime" (updated from 中文)
    original_headers = ["CurrentTime", "PromptSuggestion", "LineGeneration"]
    
    # Full expected headers: original + video-related (no duplicates)
    expected_headers = original_headers + [attr for attr in video_attributes if attr not in original_headers]
    
    # Extract values from Video object (handle missing attributes with "None")
    video_values = {attr: getattr(video, attr, "None") for attr in video_attributes}
    
    # Prepare full data (key: header name, value: data)
    full_data = {"CurrentTime": current_time}
    full_data.update(video_values)
    
    # Read existing data and update (if file exists)
    existing_data = []
    file_exists = os.path.exists(filename)
    row_updated = False  # Flag: whether matching row was found and updated
    
    if file_exists:
        try:
            with open(filename, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                existing_headers = reader.fieldnames or []
                
                # Add missing headers (video-related columns) to existing headers
                for new_header in expected_headers:
                    if new_header not in existing_headers:
                        existing_headers.append(new_header)
                
                # Iterate all rows to find time match (using "CurrentTime" field)
                for row in reader:
                    # Match row by "CurrentTime" (exact string match)
                    if row.get("CurrentTime") == current_time:
                        # Update row with Video data (preserve original columns' values)
                        row.update(video_values)
                        existing_data.append(row)
                        row_updated = True
                        print(f"✅ Found matching row (time: {current_time}), updated with Video data")
                    else:
                        # Preserve original rows (fill empty for new columns)
                        for new_header in expected_headers:
                            if new_header not in row:
                                row[new_header] = ""
                        existing_data.append(row)
        
        except Exception as e:
            print(f"⚠️ Warning: Failed to read existing file - {str(e)}. Will create new file instead.")
            file_exists = False
    
    # Add new row if no matching time found
    if not row_updated:
        # Fill empty values for original columns (since they're not provided for new rows)
        new_row = {header: full_data.get(header, "") for header in expected_headers}
        existing_data.append(new_row)
        print(f"❌ No matching row found. Added new row with time: {current_time}")
    
    # Write updated data back to CSV (safe overwrite with in-memory data)
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=expected_headers)
        writer.writeheader()
        writer.writerows(existing_data)
    
    print(f"✅ Successfully saved Video data to: {os.path.abspath(filename)}")
    print(f"📋 Current CSV columns: {expected_headers}")


if __name__ == "__main__":

    video = client.videos.retrieve("video_692eec5ce7c88193b1f157742754a50c08996df11182c341")

    save_video_to_csv(video)