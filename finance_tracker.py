# Import necessary modules

import http.server  # For handling HTTP requests
import socketserver  # For creating a basic TCP server
import urllib.parse  # For parsing URL parameters
import csv  # For reading and writing CSV files
from datetime import datetime  # For working with date and time
from collections import defaultdict  # For creating default dictionary for summaries
import os  # For checking file existence



# Set server port
PORT = 8000



# File paths
CSV_FILE = "sample_finance_data_2024.csv"  # CSV file to store finance entries
STYLE_FILE = "style.css"  # CSS file for styling the web pages




# Create external CSS file if it doesn't exist

if not os.path.exists(STYLE_FILE):
    with open(STYLE_FILE, 'w') as f:
        f.write("""
        /* CSS styles for the finance tracker UI */
        body {
            font-family: 'Segoe UI', sans-serif;
            margin: 20px;
            background: linear-gradient(to right, #f5f7fa, #c3cfe2);
            color: #333;
        }
        h1, h2 {
            color: #2c3e50;
            text-align: center;
        }
        a {
            text-decoration: none;
            color: #0077cc;
            font-weight: bold;
        }
        a:hover {
            color: #005fa3;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
        }
        th {
            background: linear-gradient(to right, #6a11cb, #2575fc);
            color: white;
            padding: 10px;
        }
        td {
            padding: 10px;
            text-align: center;
            background: #fff;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        form {
            background: #ffffff;
            padding: 20px;
            border-radius: 10px;
            width: 400px;
            margin: auto;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        input, select {
            padding: 8px;
            width: 100%;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        input[type="submit"] {
            background: linear-gradient(to right, #00b4db, #0083b0);
            color: white;
            cursor: pointer;
            border: none;
        }
        input[type="submit"]:hover {
            background: linear-gradient(to right, #0083b0, #00b4db);
        }
        """)




