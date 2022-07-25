# Task 5
import pandas as pd
from scipy import stats
import numpy as np
from bokeh.io import output_file, save
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.annotations import Label
from bokeh.models.tools import HoverTool

# Bug notice: Some of the data recieved, had the leading '0' truncated off the front.
# For example '09180000' --> '9180000'
# If there are any errors with reading in the raw data, please check the site numbers.
site_list = ['09180000',  # DOLORES RIVER NEAR CISCO, UT,
             '09209400',  # GREEN RIVER NEAR LA BARGE, WY,
             '09260000',  # LITTLE SNAKE RIVER NEAR LILY, CO
             '09302000',  # DUCHESNE RIVER NEAR RANDLETT, UT,
             '09306500',  # WHITE RIVER NEAR WATSON, UTAH
             '09379500',  # SAN JUAN RIVER NEAR BLUFF, UT
             ]

# Read in the metadata so that the site names can be attached to the graph.
def load_metadata():
    try:
        df_metadata = pd.read_csv('raw_data/metadata.csv')
    except:
        print("ERROR WITH READING METADATA")
        exit(1)

    return df_metadata

# Read in Data
def load_raw_data():
    try:
        df = pd.read_csv('raw_data/growing_season_et_and_flow.csv')
    except:
        print("ERROR WHEN READING IN DATA")
        exit(1)
    return df


df_metadata = load_metadata()
df = load_raw_data()
output_file('normalized_growing_season.html')

list_of_dfs = []
for site in site_list:

    # Break data down by Site
    site_name = df_metadata.loc[df_metadata['station_id'] == int(site), 'site_name'].iloc[0]
    df_station = df[df["site_name"] == site_name]

    # Normalize the Data
    mean = df_station['mean_gs_flow'].mean()
    df_station = df_station.assign(discharge_mean_cfs=lambda x: (x['mean_gs_flow'] / mean))
    list_of_dfs.append(df_station)
df = pd.concat(list_of_dfs)

p = figure(width=900, height=900)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
circle = p.circle(x='mean_gs_flow', y='gs_etof',
            source=ColumnDataSource(df),
            color='black', fill_color="#add8e6",
            size=8)

p.title.text = 'Normalized Growing Season EToF vs Normalized Mean Flow'
p.title.text_font_size = '9pt'
p.yaxis.axis_label = 'Growing Season EToF'
p.xaxis.axis_label = 'Normalized Growing Season Mean Flow - cfs'

# Calculate the least-square regression line
regression_line = np.polyfit(df['mean_gs_flow'], df['gs_etof'], 1, full=True)
slope = regression_line[0][0]
intercept = regression_line[0][1]
y_predicted = [slope * i + intercept for i in df['mean_gs_flow']]
p.line(df['mean_gs_flow'], y_predicted, color='black')

# Calculations to be used in the stats label on every scatter plot
pearson_r, pearson_p = stats.pearsonr(df['gs_etof'], df['mean_gs_flow'])
kendall_r, kendall_p = stats.kendalltau(df['gs_etof'], df['mean_gs_flow'])

# The stats label to be added.
label_text = 'Slope: ' + str(round(slope, 3)) + '\n' + \
             'Intercept: ' + str(round(intercept, 3)) + '\n' + \
             'Pearson r: ' + str(round(pearson_r, 3)) + '\n' + \
             'Pearson P-Value: ' + str(round(pearson_p, 3)) + '\n' + \
             'Kendall Tau: ' + str(round(kendall_r, 3)) + '\n' + \
             'Kendall P-Value: ' + str(round(kendall_p, 3)) + '\n' + \
             'n: ' + str(len(df))
label = Label(x=700, y=20, x_units='screen', y_units='screen',
             text_font_size='8pt', text=label_text)
p.add_layout(label)

hover = HoverTool()
hover.renderers = [circle]
hover.tooltips = [
    ('Year', '@year'),
    ('Site', '@site_name'),
    ('Growing Season EToF', '@gs_etof'),
    ('Normalized Growing Season Mean Discharge', '@mean_gs_flow')
]
p.add_tools(hover)

save(p)
