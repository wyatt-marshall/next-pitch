# 4701
Final project for CS 4701 for Jacob Levy, Wyatt Marshall, and Jerry Wu


BEFORE STARTING, go to https://www.kaggle.com/josephvm/mlb-game-data?select=pitches.csv, and download the 'pitches.csv'
file, and then locally drag that file into the inner folder of this repo, once you have downloaded it onto your machine.
The file is greater than the file size limit that GitHub allows, but is crucial for this project to run. Without it, 
you will certainly experience errors, and be unable to run anything in the package.

To get data ready to by analyzed:

```import preprocessing```

#to analyze pitches on a fastball vs. offspeed basis for a pitcher with last name Darvish
```x, y = get_x_y_fastball_offspeed('Darvish')```

#to analyze pitches on a categorical basis for a pitcher with last name Darvish
```x, y = get_x_y_categorical('Darvish')```

y is the category in this case: 0 for non-moving fastball, 1 for moving fastball (sinker, cutter, two-seam), 2 for curves, 3 for changeup, 4 for slider, and 5 for knuckleballs or knuckle-curves
x and y will be the input and target vectors needed for ML analysis


Note: these functions above take about 30 seconds to run for a given pitcher

To run the UI:
In the command line, type ```python3 svm_ui.py```
Follow the instructions prompted in terminal!