# Define the request handler for HTTP requests
class FinanceRequestHandler(http.server.SimpleHTTPRequestHandler):


    # Handle GET requests
    
    def do_GET(self):
        if self.path == "/style.css":
            
            
            # Serve the CSS file
            
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open(STYLE_FILE, 'r') as file:
                self.wfile.write(file.read().encode())
        elif self.path.startswith("/edit"):
            self.show_edit_form()  # Show edit form
        elif self.path.startswith("/add"):
            self.show_add_form()  # Show add entry form
        elif self.path.startswith("/summary"):
            self.show_summary()  # Show summary page
        else:
            self.show_home()  # Default: show homepage


    # Handle POST requests
    
    def do_POST(self):
        length = int(self.headers['Content-Length'])  # Read content length
        post_data = self.rfile.read(length)  # Read form data
        fields = urllib.parse.parse_qs(post_data.decode('utf-8'))  # Parse form data


        if self.path.startswith("/submit"):
            
            
            # Append new entry to CSV
            
            new_entry = {
                'Date': fields['date'][0],
                'Type': fields['type'][0],
                'Category': fields['category'][0],
                'Amount': fields['amount'][0],
                'Description': fields['description'][0]
            }
            
            with open(CSV_FILE, mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=new_entry.keys())
                writer.writerow(new_entry)


        elif self.path.startswith("/update"):
            
            
            # Update existing entry
            
            index = int(fields['index'][0])
            with open(CSV_FILE, 'r') as file:
                rows = list(csv.DictReader(file))
            rows[index] = {
                'Date': fields['date'][0],
                'Type': fields['type'][0],
                'Category': fields['category'][0],
                'Amount': fields['amount'][0],
                'Description': fields['description'][0]
            }
            
            with open(CSV_FILE, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)


        # Redirect back to homepage after POST
        
        self.send_response(303)
        self.send_header('Location', '/')
        self.end_headers()



    # Display home page with all records
    
    def show_home(self):
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            rows = list(reader)


        html = f"""
        <html><head><meta charset='UTF-8'>
        <title>Finance Tracker</title>
        <link rel='stylesheet' type='text/css' href='/style.css'>
        <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'>
        </head><body>
        <h1><i class='fas fa-book'></i> Personal Finance Tracker</h1>
        <a href='/add'><i class='fas fa-plus'></i> Add Entry</a> |
        <a href='/summary'><i class='fas fa-chart-bar'></i> View Summary</a><br><br>
        <table border='1'><tr><th>Date</th><th>Type</th><th>Category</th><th>Amount</th><th>Description</th><th>Actions</th></tr>
        """
        
        for idx, row in enumerate(rows):
            html += f"<tr><td>{row['Date']}</td><td>{row['Type']}</td><td>{row['Category']}</td><td>₹{row['Amount']}</td><td>{row['Description']}</td><td><a href='/edit?index={idx}'>✏️ Edit</a></td></tr>"
        html += "</table></body></html>"
        self.respond(html)



    # Show form to add a new entry
    
    def show_add_form(self):
        html = """
        <html><head><meta charset='UTF-8'><title>Add Entry</title>
        <link rel='stylesheet' type='text/css' href='/style.css'>
        <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'>
        </head><body>
        <h2><i class='fas fa-plus'></i> Add New Entry</h2>
        <form method='POST' action='/submit'>
            Date (DD-MM-YYYY): <input type='text' name='date'><br>
            Type: <select name='type'>
                <option value='Income'>Income</option>
                <option value='Expense'>Expense</option>
            </select><br>
            Category: <input type='text' name='category'><br>
            Amount: <input type='text' name='amount'><br>
            Description: <input type='text' name='description'><br>
            <input type='submit' value='Add Entry'>
        </form>
        <br><a href='/'><i class='fas fa-arrow-left'></i> Back to Home</a></body></html>
        """
        
        self.respond(html)
        
        

    # Show form to edit an existing entry
    
    def show_edit_form(self):
        query = urllib.parse.urlparse(self.path).query
        index = int(urllib.parse.parse_qs(query)['index'][0])
        with open(CSV_FILE, 'r') as file:
            rows = list(csv.DictReader(file))
        row = rows[index]

        html = f"""
        <html><head><meta charset='UTF-8'><title>Edit Entry</title>
        <link rel='stylesheet' type='text/css' href='/style.css'>
        <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'>
        </head><body>
        <h2><i class='fas fa-pen'></i> Edit Entry</h2>
        <form method='POST' action='/update'>
            <input type='hidden' name='index' value='{index}'>
            Date: <input type='text' name='date' value='{row['Date']}'><br>
            Type: <select name='type'>
                <option value='Income' {'selected' if row['Type'] == 'Income' else ''}>Income</option>
                <option value='Expense' {'selected' if row['Type'] == 'Expense' else ''}>Expense</option>
            </select><br>
            Category: <input type='text' name='category' value='{row['Category']}'><br>
            Amount: <input type='text' name='amount' value='{row['Amount']}'><br>
            Description: <input type='text' name='description' value='{row['Description']}'><br>
            <input type='submit' value='Update Entry'>
        </form>
        <br><a href='/'><i class='fas fa-arrow-left'></i> Back to Home</a></body></html>
        """
        self.respond(html)



    # Show summary reports (by category and by month)
    
    def show_summary(self):
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            data = list(reader)

        by_category = defaultdict(int)
        by_month = defaultdict(int)


        for row in data:
            if row['Type'].lower() == 'expense':
                by_category[row['Category']] += int(row['Amount'])
                month = datetime.strptime(row['Date'], "%d-%m-%Y").strftime("%B")
                by_month[month] += int(row['Amount'])

        html = """
        <html><head><meta charset='UTF-8'><title>Summary</title>
        <link rel='stylesheet' type='text/css' href='/style.css'>
        <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'>
        </head><body>
        <h2><i class='fas fa-chart-pie'></i> Summary by Category</h2><ul>
        """
       
        for cat, amt in by_category.items():
            html += f"<li>{cat}: ₹{amt}</li>"
        html += "</ul><h2><i class='fas fa-calendar-alt'></i> Summary by Month</h2><ul>"
        
        for month, amt in by_month.items():
            html += f"<li>{month}: ₹{amt}</li>"
        html += "</ul><br><a href='/'><i class='fas fa-arrow-left'></i> Back to Home</a></body></html>"

        self.respond(html)



    # Common method to respond with HTML
    
    def respond(self, html):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))





# Start the server and listen on the specified port

with socketserver.TCPServer(("", PORT), FinanceRequestHandler) as httpd:
    print(f"🚀 Serving on http://localhost:{PORT}")
    httpd.serve_forever()
