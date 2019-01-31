from flask import Flask,render_template,request,url_for,redirect,session,flash
from db import *
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
global temp
temp = False
conn = connectDB()
cursor = conn.cursor(dictionary=True)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' is session:
            return f(*args, **kwargs)
        else:
            return 'cannot access'
    return decorated_function


@app.route("/")
def menu():
    return render_template("search.html",flag=temp)


@app.route("/signup", methods = ['POST','GET'])
def signup():
    if request.method == 'POST':
        userdetails=request.form
        email = userdetails['email']
        name = userdetails['name']
        password = userdetails['password']
        confirmPassword = userdetails['confirmPassword']
        gender = userdetails['gender']
        car = userdetails['car']
        mobile = userdetails['mobile']
        govtid = userdetails['govtid']
        if password!=confirmPassword:
            return "not matched"
        pwd = sha256_crypt.encrypt(str(password))
        cursor.execute('insert into users values(null,%s,%s,%s,%s,%s,%s,%s)',(pwd,name,gender,mobile,email,car,govtid))
        conn.commit()
        return redirect(url_for('menu'))
    return render_template("signup.html",flag=temp)

@app.route("/login",methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        userdetails = request.form
        userid = userdetails['email']
        passwed = userdetails['password']
        cursor.execute('select * from users where email = %s', (userid,))
        res = cursor.fetchone()
        #print(res)
        if res is None:
            return ("invalid user name")
        else:
            pwd= res['pwd']
            if sha256_crypt.verify(passwed,pwd):
                session['logged_in']=True
                global temp
                temp= True
                #print("this is ",temp)
                session['userid']=int(res['userid'])
                #return 'You are now logged in','success'
                return redirect(url_for('menu'))
            else:
                return "invalid password"
    return render_template("login.html",flag=temp)


@app.route("/searchresult")
def searchresult():
    src = request.args.get('source')
    dest = request.args.get('destination')
    #cursor.execute('select * from pool')
    #res=cursor.fetchall()

    cursor.execute('select * from pool p,users u, dest d, src s where p.userid= u.userid and p.src=s.srcid and p.dest=d.destid and p.src=%s and p.dest=%s',(src,dest))
    res = cursor.fetchall()
    print(res)
    return render_template("searchresult.html",rows=res,l=len(res),flag=temp)


@app.route("/createpool",methods = ['POST','GET'])
def createpool():
    if request.method == 'POST':
        userdetails=request.form
        userid = session['userid']
        source = userdetails['source']
        destination = userdetails['destination']
        vacancy = userdetails['vacancy']
        time = userdetails['time']
        cost = userdetails['cost']
        print("this is ",time)
        cursor.execute('insert into pool values(%s,null,%s,%s,%s,%s,%s)',(userid,source,destination,vacancy,time,cost))
        conn.commit()
        return redirect(url_for('menu'))
    return render_template("createpool.html",flag=temp)

# requestpool
@app.route("/requestpool",methods = ['POST','GET'])
def requestpool():
    if request.method == 'GET':
        poolid = request.args.get('poolid')
        return render_template("requestpool.html", poolid=poolid)
    else:
        if not session['logged_in']:
            return redirect(url_for('menu'))
        userid = session['userid']
        status='Requested'
        userdetails = request.form
        src=userdetails['source']
        dest=userdetails['destination']
        poolid = userdetails['poolid']
        cursor.execute('insert into joinpool values(null,%s,%s,%s,%s,%s)',(userid, poolid, status, src, dest))
        conn.commit()
        return "Success"
        #return  redirect(url_for('menu'))


@app.route("/mypools",methods = ['POST','GET'])
def mypools():
    if request.method == 'GET':
        userid = session['userid']
        cursor.execute('select * from users u,joinpool j, pool p where j.userid=%s and p.poolid=j.poolid and j.userid= u.userid', (userid,))
        res = cursor.fetchall()
        #print(res, len(res))
        req=[]
        accreq=[]
        rejreq=[]
        for i in range(len(res)):
            if res[i]['status'] == 'Requested':
                req.append(res[i])
            elif res[i]['status'] == 'Accepted':
                accreq.append(res[i])
            else:
                rejreq.append(res[i])

        return render_template("poolrequest.html",req=req,accreq=accreq,flag=temp,rejreq=rejreq,l=len(req),l1=len(accreq),l2=len(rejreq))

@app.route("/logout")
def logout():
    global temp
    temp= False
    session.clear()
    return redirect(url_for('menu'))

if __name__ == '__main__':
    app.run(debug=True)