import atexit
import psycopg2
from task import match_email_app
from celery import Celery
from celery.result import AsyncResult
from decouple import config
from flask_mail import Mail, Message
from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    func,
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker



app_name='server'
app = Flask(app_name)
app.config['UPLOAD_FOLDER'] = 'files'
celery=Celery(
    app_name,
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/2',
)
celery.conf.update(app.config)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask


bcrypt = Bcrypt(app)
engine = create_engine(config('ENGINE_CREATE'))
Base = declarative_base()
Session = sessionmaker(bind=engine)


atexit.register(lambda: engine.dispose())


app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
app.config['MAIL_SERVER'] = config('MAIL_SERVER')
app.config['MAIL_PORT'] = config('MAIL_PORT', cast=int)
app.config['MAIL_USE_TLS'] = config('MAIL_USE_TLS', cast=bool)
app.config['MAIL_USE_SSL'] = config('MAIL_USE_SSL', cast=bool)
app.config['MAIL_USERNAME'] = config('MAIL_USERNAME')  # введите свой адрес электронной почты здесь
app.config['MAIL_PASSWORD'] = config('MAIL_PASSWORD')  # введите пароль

mail=Mail(app)




class ADS(Base):
    __tablename__ = "ads_table"
    id = Column(Integer, primary_key=True)
    heading = Column(String(100), nullable=False, unique=True)
    description = Column(String(200), nullable=False)
    create_time = Column(DateTime, server_default=func.now())
    owner = Column(String(200), nullable=False)


Base.metadata.create_all(engine)


class ADSViews(MethodView):
    def get(self, id: int):
        with Session() as session:
            query_id = session.query(ADS).get(id)
            return jsonify({
                'heading': query_id.heading,
                'owner': query_id.owner,
                'create_time': query_id.create_time.isoformat()
            })

    def post(self):
        json_data = request.json
        with Session() as session:
            ads = ADS(heading=json_data['heading'], description=json_data['description'], owner=json_data['owner'])
            session.add(ads)
            session.commit()
            return jsonify({
                'heading': ads.heading,
                'owner': ads.owner,
                'create_time': ads.create_time.isoformat()
            })

    def patch(self, id: int):
        json_data = request.json
        with Session() as session:
            i = session.query(ADS).get(id)
            for x, y in json_data.items():
                if x == 'heading':
                    i.heading = y
                else:
                    i.description = y
                session.add(i)
                session.commit()


    def delete(self, id: int):
        with Session() as session:
            i = session.query(ADS).filter(ADS.id == id).one()
            session.delete(i)
            session.commit()





@celery.task()
def post_mail():
    result = match_email_app(app, mail)
    return result

class MailSend(MethodView):

    def post(self):
        task = post_mail().delay(15)
        print(task)
        return jsonify({
            "task_id": task.id
        })


    def get(self, task_id):
        task = AsyncResult(task_id, app=celery)
        return jsonify({'status': task.status,
                        'result': task.result})







app.add_url_rule('/ads/', view_func=ADSViews.as_view('create_ads'), methods=['POST'])
app.add_url_rule(
    "/ads/<int:id>/", view_func=ADSViews.as_view("get_ads"), methods=["GET"]
)
app.add_url_rule(
    "/ads/<int:id>/", view_func=ADSViews.as_view("patch_ads"), methods=["patch"]
)
app.add_url_rule(
    "/ads/<int:id>/", view_func=ADSViews.as_view("delete_ads"), methods=["DELETE"]
)
app.add_url_rule('/letter/', view_func=MailSend.as_view('Mail_send'), methods=['POST'])

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000
    )