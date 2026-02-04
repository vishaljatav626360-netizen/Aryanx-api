from flask import Flask, request, jsonify
import pandas as pd
import os
import re

app = Flask(__name__)

# Ensure your file is named exactly aadhar.xlsx
FILE_NAME = 'aadhar(1).xlsx'

def load_data():
    if os.path.exists(FILE_NAME):
        try:
            # Load all columns as strings to prevent data corruption
            df = pd.read_excel(FILE_NAME, dtype=str, engine='openpyxl')
            # Clean data: Remove .0 and extra spaces
            for col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            return df
        except Exception:
            return None
    return None

df = load_data()

def clean_input_number(number):
    """Removes +91 or 91 prefix to get the base 10-digit number"""
    number = str(number).strip().replace('+', '')
    if len(number) > 10 and number.startswith('91'):
        return number[2:]
    return number

@app.route('/')
def api_search():
    # Adding branding to the JSON response
    branding = "@Simpleguy444"
    
    num_query = request.args.get('num', '').strip()
    name_query = request.args.get('name', '').strip()

    if not num_query and not name_query:
        return jsonify({
            "error": "Provide 'num' or 'name' parameter",
            "developer": branding
        }), 400

    if df is None:
        return jsonify({"error": "Database file not found", "developer": branding}), 500

    results = df.copy()

    # Search by Name
    if name_query:
        results = results[results['name'].str.contains(name_query, case=False, na=False)]
    
    # Search by Number (with auto-filter for +91/91)
    if num_query:
        target_num = clean_input_number(num_query)
        # We search the phoneNumber column for the 10-digit match
        results = results[results['phoneNumber'].str.contains(target_num, na=False)]

    if results.empty:
        return jsonify({"results": [], "count": 0, "developer": branding}), 404

    # Convert to list of dictionaries for Raw JSON output
    data_list = results.to_dict(orient="records")
    
    return jsonify({
        "status": "success",
        "developer": branding,
        "count": len(data_list),
        "data": data_list
    })

if __name__ == "__main__":
    app.run(debug=True)
    