import os
from flask import Flask, jsonify, request
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

RESULTS_CSV = os.getenv('STUDENT_RESULTS_CSV', 'data/student_results.csv')

# --- Student results endpoint ---
def read_results_csv():
    if not os.path.exists(RESULTS_CSV):
        return []
    df = pd.read_csv(RESULTS_CSV)
    df = df.rename(columns=lambda c: c.strip())  # remove extra spaces
    return df.to_dict(orient='records')

@app.route('/student-performance', methods=['GET'])
def student_performance():
    data = read_results_csv()
    
    # Optional filters
    reg = request.args.get('regno')
    if reg:
        data = [d for d in data if str(d.get('Reg.No','')).strip() == reg.strip()]
        
    subject = request.args.get('subject')
    if subject:
        subject = subject.strip()
        # Only return studentname, regno, and requested subject column
        filtered = []
        for d in data:
            filtered.append({
                'Reg.No': d['Reg.No'],
                'Name': d['Name'],
                subject: d.get(subject, None),
                'GPA': d['GPA']
            })
        data = filtered
        
    return jsonify(data)

if __name__ == '__main__':
    app.run(host=os.getenv('FLASK_HOST','0.0.0.0'),
            port=int(os.getenv('FLASK_PORT',5001)),
            debug=True)
