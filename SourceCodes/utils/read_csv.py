import csv
import os
from typing import Union, List, Dict, Any

def read_csv_by_row_and_title(
    csv_path: str,
    rows: Union[int, List[int]],
    title: Union[str, List[str]]
) -> Union[Dict[str, Any], List[Dict[str, Any]], str]:
    """
    Read specific rows and columns (by header title) from a CSV file.
    Supports `-1` to represent the last data row for convenience.
    
    Args:
        csv_path: Relative or absolute path to the target CSV file
        rows: Specific row(s) to read (supports two formats)
              - 1-based index: e.g., 2 (reads row 2), [2, 4] (reads rows 2 and 4)
              - Special value: -1 (reads the last data row), [2, -1] (reads row 2 and last row)
        title: Specific column(s) to read (by exact header name)
              - Single column: e.g., "PromptSuggestion"
              - Multiple columns: e.g., ["CurrentTime", "LineGeneration"]
    
    Returns:
        Structured data (dict for single row, list of dicts for multiple rows)
        or error/warning message as string if operation fails
    """
    # Normalize input: convert single values to lists for uniform processing
    if isinstance(rows, int):
        rows = [rows]
    if not isinstance(rows, list) or not all(isinstance(r, int) for r in rows):
        return "Error: 'rows' must be an integer or list of integers"
    
    if isinstance(title, str):
        title = [title]
    if not isinstance(title, list) or not all(isinstance(t, str) for t in title):
        return "Error: 'title' must be a string or list of strings"
    
    # Check if file exists
    if not os.path.exists(csv_path):
        return f"Error: File not found - {csv_path}"
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            csv_headers = reader.fieldnames or []
            
            # Check for missing titles
            missing_titles = [t for t in title if t not in csv_headers]
            if missing_titles:
                return f"Error: Missing titles - {', '.join(missing_titles)}. Available: {', '.join(csv_headers)}"
            
            # Read all data rows (0-based list, excludes header)
            csv_data_rows = list(reader)
            total_data_rows = len(csv_data_rows)
            
            if total_data_rows == 0:
                return "Warning: CSV has no data rows (only header)"
            
            # Convert input rows to 0-based indices
            processed_indices = []
            for row_num in rows:
                if row_num == -1:
                    processed_indices.append(total_data_rows - 1)  # Last row
                elif row_num >= 2:
                    processed_indices.append(row_num - 2)  # 1-based → 0-based
                else:
                    processed_indices.append(None)  # Invalid row
            
            # Collect pure data values (exclude headers)
            results = []
            warnings = []
            for orig_row, idx in zip(rows, processed_indices):
                if idx is None:
                    warnings.append(f"Warning: Row {orig_row} invalid (data starts at row 2, use -1 for last row)")
                    continue
                
                if 0 <= idx < total_data_rows:
                    # Extract only values (no titles) for requested columns
                    row_values = [csv_data_rows[idx][col] for col in title]
                    # Simplify: if single title, store scalar instead of list
                    results.append(row_values[0] if len(title) == 1 else row_values)
                else:
                    warnings.append(f"Warning: Row {orig_row} does not exist (total data rows: {total_data_rows})")
            
            # Combine results and warnings (warnings first if any)
            final_output = []
            if warnings:
                final_output.extend(warnings)
            if results:
                # Simplify further: if single result, return directly instead of list
                if len(results) == 1 and not warnings:
                    final_output = results[0]
                else:
                    final_output.extend(results)
            
            return final_output if final_output else "Warning: No valid data found"
    
    except UnicodeDecodeError:
        return "Error: Encoding error - try using 'gbk' encoding in open()"
    except Exception as e:
        return f"Error: Unexpected issue - {str(e)}"
    


def read_csv_by_row(
    csv_path: str,
    target_row: int,
    title: Union[str, List[str]]

) -> Union[Dict[str, Any], List[Dict[str, Any]], str]:
    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            rows = list(csv_reader)
            
            if target_row < len(rows):
                result = rows[target_row][title]
                print(f"Reading row {target_row}, title '{title}': {result}")
                return result
            else:
                print(f"Error: No row {target_row} in CSV (file has only {len(rows)} rows including header)")
                return "Error"
    except Exception as e:
        return "Error"

# ------------------- Usage Examples -------------------
if __name__ == "__main__":
    # Example 1: Read single row + single title
    generated_lines_path = "ScriptsLists\generated_lines.csv"

    result1 = read_csv_by_row_and_title(generated_lines_path, rows=-1, title="LineGeneration")
    print(result1)
    