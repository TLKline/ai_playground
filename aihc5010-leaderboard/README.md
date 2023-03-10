# AIHC5010-leaderboard

## Installation

```commandline
$ conda create -n aihc5010-leaderboard python=3.9
$ conda activate aihc5010-leaderboard
$ pip install Flask Flask-SQLAlchemy pandas SQLAlchemy 
```


## Hosting
The leaderboard is hosted for free on pythonanywhere.com.

To manage the leaderboard login to pythonanywhere.com as the AIHC5010 user.

The source code is in the mysite/ directory. It doesn't look like there is a way
to integrate git on pythonanywhere.com so edits need to be manually copied across from here.


## Database management
Submissions are stored in the submissions.db sqlite3 database in the mysite/ directory.

The leaderboard can be accessed at https://aihc5010.pythonanywhere.com/leaderboard/.

To start a new leaderboard delete the current submissions.db on pythonanywhere.com. Then visit 
https://aihc5010.pythonanywhere.com/build-database/ this will create a new database and should display the message 
"Database created.". If a submissions.db file already exists the message "leaderboard table already exists." will be 
displayed. In the case of an error the error message will be displayed.

The database can't be easily accessed on pythonanywhere.com.  To make manual changes (e.g. deleting a submission) it's 
best to download a local copy and make changes to it. Then replace the hosted version with the updated 
version.


## Routes
The site has two routes that drive its function:

https://aihc5010.pythonanywhere.com/build-database/ : see **Database management** above. Also useful for testing the 
database connection.

https://aihc5010.pythonanywhere.com/submit-model/ : route for submitting results to the leaderboard. For an example see 
ML_Ed_AutoSeg_001_with_Submitter_05_june_v1.ipynb.

The site has a welcome route:

https://aihc5010.pythonanywhere.com/ : a welcome page that provides links to the leaderboard routes.

For each leaderboard there is are additional routes. Current routes are:

https://aihc5010.pythonanywhere.com/leaderboard-segmentation/ : the leaderboard page displaying leading results and hyperparameter 
frequency analysis for the segmentation notebook (ML_Ed_AutoSeg_001_with_Submitter_10_Jan_v1_TODO.ipynb).

https://aihc5010.pythonanywhere.com/leaderboard-classification/ : the leaderboard page displaying leading results and hyperparameter 
frequency analysis for the classification notebook (SIIM_Keras_Binary_Classifier_TODO.ipynb).

https://aihc5010.pythonanywhere.com/leaderboard-multimodal/ : the leaderboard page displaying leading results and hyperparameter 
frequency analysis for the multimodal notebook (Multimodality_lab_SIIM22_TODO.ipynb).

## Checklist for adding new leaderboards

1. Add the sub_model method to the new notebook and define a unique 'ModelKey'. This will identify the correct rows to display on the leaderboard. Follow this template:

```python
def sub_model(team, hyperparam):
  url='http://127.0.0.1:5005/submit-model/'
  hyperparam['team']=team
  hyperparam['ModelKey']='model_new' # TODO: edit to unique ModelKey
  x=requests.post(url,data=hyperparam)
  if x.status_code==200:
      print(f"Model Submitted Successfully for team {team}")
  else:
      print(x.status_code)
      print(x.text)
      print("Failed to Submit")
```

2. Make a copy of one of the models*.html files. Give it a unique name and edit the text and the image for the new task.

3. Edit main.py adding a new route and a method following this template:

```python
@app.route('/leaderboard-new/') # TODO: edit to unique route path
def models_new(): # TODO: edit to unique method name
    tasks = db.session.execute('SELECT * FROM leaderboard WHERE ModelKey=="new_model"') # TODO: edit to the 'ModelKey' chosen in step 1.
    df = pd.DataFrame(tasks, columns=['id', 'team', 'ModelKey', 'metric', 'LearningRate', 'BatchSize', 'Epochs',
                                      'ImageSize', 'BatchNorm', 'Filters', 'Dropout'])
    df['metric'] = pd.to_numeric(df.metric, errors='coerce')
    df1 = df.groupby('team').metric.agg(['count', 'max']).reset_index().sort_values('max', ascending=False)
    fields = df.columns[3:-4]
    context = {'model_name': 'T1 MRI sequences pre- or post-contrast',
               'Leader_Board': df1,
               'fields': fields.drop('metric'),
               'data': df}
    return render_template('models_new.html', **context) # TODO: edit to point to new template created in step 2
```

4. Add the link to the new leaderboard to welcome.html. For debugging the links hosted on gitlab are on localhost.

5. Test a submission locally. Run main.py. Run the notebook. Then visit the webpages on local host and check that the submission was successful and pages display as expected.

6. Login to pythonanywhere.com as the AIHC5010 user. Upload main.py, welcome.html and the template for the new leaderboard (e.g. models_new.html in the example above) to their equivalent locations in the mysite/ directory on pythonanywhere.com.

7. Edit the links to the leaderboards in the hosted version of welcome.html.

8. Make a copy of the notebook or edit it to replace localhost with the pythonanywhere.com url. For example:

```python
def sub_model(team, hyperparam):
  url='https://aihc5010.pythonanywhere.com/submit-model/'  # TODO: point to aihc5010.pythonanywhere.com
  hyperparam['team']=team
  hyperparam['ModelKey']='model_new'
  x=requests.post(url,data=hyperparam)
  if x.status_code==200:
      print(f"Model Submitted Successfully for team {team}")
  else:
      print(x.status_code)
      print(x.text)
      print("Failed to Submit")
```
9. navigate to https://www.pythonanywhere.com/user/AIHC5010/webapps/#tab_id_aihc5010_pythonanywhere_com and hit the 'Reload AIHC5010.pythonanywhere.com' button. Hit the 'Run until 3 months from today' button while you're at it.
   
10. Test a submission to the hosted leaderboard.

11. Remove any test submissions from the leaderboard so we have a clean version for the class. Download the hosted submissions.db and delete any entries that match the team of tester. For example, on the local copy just downloaded:

```commandline
$ sqlite3 submissions.db
SQLite version 3.40.0 2022-11-16 12:10:08
Enter ".help" for usage hints.
sqlite> .schema
CREATE TABLE leaderboard (id INTEGER PRIMARY KEY, team, ModelKey, metric, LearningRate, BatchSize, Epochs, ImageSize, BatchNorm, Filters, Dropout);
sqlite> SELECT count(*) FROM leaderboard WHERE team='tester';
1
sqlite> DELETE FROM leaderboard WHERE team='tester';
sqlite> SELECT count(*) FROM leaderboard WHERE team='tester';
0
```

12. Upload the local version of submissions.db to pythonanywhere.com.

13. Verify the hosted webpage for the leaderboard shows no submissions.