import psycopg2
import celery
from flask import Flask
from flask_mail import Mail, Message
from decouple import config




def take_owner_db():
    temp =[]
    con = psycopg2.connect(config('SQLALCHEMY_DATABASE_URI'))
    cur = con.cursor()
    query="SELECT DISTINCT owner from ads_table"
    cur.execute(query)
    records=cur.fetchall()
    [temp.append((x[0])) for x in records]
    return temp


def match_email_app(app, mail):
    recipients = take_owner_db()
    msg = Message('Hello', sender=config('MAIL_USERNAME'), recipients=recipients)
    msg.body = "jl;kjsd;lfkjasd;"
    with app.app_context():
        mail.send(msg)
    return f'Letters send on the email addres: {recipients}'