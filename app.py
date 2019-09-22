import os
import re
from sql import SQL
import smtplib
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
from flask_session import Session
from helpers import location
from helpers import naira, login_required
import datetime
from dateutil.relativedelta import relativedelta



app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///decapay.db")

# db.execute("CREATE TABLE  boys(first text, last text)")
# db.execute("CREATE TABLE  boys(first text, last text)")

# db.execute("CREATE TABLE loans (id, userId, loanType, loanAmount, interestRate, loanPeriod, monthlyRepayment, totalInterest,  totalCostOfLoan, status) ")

# db.execute("CREATE TABLE repayment (id, user_id, loan_id, due_date, begining_balance, monthly_payment, principal, interest,  ending_balance)")

        
# db.execute("CREATE TABLE users(id, first, last, username, phone, email, password, address,  state, city,  gender)")


server = smtplib.SMTP(host="smtp.gmail.com", port=587)
server.ehlo()
server.starttls()
server.login("decapays@gmail.com", "Decagon111")



# app.config['SESSION_TYPE'] = 'memcached'
app.secret_key = os.urandom(24)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response




@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template('login.html', message_error="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template('login.html', message_error="must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template('login.html', message_error="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        userDetails = db.execute(
            'SELECT * FROM users WHERE id = :userId', userId=session["user_id"])
        return render_template("profile.html", message="You have successfully logged in", userName=userDetails[0]["username"])

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    return render_template("login.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    q = request.args.get("q")
    rows = db.execute(
        "SELECT * FROM users WHERE username = :username", username=q)
    if (rows):
        return jsonify(message="True")
    return jsonify(message="False")


@app.route('/register', methods=["GET", "POST"])
def register():
    # render page on get request
    if request.method == 'GET':
        response = location()
        return render_template("register.html",  message_get=response)
    elif request.method == 'POST':
        response = location()
        details = []
        first = request.form.get('firstname')
        last = request.form.get('lastname')
        username = request.form.get('username')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        gender = request.form.get('gender')
        address = request.form.get('address')
        state = request.form.get('state')
        city = request.form.get('city')
        # check for existing username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        print(details)

        #check username
        if not username:
                return render_template('register.html',  message=[" ", "You must provide a username"], message_get=response, first=first, last=last,
                                       username=username, email=email, gender=gender)
            #check password
        elif not password:
                return render_template('register.html', message=[" ", "Password not provided"], message_get=response, first=first, last=last,
                                       username=username, email=email, gender=gender)
        elif not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
                return render_template('register.html', message=[" ", "Password must be atleast 8 characters long"], message_get=response, first=first, last=last,
                                    username=username, email=email, gender=gender)
        #check if passwords match
        elif password != confirmation:
                return render_template('register.html',  message=[" ", "Passwords do no match"], message_get=response,  first=first, last=last,
                                       username=username, email=email, gender=gender)

        #confirm username has not been taken
        elif (rows):
                return render_template('register.html', message=[" ", "Username has been taken"], message_get=response, first=first, last=last,
                                       username=username, email=email, gender=gender)
        #With all conditions met Insert user into database
        else:
            db.execute("INSERT INTO users(first, last, username, phone, email, password, address,  state, city,  gender) VALUES(:first, :last, :username, :phone, :email, :password, :address,  :state, :city,  :gender)",
                       first=first, last=last, username=username, phone=phone, email=email,  password=generate_password_hash(password), address=address,  state=state,  city=city, gender=gender)

            rows = db.execute("SELECT * FROM users WHERE username = :username",
                              username=username)

            server.sendmail("decapays@gmail.com", email,
                            "Congratulation your account has been verified")

            # session["user_id"] = username
            session["user_id"] = rows[0]["id"]
            session["user_name"] = username
            print(rows)

            # userDetails = db.execute('SELECT * FROM users WHERE id = :userId', userId= session["user_id"])
            return render_template("profile.html", message="You have successfully registered", userName=session["user_name"])


@app.route('/create', methods=["GET", "POST"])
@login_required
def create():
    def ableToGetLoan(loantype):
        if loantype == "Decamini":
            interestRate = 0.03
            return render_template("create.html", loantype=loantype, mini=100000, max=300000, interestRate=interestRate)
        elif loantype == "Decaflex":
            interestRate = 0.05
            return render_template("create.html", loantype=loantype, mini=310000, max=900000, interestRate=interestRate)
        elif loantype == "Decalarge":
            interestRate = 0.10
            return render_template("create.html", loantype=loantype, mini=910000, max=2000000, interestRate=interestRate)
        else:
            userDetails = db.execute(
                'SELECT * FROM users WHERE id = :userId', userId=session["user_id"])
            return render_template("profile.html", message="You have successfully registered", userName=userDetails[0]["username"])
    if request.method == "POST":
        loantype = request.form.get("loantype")
        amountborrowed = int(request.form.get("amountborrowed"))
        interestRate = float(request.form.get("interestrate"))
        period = int(request.form.get("period"))
        totalInterest = amountborrowed * interestRate
        totalCostOfLoan = amountborrowed + totalInterest
        monthlyPayment = totalCostOfLoan / period
        monthlyInterest = totalInterest / period
        monthlyPrincipal = monthlyPayment - monthlyInterest
        startdate = datetime.datetime.now()
        k = db.execute("INSERT INTO loans (userId, loanType,startdate, loanAmount, interestRate, loanPeriod, monthlyRepayment, totalInterest,  totalCostOfLoan, status) VALUES(:userId, :loanType, :startdate, :loanAmount, :interestRate, :loanPeriod, :monthlyRepayment, :totalInterest,  :totalCostOfLoan, :status)",
                       userId=session["user_id"], loanType=loantype, startdate=startdate, loanAmount=amountborrowed, interestRate=interestRate, loanPeriod=period, monthlyRepayment=monthlyPayment, totalInterest=totalInterest,  totalCostOfLoan=totalCostOfLoan, status=False)

        
        activeLoan = db.execute('SELECT * FROM loans WHERE userId = :userId and status = :status', userId= session["user_id"], status = False)
        # print(activeLoan)
        payment = float(activeLoan[0]["monthlyRepayment"])
        tbalance = activeLoan[0]["totalCostOfLoan"]
        date = (startdate + relativedelta(months=+1)).strftime("%x")
        period = activeLoan[0]["loanPeriod"]
        tInterest = float(activeLoan[0]["totalInterest"])
        rate = activeLoan[0]["interestRate"]
        loan_id = activeLoan[0]["id"]
        interest = tInterest / period
        principal = payment - interest
        principal = naira(principal)
        interest= naira(interest)
        for x in range(period):
            i = x + 1
            due_date = (startdate + relativedelta(months=+i)).strftime("%x")
            balance = tbalance - (x * payment)
            ending_balance = tbalance - ((x + 1) * payment) 
            ending_balance = naira(ending_balance)
            balance = naira(balance)

            k = db.execute("INSERT INTO repayment (user_id, loan_id, due_date, begining_balance, monthly_payment, principal, interest,  ending_balance,status) VALUES(:user_id, :loan_id, :due_date, :begining_balance, :monthly_payment, :principal, :interest,  :ending_balance, :status)",
            user_id= session["user_id"], loan_id = loan_id, due_date = due_date, begining_balance = balance, monthly_payment = payment, principal = principal, interest = interest,  ending_balance= ending_balance, status=False) 

        
        repayments_details= db.execute('SELECT * FROM repayment WHERE user_id = :userId and loan_id = :loan_id', userId= session["user_id"], loan_id = loan_id )
        # print(repayments_details)
        # return render_template("paymenthistory.html",activeLoan = activeLoan,payment = naira(payment), tbalance =naira(tbalance), principal = principal, interest= interest,repayments_details=repayments_details,totalInterest=naira(totalInterest), amountborrowed= naira(amountborrowed) )        
        return render_template("/success.html")
    elif request.method == "GET":
        userLoans = db.execute(
            'SELECT * FROM loans WHERE userId = :userId and status = :status', userId=session["user_id"], status = False)
        loantype = request.args.get("loantype")
        if len(userLoans) == 0:
            return ableToGetLoan(loantype)
        # status = userLoans[0]["status"]
        # print(status)
        # if status == "1":
        #     return ableToGetLoan(loantype)
        else:
            return render_template("noteligible.html", details="Please Pay up before making another application")


@app.route('/history', methods=['GET'])
@login_required
def history():
    if request.method == 'GET':
        activeLoan = db.execute('SELECT * FROM loans WHERE userId = :userId and status = :status', userId= session["user_id"], status = False)
        payment = float(activeLoan[0]["monthlyRepayment"])
        tbalance = activeLoan[0]["totalCostOfLoan"]
        totalInterest = activeLoan[0]["totalInterest"]
        tbalance = activeLoan[0]["totalCostOfLoan"]
        amountborrowed = activeLoan[0]["loanAmount"]
        loan_id = activeLoan[0]["id"]
    
        repayments_details= db.execute('SELECT * FROM repayment WHERE user_id = :userId and loan_id = :loan_id', userId= session["user_id"], loan_id = loan_id )
        

        return render_template("paymenthistory.html",activeLoan = activeLoan,payment = naira(payment), tbalance =naira(tbalance),repayments_details=repayments_details,totalInterest=naira(totalInterest), amountborrowed= naira(amountborrowed) )

        

@app.route('/duepayment', methods=["GET", "POST"])
@login_required
def duepayment():
    activeLoan = db.execute('SELECT * FROM loans WHERE userId = :userId and status = :status', userId= session["user_id"], status = False)
    loan_id = activeLoan[0]["id"]
    period = activeLoan[0]["loanPeriod"]
   
    repayments_details= db.execute('SELECT * FROM repayment WHERE user_id = :userId and loan_id = :loan_id', userId= session["user_id"], loan_id = loan_id )
    
    
    if request.method == "GET":    
        for x in range(period):
            status = repayments_details[x]["status"]
            if status == False:
                return render_template("duepayment.html",activeLoan = activeLoan, repayments_details=repayments_details, x=x)
    else:
        for x in range(period):
            status = repayments_details[x]["status"]
            if status == False:
                datepaid = request.form.get("datepaid")  
                paymentproof = request.form.get("paymentproof")  
                imageUrl = request.form.get("imageUrl") 
                if paymentproof == '':
                    return render_template("duepayment.html",activeLoan = activeLoan,repayments_details = repayments_details, message ='Please payment proof cannot be empty',x=x)
                if datepaid == '':
                    return render_template("duepayment.html",activeLoan = activeLoan, repayments_details = repayments_details, message ='Please date paid cannot be empty', x=x)
                if imageUrl == '':
                    return render_template("duepayment.html",activeLoan = activeLoan, repayments_details = repayments_details, message ='image url cannot be empty', x=x)
                else:
                    # should return a template of pending payment
                    return render_template("unconfirmed_payment.html")

    



    # startdate = datetime.datetime.now()
    # activeLoan = db.execute(
    #     'SELECT * FROM loans WHERE userId = :userId AND status = :status', userId=session["user_id"], status=False)
    # date = (startdate + relativedelta(months=+1)).strftime("%x")
    # period = activeLoan[0]["loanPeriod"]
    # tInterest = float(activeLoan[0]["totalInterest"])
    # payment = float(activeLoan[0]["monthlyRepayment"])
    # rate = activeLoan[0]["interestRate"]
    # loan_id = activeLoan[0]["id"]
    # tbalance = float(activeLoan[0]["totalCostOfLoan"])
    # interest = tInterest / period
    # principal = payment - interest

    # balances = []
    # dates = []
    # ending_balances = []
    # pmt = 3
    # for x in range(period):
    #     due_date = (startdate + relativedelta(months=+x)).strftime("%x")
    #     balance = tbalance - (x * payment)
    #     ending_balance = tbalance - ((x + 1) * payment)
    #     balance = naira(balance)
    #     ending_balances.append(ending_balance)
    #     balances.append(balance)
    #     dates.append(due_date)
    # if request.method == "GET":       
    #     return render_template("duepayment.html",activeLoan = activeLoan, dates = dates,balances = balances,period = period)
    # else:
    #     datepaid = request.form.get("datepaid")  
    #     print('joel')
    #     paymentproof = request.form.get("paymentproof")  
    #     imageUrl = request.form.get("imageUrl") 
    #     if paymentproof == '':
    #         return render_template("duepayment.html",activeLoan = activeLoan, dates = dates,balances = balances,period = period,message ='Please payment proof cannot be empty')
    #     if datepaid == '':
    #         return render_template("duepayment.html",activeLoan = activeLoan, dates = dates,balances = balances,period = period,message ='Please date paid cannot be empty')
    #     if imageUrl == '':
    #         return render_template("duepayment.html",activeLoan = activeLoan, dates = dates,balances = balances,period = period,message ='image url cannot be empty')
    #     else:
    #         db.execute("INSERT INTO repayment (user_id, loan_id, due_date, begining_balance, monthly_payment, principal, interest,  ending_balance, payment_proof, payment_mode,status,date_paid) VALUES(:user_id, :loan_id, :due_date, :begining_balance, :monthly_payment, :principal, :interest,  :ending_balance, :payment_proof, :payment_mode, :status, :date_paid)",
    #         user_id= session["user_id"], loan_id = loan_id, due_date = due_date, begining_balance = balance, monthly_payment = naira(payment), principal = naira(principal), interest = interest,  ending_balance= ending_balance, payment_proof = imageUrl, payment_mode=paymentproof, status=False, date_paid = datepaid) 
    #         userHistory = db.execute("SELECT * FROM repayment WHERE user_id = :user_id", user_id= session["user_id"])
    #         # print(userHistory)
    #         return render_template("paymenthistory.html", userHistory=userHistory, activeLoan = activeLoan,payment = naira(payment), tbalance =naira(tbalance), balances=balances,dates=dates, ending_balances=ending_balances, principal = naira(principal), pmt=period, interest= naira(interest))



@app.route('/success')
def success():
    return render_template("success.html")


@app.route('/profile')
@login_required
def profile():
    if session.get("user_id") is None:
        return render_template("notfound.html", details="Login Is Required")
    else:
        userDetails = db.execute(
            'SELECT * FROM users WHERE id = :userId', userId=session["user_id"])
        return render_template("profile.html", userName=userDetails[0]["username"])


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    flash('You have successfully logged out')
    # Redirect user to login form
    return redirect("/login")
