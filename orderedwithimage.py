from flask import Flask, render_template,request,jsonify
import pyodbc
import yagmail
import openai
import json
import random
import pyttsx3

app = Flask(__name__)
server = ''
database = 'test'
username = 'sa'
password = '22'
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

openai.api_key = "123"
chat_log = []

def generate_picture(prompt, n=1, size="512x512"):
    response = openai.Image.create(prompt=prompt, n=n, size=size)
    urls = [data['url'] for data in response['data']]
    return urls
@app.route("/")
def hello_world():
    return render_template('new.html')
verification_code=None
email=None
password=None
@app.route("/result",methods=['POST',"GET"])    
def register():
    global verification_code,email
    output = request.form.to_dict()
    # Get the user input from the registration form
    username = output['username']
    global email
    email = output['email']
    global password
    password = output['password']
    sender='dummbadzesabaa@gmail.com'
    reciver=email
    subject='registraciaaa'
    global verification_code # Use global keyword to access the global variable
    verification_code = random.randint(100000, 999999)
    
    content = f'Hello {username},\n\nYour verification code is: {verification_code}\n\nPlease enter this code on the verification page to complete your registration.'
    
    yag=yagmail.SMTP(user=sender,password='tsivrgxjuiqspvof')
    yag.send(to=reciver,subject=subject,contents=content)
    print('email.sent')
    return render_template("verify.html")
@app.route('/verify', methods=['POST'])
def verify():
    global verification_code # Use global keyword to access the global variable
    output = request.form.to_dict()
    code = int(output['code'])
    if code == verification_code:
        global email
        global password
        cursor = cnxn.cursor()
        cursor.execute("INSERT INTO users (username, email, password,verification_code) VALUES (?, ?, ?, ?)", (username, email, password,verification_code))
        cnxn.commit()
        return render_template('index.html')
    else:
        error_message = 'Invalid verification code. Please try again.'
        return render_template('verify.html', error=error_message)
@app.route("/test",methods=['POST',"GET"])    
def defs():
    if request.method=='POST':
        output = request.form.to_dict()
        
    # Get the user input from the registration form
    # username = output['username']
        email = output['email']
        password = output['password']
        print('i am here')
        print(email)
        print(password)
        cursor = cnxn.cursor()
        query = "SELECT * FROM users WHERE email=? AND password=?"
        values = (email, password)
        cursor.execute(query, values)
        user = cursor.fetchone()
        if user is not None:
            print('Access granted')
            return render_template("index.html")
        else:
            print('Access denied')
            return render_template("new.html")
    else:
        
        return render_template("new.html")
@app.route('/chat', methods=['POST'])
def chat():
    message = request.json['message']
    chat_log.append({"role": "user", "content": message})
    if message.startswith('generate picture'):
        urls = generate_picture(message, n=1, size="1024x1024")
        for url in urls:
            chat_log.append({"role": "bot", "content": f"<img src='{url}' alt='generated image'/>"})
        return jsonify({"response": urls})
    else: 
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        response = completion.choices[0].message
        voice=pyttsx3.init()
        
        chat_log.append({"content": response})
        # response_dict={"link":response}
        voice.say(response)
        voice.runAndWait()
        return jsonify({"response": str(response)})
        
#   response = completion.choices[0].message
#   print(completion.choices[0].message)
#   chat_log.append({"content": response})
#   return jsonify({"response": str(response)})
if __name__ == '__main__':
    app.run(debug=True)
