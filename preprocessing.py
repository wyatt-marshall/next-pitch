
import pandas as pd
import numpy as np



def create_usable_df(pitcher):
    df = pd.read_csv('pitches.csv', low_memory=False)
    df = df[df['Pitcher'] == pitcher]
    df = df.drop(['MPH'], axis=1)
    #Remove intentional balls, extraneous pitches, and non-entries
    df = df[~df.Type.str.contains("--")]
    df = df[~df.Type.str.contains("Intentional Ball")]
    df = df[~df.Type.str.contains("Pitch Out")]
    df = df[~df.Type.str.contains("Forkball")]
    df = df[~df.Type.str.contains("Screwball")]
    df = df[~df.Type.str.contains("Eephus Pitch")]
    df = df[~df.Type.str.contains("Unknown")]

    #Assign pitch types a catagory
    pitch_category = {0: ['Fastball', 'Four-seam FB'], 
                    1: ['Cutter', 'Splitter', 'Sinker', 'Two-seam FB'],
                    2: ['Slow Curve', 'Curve'], 3: ['Changeup'], 4: ['Slider'],
                    5: ['Knuckleball', 'Knuckle Curve'], }
    pitch_num = {}
    ind = 0
    for pitch in list(df['Type'].unique()):
        pitch_num[ind] = [pitch]
        ind += 1

    def pitch_to_num(d, pitch):
        for key in d:
            if pitch in d[key]:
                return key


    df['category'] = df.apply(lambda x: pitch_to_num(pitch_category, x.Type), axis=1)
    df['type'] = df.apply(lambda x: pitch_to_num(pitch_num, x.Type), axis=1)


    df['last_type'] = df.type.shift(1)
    df['last_category'] = df.category.shift(1)


    #Feature engineering for total pitch count for the game
    df['pitch_count'] = [0]*len(df)
    seen = {}
    for index, row in df.iterrows():
        if row.Game not in seen:
            seen[row.Game] = 0
        else:
            seen[row.Game] += 1
        df.at[index,'pitch_count'] = seen[row.Game]


    def event(pitch):
        if pitch == 'Ball':
            return 'Ball'
        if 'Strike' in pitch:
            return 'Strike'
        if 'Foul' in pitch:
            return 'Foul'
        else:
            return 'End'


    df['pitch_event'] = df.apply(lambda x: event(x.Pitch), axis=1)
    df['prev_pitch_event'] = df.pitch_event.shift(1)


    #Drop any set of rows where there is a missing pitch
    for index, row in df.iterrows():
        if row.Num == 1:
            df.at[index,'consistent'] = 1
        else:
            try:
                c = df.at[index-1,'consistent']
                df.at[index,'consistent'] = c
            except:
                df.at[index,'consistent'] = 0

    df = df[df.consistent != 0]


    for index, row in df.iterrows():
        if row.Num == 1:
            df.at[index,'balls'] = 0
            df.at[index, 'strikes'] = 0
        else:
            event = row.prev_pitch_event
            if event == 'Ball':
                df.at[index,'balls'] = df.at[index-1,'balls'] + 1
                df.at[index, 'strikes'] = df.at[index-1,'strikes']
            elif event == 'Strike':
                df.at[index,'balls'] = df.at[index-1,'balls']
                df.at[index, 'strikes'] = df.at[index-1,'strikes'] + 1
            elif event == 'Foul':
                df.at[index,'balls'] = df.at[index-1,'balls']
                df.at[index, 'strikes'] = min(df.at[index-1,'strikes'] + 1, 2)

    return df



def feature_eng(df):
    def event_categories(event):
        d = {"Ball": 0, "Strike": 1, "Foul": 2, "End": 3}
        if event not in d:
            return 0
        return d[event]
    #Assign events to numbers so it can be used in an SVM
    df["prev_event"] = df.apply(lambda row: event_categories(row.prev_pitch_event), axis=1)


    def inning_from_string(s):
        snd = s.split()[1]
        inning = int(snd[0])
        return inning

    df["inning"] = df.apply(lambda row: inning_from_string(row.Inning), axis=1)


    events = pd.read_csv('events.csv')


    pitcher_games = list(df['Game'].unique())


    events.columns


    pitcher_events = events[events['Game'].isin(pitcher_games)]


    def is_home(row):
        event_row = pitcher_events[(pitcher_events['Game'] == row.Game) & (pitcher_events['Event Id'] == 0)]
        home = list(event_row['Home'])[0]
        return int(home == row['Pitching Team'])
    df["home"] = df.apply(lambda row: is_home(row), axis=1)



    def score(row):
        """
        Returns the score as a tuple, with the first number being the score of the pitcher's team,
        and the second number of the opposing team
        """
        event, game, team, home = row['Event Id'], row['Game'], row['Pitching Team'], row['home']
        prev_event = int(event) - 1
        if prev_event <= 0:
            return 0, 0
        event_row = pitcher_events[(pitcher_events['Game'] == game) & (pitcher_events['Event Id'] == prev_event)]
        home_score = str(list(event_row['Home'])[0])
        away_score = str(list(event_row['Away'])[0])
        while len(home_score) != 1:
            if prev_event == 0:
                return 0, 0
            prev_event = prev_event - 1
            event_row = pitcher_events[(pitcher_events['Game'] == game) & (pitcher_events['Event Id'] == prev_event)]
            home_score = str(list(event_row['Home'])[0])
            away_score = str(list(event_row['Away'])[0])
        if home:
            return int(home_score), int(away_score)
        else:
            return int(away_score), int(home_score)



    df["pitcher_score"] = df.apply(lambda row: score(row)[0], axis=1)
    df['opposing_score'] = df.apply(lambda row: score(row)[1], axis=1)


    df = df[["Num", "last_category", "pitch_count", "prev_event", "prev_pitch_event", "balls", "strikes",
                "inning", "home", "pitcher_score", "opposing_score", "category"]]


    #drop first row and all nans
    df = df.iloc[1: , :]
    df = df.dropna()

    def event_categories(event):
        d = {"Ball": 0, "Strike": 1, "Foul": 2, "End": 3}
        return d[event]
    #Assign events to numbers so it can be used in an SVM
    df["prev_event"] = df.apply(lambda row: event_categories(row.prev_pitch_event), axis=1)


    df = df[["Num", "last_category", "pitch_count", "prev_event", "balls", "strikes",
                "inning", "home", "pitcher_score", "opposing_score", "category"]]

    return df





def get_x_y_fastballs_offspeed(pitcher):
    """
    Returns the input vectors and corresponding targets for a given pitcher.
    The target is 0 if it is a four-seam fastball, 
    1 for a moving (two-seam, cutter, sinker) fastball, and 2 otherwise
    """
    df = create_usable_df(pitcher)
    df = feature_eng(df)
    x = df.drop(['category'], axis=1)
    y = pd.DataFrame(df['category'])
    def is_fastball(category):
        if category == 0:
            return 0
        elif category == 1:
            return 1
        else:
            return 2
    y['offspeed'] = y.apply(lambda row: is_fastball(row.category), axis=1)   
    y = y.drop(['category'], axis=1)
    return x, y


def get_x_y_categorical(pitcher):
    """
    Returns the input vectors and corresponding targets for a given pitcher.
    The target is the category, 0 for non-moving fastball, 1 for moving 
    fastball (sinker, cutter, two-seam), 2 for curves, 3 for changeup,
    4 for slider, and 5 for knuckleballs or knuckle-curves
    """
    df = create_usable_df(pitcher)
    df = feature_eng(df)
    x = df.drop(['category'], axis=1)
    y = pd.DataFrame(df['category'])
    return x, y
