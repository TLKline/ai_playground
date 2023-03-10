import pandas as pd

from flask import Flask, request, jsonify, render_template
# from sqlalchemy.sql import text
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError


app = Flask(__name__)

# https://python-adv-web-apps.readthedocs.io/en/latest/flask_db1.html
db_name = 'submissions.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


@app.route('/')
def welcome():
    return render_template('welcome.html')


@app.route('/build-database/')
def build_database():
    try:
        db.session.execute('CREATE TABLE leaderboard (id INTEGER PRIMARY KEY, team, ModelKey, metric, LearningRate, BatchSize, Epochs, ImageSize, BatchNorm, Filters, Dropout)')
    except OperationalError as e:
        db.session.execute('SELECT 1 FROM leaderboard')
        return '<h1>leaderboard table already exists.</h1>'
    except Exception as e:
        # e holds description of the error
        error_text = '<p>The error:<br>' + str(e) + '</p>'
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text
    return '<h1>Database created.</h1>'


@app.route('/submit-model/', methods=['POST'])
def submit_model():
    if request.method == 'POST':
        model = request.form.to_dict()
        try:
            model['BatchNorm']
        except KeyError:
            model['BatchNorm'] = False
        try:
            model['Filters']
        except KeyError:
            model['Filters'] = None
        try:
            model['Dropout']
        except KeyError:
            model['Dropout'] = None
        insert = 'INSERT OR REPLACE INTO leaderboard (team, ModelKey, metric, LearningRate, BatchSize, Epochs, ImageSize, BatchNorm, Filters, Dropout) VALUES (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')'
        values = (model['team'], model['ModelKey'], model['metric'], model['LearningRate'], model['BatchSize'],
                  model['Epochs'], model['ImageSize'], model['BatchNorm'], model['Filters'], model['Dropout'])
        db.session.execute(insert % values)
        db.session.commit()
    return jsonify({'Message': 'Model Submitted'}), 200


@app.route('/leaderboard-segmentation/')
def models():
    tasks = db.session.execute('SELECT * FROM leaderboard WHERE ModelKey=="SIIM_AutoSeg_001"')
    df = pd.DataFrame(tasks, columns=['id', 'team', 'ModelKey', 'metric', 'LearningRate', 'BatchSize', 'Epochs',
                                      'ImageSize', 'BatchNorm', 'Filters', 'Dropout'])
    df['metric'] = pd.to_numeric(df.metric, errors='coerce')
    df1 = df.groupby('team').metric.agg(['count', 'max']).reset_index().sort_values('max', ascending=False)
    fields = df.columns[4:]
    context = {'model_name': 'Segmenting kidneys in MR Images',
               'Leader_Board': df1,
               'fields': fields,
               'data': df}
    return render_template('leaderboard-segmentation.html', **context)


@app.route('/leaderboard-classification/')
def models2():
    tasks = db.session.execute('SELECT * FROM leaderboard WHERE ModelKey=="lab2"')
    df = pd.DataFrame(tasks, columns=['id', 'team', 'ModelKey', 'metric', 'LearningRate', 'BatchSize', 'Epochs',
                                      'ImageSize', 'BatchNorm', 'Filters', 'Dropout'])
    df['metric'] = pd.to_numeric(df.metric, errors='coerce')
    df1 = df.groupby('team').metric.agg(['count', 'max']).reset_index().sort_values('max', ascending=False)
    fields = df.columns[4:]
    context = {'model_name': 'T1 MRI sequences pre- or post-contrast',
               'Leader_Board': df1,
               'fields': fields,
               'data': df}
    return render_template('leaderboard-classification.html', **context)


@app.route('/leaderboard-multimodal/')
def models3():
    tasks = db.session.execute('SELECT id, team, ModelKey, metric, LearningRate, BatchSize, Epochs, ImageSize FROM leaderboard WHERE ModelKey=="lab3"')
    df = pd.DataFrame(tasks, columns=['id', 'team', 'ModelKey', 'metric', 'LearningRate', 'BatchSize', 'Epochs', 'ImageSize'])
    df['metric'] = pd.to_numeric(df.metric, errors='coerce')
    df1 = df.groupby('team').metric.agg(['count', 'max']).reset_index().sort_values('max', ascending=False)
    fields = df.columns[4:]
    context = {'model_name': 'Multimodal Learning',
               'Leader_Board': df1,
               'fields': fields,
               'data': df}
    return render_template('leaderboard-multimodal.html', **context)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5005)
