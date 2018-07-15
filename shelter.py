import pandas as pd
import numpy as np
from ipysankeywidget import SankeyWidget

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def read_data():
    dataurl = 'https://data.bloomington.in.gov/dataset/94d3f457-57b5-45be-bee0-a0106f59b7ed/resource/8854ce02-e8f5-44b9-b85f-17f002a7d023/download/8854ce02-e8f5-44b9-b85f-17f002a7d023.csv'
    df = pd.read_csv(dataurl)
    return df


df = read_data ()
df['identichipnumber']=df['identichipnumber'].fillna('None')
df['unique_id'] = df[['sheltercode', 'identichipnumber']].apply(lambda x: ''.join(x), axis=1)
multiple_ids = df['unique_id'].value_counts().to_dict()
print('Before' ,df.shape[0])
for key in multiple_ids:
    if multiple_ids[key] > 1:
        multiple_entry = df[df.unique_id == key].sort_values('movementdate')
        intake_times = pd.to_datetime (multiple_entry['intakedate'] )

        # number of intakes before outcome_time
        number_intakes = len ( intake_times )

        df.set_value(df['unique_id'] == key,'number_of_intakes',number_intakes)
        # last intake.
        last_intake = intake_times.max ()
        last_row = multiple_entry.tail(1)

        count = 1
        for index, row in multiple_entry.head(number_intakes).iterrows ():
            df.set_value ( df['unique_id'] == key, 'intermediatemovement'+str(count), row.movementtype )
            df.set_value ( df['unique_id'] == key, 'intermediatemovementdate' + str ( count ), row.movementdate)
            count+=1

        '''
        'istrial', 'returndate', 'returnedreason',
       'deceaseddate', 'deceasedreason', 'diedoffshelter', 'puttosleep',
       'isdoa'
        '''

        if last_row.iloc[0].istrial:
            df.set_value ( df['unique_id'] == key, 'outcometype', 'istrail')

        elif not(pd.to_datetime(last_row.iloc[0].deceaseddate)!=np.nan):
            df.set_value ( df['unique_id'] == key, 'outcometype', last_row.iloc[0].deceasedreason)

        elif last_row.iloc[0].diedoffshelter==1:
            df.set_value ( df['unique_id'] == key, 'outcometype', 'died off shelter' )

        elif last_row.iloc[0].puttosleep == 1:
            df.set_value ( df['unique_id'] == key, 'outcometype', 'put to sleep' )

        elif last_row.iloc[0].isdoa == 1:
            df.set_value ( df['unique_id'] == key, 'outcometype', 'dead on arrival' )

        else:
            df.set_value ( df['unique_id'] == key, 'outcometype', last_row.iloc[0].returnedreason )


        # remove other lines
        df.drop(df[(df['unique_id'] == key) & \
               (pd.to_datetime(df[df['unique_id'] == key]['movementdate']) != last_row.iloc[0].movementdate)].index,inplace=True)

    else:
        entry = df[df.unique_id == key]
        df.set_value ( df['unique_id'] == key, 'number_of_intakes', 1 )
        df.set_value ( df['unique_id'] == key, 'intermediatemovement' + str ( 1 ), entry.iloc[0].movementtype)
        if entry.iloc[0].istrial:
            df.set_value ( df['unique_id'] == key, 'outcometype', 'istrail')

        elif not(pd.to_datetime(entry.iloc[0].deceaseddate)!=np.nan):
            df.set_value ( df['unique_id'] == key, 'outcometype', entry.iloc[0].deceasedreason)

        elif entry.iloc[0].diedoffshelter==1:
            df.set_value ( df['unique_id'] == key, 'outcometype', 'died off shelter' )

        elif entry.iloc[0].puttosleep == 1:
            df.set_value ( df['unique_id'] == key, 'outcometype', 'put to sleep' )

        elif entry.iloc[0].isdoa == 1:
            df.set_value ( df['unique_id'] == key, 'outcometype', 'dead on arrival' )

        else:
            df.set_value ( df['unique_id'] == key, 'outcometype', entry.iloc[0].returnedreason )


print('After',df.shape[0])
print(df.head())
exit()