# -*- coding: utf-8 -*-
"""
Created on Sat Sep 20 19:22:19 2025
@author: Ayush
"""

# Import necessary modules
import mysql.connector as sql  # For MySQL database operations
import os                      # For system operations like clearing screen
import uuid                    # To generate unique passwords
from reportlab.lib.pagesizes import letter        # PDF page size for charts
from reportlab.platypus import SimpleDocTemplate  # To create PDF documents
from reportlab.graphics.shapes import Drawing     # To hold charts in PDF
from reportlab.graphics.charts.piecharts import Pie # To create pie charts
import pandas as pd            # To export SQL data to CSV
import warnings                # To suppress warnings

# Suppress pandas warning when using raw DB connections
warnings.simplefilter(action='ignore', category=UserWarning)

# --------------------- Database Connection ---------------------
# Connect to MySQL database
con = sql.connect(host='localhost', user='root', password='tiger', database='vote')
cur = con.cursor()

# --------------------- Tables Setup ----------------------------
if con.is_connected():
    # Create 'candidate' table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidate (
        c_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        c_name VARCHAR(50) NOT NULL,
        c_class VARCHAR(8) NOT NULL,
        c_pass VARCHAR(8) NOT NULL,
        votes_received INT DEFAULT 0
        );
    """)
    
    # Create 'voters' table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS voters (
        v_id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
        voter_id VARCHAR(8) NOT NULL,
        v_name VARCHAR(20) NOT NULL,
        v_class VARCHAR(8),
        voted BOOLEAN DEFAULT FALSE,
        voted_for INT,
        CONSTRAINT fk_candidate
            FOREIGN KEY (voted_for) REFERENCES candidate(c_id)
            ON DELETE SET NULL
        );
    """)
    
    # Reset AUTO_INCREMENT and set storage engine to InnoDB for foreign key support
    cur.execute("ALTER TABLE voters AUTO_INCREMENT = 1")
    cur.execute("ALTER TABLE candidate AUTO_INCREMENT = 1")
    cur.execute('ALTER TABLE voters ENGINE = InnoDB;')
    cur.execute('ALTER TABLE candidate ENGINE = InnoDB;')
    con.commit()
    print('Database Connected successfully\n')

# --------------------- Global Variables -----------------------
id = ''        # Stores the logged-in user ID
uname = ''     # Stores the logged-in username

# --------------------- Startup Menu ---------------------------
def startup():
    """
    Displays the initial startup menu for registration or login.
    """
    os.system('cls')  # Clear console
    os.system('title Voting Management By Team Ayush!')
    print("""
          **********************************************************
          **********************************************************
          WELCOME TO THE VOTING MACHINE!:
          
          1: Register as Candidate/Voter
          2: Login as a Candidate/Voter
          
          **********************************************************
          **********************************************************          
          """)
    n = int(input('\n>> '))
   
    os.system('cls')
    if n == 1:
        register()  # Call registration function
    elif n == 2:
        login()     # Call login function

# --------------------- Registration ---------------------------
def register():
    """
    Registers a new candidate or voter into the database.
    Generates a unique password using uuid.
    """
    vid = uuid.uuid4().hex[:8]  # Generate 8-character unique ID
    os.system('cls')
    nm = str(input('\n>> Name: '))
    cl = str(input('\n>> Class [Ex: XII B]: '))
    op = str(input('\n>> Are you a Voter or Candidate? '))
    
    if op.lower() == "candidate":
        q = "INSERT INTO candidate (c_name,c_class,c_pass) VALUES (%s, %s, %s)"
        v = (nm, cl, vid)
    else:
        q = "INSERT INTO voters (v_name,v_class,voter_id) VALUES (%s, %s, %s)"
        v = (nm, cl, vid)
    
    cur.execute(q, v)
    con.commit()
    
    # Display credentials to the user
    print(f"\n>> You have registered successfully!\nYour account login credentials are:\nusername: {nm}\nPassword: {vid}")
    login()  # Redirect to login

# --------------------- Login Function -------------------------
def login():
    """
    Logs in a user by checking username and password.
    """
    while True:
        usname = str(input('\n>> Enter your username: '))
        passwd = str(input('\n>> Enter your password: '))    
        os.system('cls')
        
        # Check if user exists in 'voters' table
        q = "SELECT v_id FROM voters WHERE v_name = %s AND voter_id = %s"
        v = (usname, passwd)
        cur.execute(q, v)
        data = cur.fetchone()
        
        if not data:
            print(">> ERROR: Either Username Or Password is incorrect!")
        else:
            global id, uname
            id = data[0]    # Save global user ID
            uname = usname  # Save global username
            menu(id, uname) # Go to menu

