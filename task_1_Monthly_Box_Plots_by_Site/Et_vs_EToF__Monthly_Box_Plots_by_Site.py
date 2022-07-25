# Task 1
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# Bug notice: Some of the data recieved, had the leading '0' truncated off the front.
# For example '09180000' --> '9180000'
# If there are any errors with reading in the raw data, please check the site numbers.
site_list = ['09180000',        # DOLORES RIVER NEAR CISCO, UT,
             '09209400',        # GREEN RIVER NEAR LA BARGE, WY,
             '09260000',        # LITTLE SNAKE RIVER NEAR LILY, CO
             '09302000',        # DUCHESNE RIVER NEAR RANDLETT, UT,
             '09306500',        # WHITE RIVER NEAR WATSON, UTAH
             '09379500',        # SAN JUAN RIVER NEAR BLUFF, UT
             ]

# Dictionary used to transfer between strings and ints.
month_dict = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sept',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec'
}

# Read in the metadata so that the site names can be attached to the graph.
try:
    df_metadata = pd.read_csv('raw_data/metadata.csv')
except:
    print("ERROR WITH READING METADATA")
    exit(1)

fig, axes = plt.subplots(6, 2, figsize=(20, 60))
fig.subplots_adjust(top=.95)
fig.subplots_adjust(bottom=0.02)
fig.suptitle(fontsize=50, t='Et vs. EToF - Monthly Box Plots by Site ')

for i, site in enumerate(site_list):

    # Reads the data in for the given site
    try:
        df_et = pd.read_csv('raw_data/ucrb_riparain_et/'+ site +'_EEMETRIC_monthly_et_etof.csv')
    except:
        print("ERROR WHEN READING DATA FROM SITE: " + site)
        exit(1)

    # Changes the end date column to 'month' through string manipulation
    df_et['END_DATE'] = df_et['END_DATE'].apply(lambda x: int(x[5:7]))
    df_et.rename({'END_DATE': "Month"}, axis=1, inplace=True)

    # Here the month column is changed from int to string.
    # Example: 1 --> 'jan'
    df_et['Month'] = df_et['Month'].apply(lambda x: month_dict[x])

    site_name = df_metadata.loc[df_metadata['station_id'] == int(site), 'site_name'].iloc[0]
    sns.boxplot(ax=axes[i,0], data=df_et, x=df_et["Month"], y=df_et["ET_MEAN"])\
        .set(title= 'ET at ' + site_name +' - '+ site)
    sns.boxplot(ax=axes[i,1], data=df_et, x=df_et["Month"], y=df_et["EToF_MEAN"])\
        .set(title= 'EToF at ' + site_name +' - '+ site)

plt.savefig('Et_vs_EToF__Monthly_Box_Plots_by_Site.png')

