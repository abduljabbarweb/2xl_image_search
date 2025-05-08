import os
import shutil
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, redirect, url_for, render_template, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xls', 'xlsx'}

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to read SKUs from the uploaded Excel file
def read_skus_from_excel(file_path):
    df = pd.read_excel(file_path)
    if 'sku' in df.columns:
        return df['sku'].dropna().astype(str).tolist()
    else:
        raise ValueError("The Excel file does not contain a 'sku' column")

# Function to search and copy images
def search_and_copy_images(source_dir, dest_dir, skus):
    def copy_file(source_file, destination_file):
        shutil.copy2(source_file, destination_file)
        print(f"Copied: {source_file} to {destination_file}")

    def process_file(root, file):
        if any(sku in file for sku in skus):
            source_file = os.path.join(root, file)
            destination_file = os.path.join(dest_dir, file)
            copy_file(source_file, destination_file)

    with ThreadPoolExecutor() as executor:
        for root, _, files in os.walk(source_dir):
            for file in files:
                executor.submit(process_file, root, file)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Read SKUs from the uploaded Excel file
            try:
                skus = read_skus_from_excel(filepath)
            except ValueError as e:
                return str(e)

            # Source and destination directories
            source_directory = request.form['source_directory']
            destination_directory = request.form['destination_directory']

            # Create the destination directory if it doesn't exist
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)

            # Execute the function to search and copy images
            search_and_copy_images(source_directory, destination_directory, skus)

            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
