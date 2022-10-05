import numpy as np
import pandas as pd
import random
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from preprocessing import *
from sklearn.svm import SVC

pitcher = input('Type the last name of the pitcher you are facing today: ')
print('training the model, this could take a minute or two...')
x, y = get_x_y_fastballs_offspeed(pitcher)
y = y.values.ravel()
clf = make_pipeline(StandardScaler(), SVC(gamma='auto', kernel ='rbf'))
clf.fit(x.values, y)
home = input('Are you home or away today? Type H or A ')
while home != 'H' and home != 'A':
  home = input('Are you home or away today? Type H or A ')
if home == 'A':
  home = 1
else:
  home = 0
done = False
num = 1
ct = 0
last = 0
prev_event = 3
last_category = 0
balls, strikes = 0, 0
tot, corr = 0, 0
d = {"B": 0, "S": 1, "F": 2, "E": 3}
while not done:
  ct += 1
  if prev_event == 3:
    num = 1
  else:
    num += 1

  bat_score, pitch_score = None, None
  while type(bat_score) != int or type(pitch_score) != int:
    try:
      bat_score = int(input('How many runs does your team have? '))
      pitch_score = int(input('How many runs does the opposing team have? '))
    except:
      print('type in a number only')

  inning = None
  while type(inning) != int:
    try:
      inning = int(input('What inning is it? Type it as a number '))
    except:
      print('type in a number only')

  to_pred = [num, last_category, ct, prev_event, balls, strikes,
       inning, home, pitch_score, bat_score]
  pred = clf.predict([to_pred])[0]
  if pred == 0:
    pred_str = 'Four-seam fastball'
  elif pred == 1:
    pred_str = 'Moving fastball'
  else:
    pred_str = 'Offspeed'
  print('Predicting ' + str(pred_str))
  tot += 1

  last_category = input('Type 0 if the pitch was a four-seam fastball, 1 if it was a moving fastball, and 2 if it was offspeed ')
  while last_category != '0' and last_category != '1' and last_category != '2':
    last_category = input('Type 0 if the pitch was a four-seam fastball, 1 if it was a moving fastball, and 2 if it was offspeed ')
  last_category = int(last_category)
  if last_category == pred:
    corr += 1

  
  prev_event = input('Was the result of the pitch a foul, a strike (non-foul), ball, or end of at-bat? Type F, S, B, or E ')
  while prev_event != 'F' and prev_event != 'B' and prev_event != 'S' and prev_event != 'E':
    prev_event = input('Was the result of the pitch a foul, a strike (non-foul), ball, or end of at-bat? Type F, S, B, or E ')
  prev_event = d[prev_event]
  if prev_event == 0:
    balls += 1
  elif prev_event == 1:
    strikes += 1
  elif prev_event == 2:
    strikes = min(strikes+1, 2)
  else:
    strikes, balls = 0, 0

  print('Current score: ' + str(corr) + " out of " + str(tot) + " for a score of " + str(corr/tot) + ".")

  leave = input('Do you want to keep predicting for ' + pitcher  + '? Type Y or N ')
  while leave != 'Y' and leave != 'N':
    leave = input('Do you want to keep predicting for ' + pitcher  + '? Type Y or N ')
  if leave == 'N':
    done = True