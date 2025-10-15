import os
from flask import Flask, jsonify, request
import pandas as pd
from dotenv import load_dotenv
import chardet  # for automatic encoding detection

# Load environment variables
load_dotenv()
app = Flask(__name__)

RESULTS_CSV = os.getenv('STUDENT_RESULTS_CSV', 'data/student_results.csv')


# --- Function to read student results CSV with encoding detection ---
def read_results_csv():
    if not os.path.exists(RESULTS_CSV):
        return []

    # Detect encoding automatically
    with open(RESULTS_CSV, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding'] or 'utf-8'

    # Read CSV with detected encoding and replace invalid characters
    df = pd.read_csv(RESULTS_CSV, encoding=encoding, errors='replace')

    # Clean column names
    df = df.rename(columns=lambda c: c.strip())

    # Strip string values to remove hidden whitespaces
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()

    return df.to_dict(orient='records')


# --- Flask endpoint to get student results ---
@app.route('/student-performance', methods=['GET'])
def student_performance():
    data = read_results_csv()

    # Optional filter: registration number
    reg = request.args.get('regno')
    if reg:
        data = [d for d in data if str(d.get('Reg.No', '')).strip() == reg.strip()]

    # Optional filter: subject
    subject = request.args.get('subject')
    if subject:
        subject = subject.strip()
        filtered = []
        for d in data:
            filtered.append({
                'Reg.No': d.get('Reg.No'),
                'Name': d.get('Name'),
                subject: d.get(subject, None),
                'GPA': d.get('GPA')
            })
        data = filtered

    return jsonify(data)


# --- Main entry point ---
if __name__ == '__main__':
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5001)),
        debug=True
    )
