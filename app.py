import re
import pdfplumber
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
@app.route('/')
def upload_form():
    return render_template('upload.html')

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to extract director details using regex patterns
def extract_director_details(text):
    director_details = []
    director_pattern = r"(Mr\.|Mrs\.|Ms\.)\s+([A-Za-z]+)\s+([A-Za-z]+)"
    din_pattern = r"DIN:\s*(\d+)"
    independence_pattern = r"(?i)(Independent|Executive)"

    # Initialize a set to store processed director names
    processed_directors = set()

    # Find all matches for Director Name, DIN, and independence status
    director_matches = re.finditer(director_pattern, text)
    din_matches = re.finditer(din_pattern, text)
    independence_matches = re.finditer(independence_pattern, text)

    # Process each match and add director details to the list if not already processed
    for director_match, din_match, independence_match in zip(director_matches, din_matches, independence_matches):
        director_name = director_match.group(2) + " " + director_match.group(3)
        din_number = din_match.group(1)
        independence_status = "Independent" if independence_match else "Executive"
        
        # Check if the director has already been processed
        if director_name not in processed_directors:
            processed_directors.add(director_name)
            director_details.append({'director': director_name, 'din': din_number, 'independence': independence_status})

    return director_details



@app.route('/upload', methods=['POST'])
def upload_file():
    pdf_file = request.files['pdfFile']
    if pdf_file.filename.endswith('.pdf'):
        pdf_text = extract_text_from_pdf(pdf_file)
        directors = extract_director_details(pdf_text)
        if directors:
            return render_template('results.html', directors=directors)
        else:
            return jsonify({'error': 'No director details found.'}), 400
    else:
        return jsonify({'error': 'Invalid file format. Please upload a PDF file.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
