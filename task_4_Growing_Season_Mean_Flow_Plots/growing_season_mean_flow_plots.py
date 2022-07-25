# Task 4
import pandas as pd
from scipy import stats
import numpy as np
from bokeh.io import output_file, save
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.annotations import Label
from bokeh.models.tools import HoverTool
from bokeh.layouts import gridplot

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
try:
    df_metadata = pd.read_csv('raw_data/metadata.csv')
except:
    print("ERROR WITH READING METADATA")
    exit(1)


# Read in Data
try:
    df = pd.read_csv('growing_season_et_and_flow.csv')
except:
    print("ERROR WHEN READING IN DATA")
    exit(1)

# Monthly scatter plot
output_file('growing_season_.html')
list_of_monthly_figs = []

for site in site_list:

    site_name = df_metadata.loc[df_metadata['station_id'] == int(site), 'site_name'].iloc[0]
    df_station = df[df["site_name"] == site_name]

    p_site = figure(width=500, height=500)
    p_site.xgrid.grid_line_color = None
    p_site.ygrid.grid_line_color = None
    circle = p_site.circle(x='mean_gs_flow', y='gs_etof',
                  source=ColumnDataSource(df_station),
                  color='black', fill_color="#add8e6",
                  size=8)


    p_site.title.text = site_name + ': Growing Season EtoF vs Mean Flow'
    p_site.title.text_font_size = '9pt'
    p_site.yaxis.axis_label = 'Growing Season EtoF'
    p_site.xaxis.axis_label = 'Growing Season Mean Flow - cfs'
    
    # Calculate the least-square regression line
    regression_line = np.polyfit(df_station['mean_gs_flow'], df_station['gs_etof'], 1, full=True)
    slope = regression_line[0][0]
    intercept = regression_line[0][1]
    y_predicted = [slope * i + intercept for i in df_station['mean_gs_flow']]
    p_site.line(df_station['mean_gs_flow'], y_predicted, color='black')

    # Calculations to be used in the stats label on every scatter plot
    pearson_r, pearson_p = stats.pearsonr(df_station['gs_etof'], df_station['mean_gs_flow'])
    kendall_r, kendall_p = stats.kendalltau(df_station['gs_etof'], df_station['mean_gs_flow'])

    # The stats label to be added.
    label_text = 'Slope: ' + str(round(slope * 1e4 , 3)) + ' 1e-4' + '\n' + \
                 'Intercept: ' + str(round(intercept, 3)) + '\n' + \
                 'Pearson r: ' + str(round(pearson_r, 3)) + '\n' + \
                 'Pearson P-Value: ' + str(round(pearson_p, 3)) + '\n' + \
                 'Kendall Tau: ' + str(round(kendall_r, 3)) + '\n' + \
                 'Kendall P-Value: ' + str(round(kendall_p, 3)) + '\n' + \
                 'n: ' + str(len(df_station))
    label = Label(x=320, y=20, x_units='screen', y_units='screen',
                  text_font_size='8pt', text=label_text)
    p_site.add_layout(label)

    hover = HoverTool()
    hover.renderers = [circle]
    hover.tooltips = [
        ('Year', '@year'),
        ('Growing Season EToF;', '@gs_etof'),
        ('Mean Discharge', '@mean_gs_flow')
    ]
    p_site.add_tools(hover)

    list_of_monthly_figs.append(p_site)

save(gridplot([[list_of_monthly_figs[0], list_of_monthly_figs[1], list_of_monthly_figs[2]],
               [list_of_monthly_figs[3], list_of_monthly_figs[4], list_of_monthly_figs[5]]]))
