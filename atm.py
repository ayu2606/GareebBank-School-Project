# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import mysql.connector as sqltr
from mysql.connector.errors import IntegrityError
import os

con = sqltr.connect(host='localhost', user='root',password='tiger',database='gb')
cur = con.cursor()

if con.is_connected(): 
    cur.execute("""
                CREATE TABLE IF NOT EXISTS gb_user(
                    id integer NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    uname varchar(20) NOT NULL UNIQUE,
                    name varchar(20) NOT NULL,
                    password varchar(20) NOT NULL,
                    balance integer default 0,
                    account_type varchar(8)
                    )
                """)
    cur.execute("ALTER TABLE gb_user AUTO_INCREMENT = 1")
    con.commit()
    print('Database Connected succesfully\n')




def startup():
    os.system('cls')
    choice = input("1: Register\n2: Login\n> ")
    return choice.strip()


def register():
    uname = input('Username: ')
    name = input("name: ")
    password = input('pass: ')
    atype = input('atype: ')
    query = "INSERT INTO gb_user (uname,name,password,account_type) VALUES (%s, %s, %s, %s)"
    values = (uname,name,password,atype)
    try: 
        cur.execute(query,values)
        con.commit()
    except IntegrityError as e:
        if "Duplicate entry" in str(e):
            print('\nUsername already exists!\n')
            main()
    os.system('cls')
    main()
    
def login():
    uname = input('Enter your username: ')
    password = input('\nEnter your password: ')
    query = "SELECT id,balance FROM gb_user where uname= %s and password = %s"
    value = (uname,password)
    cur.execute(query,value)
    data = cur.fetchone()
    if not data:
        print('\nEither username or password is inncorrect. Please try again!\n')
        main()
    else:
        menu(data[0])

def menu(id):
    while True:
        op = operations(id)
        query = "SELECT balance FROM gb_user WHERE id = %s"
        val = (id,)
        cur.execute(query,val)
        d = cur.fetchone()
        bal = d[0]
        n = int(input(f"""\n
                  MENU: (Current Balnace: {bal})
            1 : Deposit
            2 : Withdraw
            3 : Check Bal
                  
                  \n>> """))
        if n == 1:
            nn = int(input('\nEnter Amount to deposist: '))
            os.system('cls')
            print(op.deposit(nn))
        if n == 2:
            nn = int(input('\nEnter amount to withdraw: '))
            os.system('cls')
            print(op.Withdraw(nn))
        if n == 3:
            os.system('cls')
            print(op.chk_bal())

class operations:
    def __init__(self, id):
        self.id = id
    def deposit(self,balance):
        query = """UPDATE gb_user SET balance = balance + %s WHERE id= %s"""
        val = (balance, self.id)
        cur.execute(query,val)
        con.commit()    

        return f"\n₹{balance} deposited successfully!"
        
    def Withdraw(self,balance):
        query = "SELECT balance FROM gb_user WHERE id = %s"
        val = (self.id,)
        cur.execute(query,val)
        d = cur.fetchone()
        if d[0] < balance:
            return f"Not enough Funds. You have {d[0]}."
        else:
            q = "UPDATE gb_user SET balance = balance - %s WHERE id = %s"
            v = (balance, self.id)
            cur.execute(q,v)
            con.commit()
            cur.execute(query,val)
            dt = cur.fetchone()
            return f'\nSucessfully withdraw {balance}. \nYour current balance is {dt[0]}'
            
    def chk_bal(self):
        query = "SELECT balance FROM gb_user WHERE id = %s"
        val = (self.id,)
        cur.execute(query,val)
        d = cur.fetchone()
        return f"\nCurrent Balance: {d[0]}"
    
def main():
    choice = startup()
    if choice == '1':    
        register()
    elif choice == '2':
        login()
main()