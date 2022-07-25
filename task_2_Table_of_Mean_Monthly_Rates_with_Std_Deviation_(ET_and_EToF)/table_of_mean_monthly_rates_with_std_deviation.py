# Task 2
import pandas as pd
import statistics

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

# This chunk of code initializes the data frame that will eventually be exported to a .xlsx file.
# Each time the following for loop runs, a record is appended onto df_ET.
iterables = [['init'], ["Mean", "Standard Dev"]]
index = pd.MultiIndex.from_product(iterables, names=["2010-2021", ""])
init_data = [
    [(0,0), (0,1), (0,2), (0,3), (0,4), (0,5), (0,6), (0,7), (0,8), (0,9), (0,10), (0,11)],
    [(1,0), (1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (1,7), (1,8), (1,9), (1,10), (1,11)]
]
df_ET = pd.DataFrame(init_data, index=index)
df_EToF = df_ET.copy(deep=True)

for site in site_list:

    # Reads the data in for the given site
    try:
        df = pd.read_csv('raw_data/ucrb_riparain_et/' + site +'_EEMETRIC_monthly_et_etof.csv')
    except:
        print("ERROR WHEN READING DATA FROM SITE: " + site)
        exit(1)

    # Changes the end date column to 'month' through string manipulation
    df['END_DATE'] = df['END_DATE'].apply(lambda x: int(x[5:7]))
    df.rename({'END_DATE': "Month"}, axis=1, inplace=True)

    record_mean_ET = []
    record_std_ET = []
    record_mean_EToF = []
    record_std_EToF = []
    for i in range(12):

        df_monthly = df[df["Month"] == (i + 1)]

        mean_ET = round(statistics.mean(df_monthly['ET_MEAN']), 3)
        stdev_ET = round(statistics.stdev(df_monthly['ET_MEAN']), 3)
        mean_EToF = round(statistics.mean(df_monthly['EToF_MEAN']), 3)
        stdev_EToF = round(statistics.stdev(df_monthly['EToF_MEAN']), 3)

        record_mean_ET.append(mean_ET)
        record_std_ET.append(stdev_ET)
        record_mean_EToF.append(mean_EToF)
        record_std_EToF.append(stdev_EToF)

    # Get site name and calculate mean and standard dev.
    site_name = df_metadata.loc[df_metadata['station_id'] == int(site),'site_name'].iloc[0]
    df_ET.loc[(site_name, 'Mean'), :] = record_mean_ET
    df_ET.loc[(site_name, 'Standard Dev'), :] = record_std_ET
    df_EToF.loc[(site_name, 'Mean'), :] = record_mean_EToF
    df_EToF.loc[(site_name, 'Standard Dev'), :] = record_std_EToF

# Drop the first record that was used to initialize the data frame
df_ET.drop('init', inplace=True)
df_EToF.drop('init', inplace=True)

# Change the names of the 12 columns to the month names.
for cols, i in enumerate(df_ET):
    df_ET.rename({i: month_dict[i + 1]}, axis=1, inplace=True)
    df_EToF.rename({i: month_dict[i + 1]}, axis=1, inplace=True)

# Write the 2 dataframes to the .xlsx file and format it.
writer = pd.ExcelWriter('table_of_mean_monthly_rates_with_std_deviation.xlsx', engine='xlsxwriter')

df_ET.to_excel(writer, sheet_name='Sheet1', startrow=1)
df_EToF.to_excel(writer, sheet_name='Sheet1', startrow=len(df_ET) + 5)

ws = writer.sheets['Sheet1']
ws.write_string(0, 0, 'Monthly ET Rates (mm/month)')
ws.write_string(len(df_ET) + 4, 0, 'Monthly EToF (unitless)')
ws.set_column(0, 0, 45)
ws.set_column(1, 1, 25)

writer.save()