# --------------------- Main Menu -----------------------------
def menu(id, uname):
    """
    Displays the main menu after login.
    """
    os.system('cls')
    print(f"""
          WELCOME {uname}! 
          
          1: Vote a candidate
          2: Candidate List
          3: Results
          4: Export Voter list
          9: Exit
          """)
    
    while True:
        ch = int(input('\n>> '))
        if ch == 1:
            # Check if user has already voted
            cur.execute("SELECT voted FROM voters WHERE v_id = %s", (id,))
            r = cur.fetchone()
            if r[0]:
                input('You have already voted!.\nPress Enter to return to the menu')
                menu(id, uname)
            elif r[0] == 0:
                vote()
        elif ch == 2:
            cad_list()
        elif ch == 3:
            result()
        elif ch == 4:
            create_csv()
        else:
            print('Invalid Choice!....')

# --------------------- Voting Function -----------------------
def vote():
    """
    Allows a voter to vote for a candidate.
    """
    cur.execute("SELECT c_id, c_name, c_class FROM candidate")
    print("SELECT A CANDIDATE: ")
    print(f"{'ID':<4} {'Name':<15} {'Class':<10}")
    print("-" * 40)
    
    # Display candidates
    for i in cur.fetchall():
        print(f'{i[0]:<4} {i[1]:<15} {i[2]:<10}')
    
    ch = int(input("\n>> "))
    
    # Update votes and mark voter as voted
    cur.execute("UPDATE candidate SET votes_received = votes_received + 1 WHERE c_id = %s", (ch,))
    cur.execute('UPDATE voters SET voted_for = %s, voted = 1 WHERE v_id = %s', (ch, id))
    con.commit()
    
    menu(id, uname)

# --------------------- Candidate List ------------------------
def cad_list():
    """
    Displays the list of candidates.
    """
    print(f"{'ID':<4} {'Name':<15} {'Class':<10}")
    print("-" * 40)
    cur.execute('SELECT c_id, c_name, c_class FROM candidate')
    for c_id, c_name, c_class in cur.fetchall():
        print(f"{c_id:<4} {c_name:<15} {c_class:<10}")
    
    input("\nPress Enter to return back to menu!")
    menu(id, uname)    

# --------------------- Results -------------------------------
def result():
    """
    Displays voting results and optionally generates a pie chart.
    """
    name = []
    vote_count = []
    
    print(f"{'ID':<4} {'Name':<15} {'Class':<10} {'Votes':<6}")
    print("-" * 40)
    
    cur.execute('SELECT c_id, c_name, c_class, votes_received FROM candidate ORDER BY votes_received DESC')
    for c_id, c_name, c_class, votes in cur.fetchall():
        print(f"{c_id:<4} {c_name:<15} {c_class:<10} {votes:<6}")
        name.append(c_name)
        vote_count.append(votes)
    
    while True:
        ch = input("\nDo you want Pie chart of the result? (Yes/No): ")
        if ch.lower() == 'yes':
            create_pie(name, vote_count)
        elif ch.lower() == 'no':    
            menu(id, uname)
        else:
            print('\nInvalid input....')

# --------------------- Create Pie Chart -----------------------
def create_pie(c_name, votes):
    """
    Generates a pie chart PDF for voting results.
    """
    pdf = SimpleDocTemplate('Result_pie_chart.pdf', pagesize=letter)
    drawing = Drawing(400, 200)
    
    pie = Pie()
    pie.x = 150
    pie.y = 50
    pie.width = 150
    pie.height = 150
    pie.data = votes
    pie.labels = c_name  # Correct attribute
    
    drawing.add(pie)
    
    pdf.build([drawing])
    pdf_path = os.path.abspath('./Result_pie_chart.pdf')
    print(f'\nPDF is available at {pdf_path}')
    input('\nPress Enter for menu....')
    menu(id, uname)

# --------------------- Export Voter List ---------------------
def create_csv():
    """
    Exports the voter list to a CSV file using Pandas.
    """
    query = 'SELECT v_id, v_name, v_class FROM voters'
    df = pd.read_sql(query, con)  # Read SQL table into DataFrame
    df.to_csv("voter_list.csv", index=False)  # Export to CSV
    print('\nExported CSV Report as voter_list.csv')
    input('\nPress Enter to return to Menu.....')

# --------------------- Start Program -------------------------
startup()
