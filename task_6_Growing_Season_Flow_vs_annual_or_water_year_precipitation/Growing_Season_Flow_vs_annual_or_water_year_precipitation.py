# Task 6
import pandas as pd
from scipy import stats
import numpy as np
import os
from bokeh.io import output_file, save, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.annotations import Label
from bokeh.models.tools import HoverTool
from bokeh.layouts import gridplot

# Bug notice: Some of the data recieved, had the leading '0' truncated off the front.
# For example '09180000' --> '9180000'
# If there are any errors with reading in the raw data, please check the site numbers.
list_site = ['09180000',  # DOLORES RIVER NEAR CISCO, UT,
             '09209400',  # GREEN RIVER NEAR LA BARGE, WY,
             '09260000',  # LITTLE SNAKE RIVER NEAR LILY, CO
             '09302000',  # DUCHESNE RIVER NEAR RANDLETT, UT,
             '09306500',  # WHITE RIVER NEAR WATSON, UTAH
             '09379500',  # SAN JUAN RIVER NEAR BLUFF, UT
             ]

# This dict is used to transform the var names of the columns into
# more readable names to be used in the plot displays.
dict_var_to_string_conversion = {
    'mean_gs_flow': 'Mean Growing Season Flow (cfs)',
    'ann_pr': 'Annual Precipitation (PLACE HOLDER VAR)',
    'wy_pr': 'Water Year Precipitation (PLACE HOLDER VAR)',
    'gs_pr': 'Growing Season Precipitation (PLACE HOLDER VAR)'
}

# Read in the metadata so that the site names can be attached to the graph.
def load_metadata():
    try:
        df_metadata = pd.read_csv('raw_data/metadata.csv')
    except:
        print("ERROR WITH READING METADATA")
        exit(1)

    return df_metadata


# Read the data into two DataFrames and then joins the DataFrames into a single DataFrame
def load_raw_data_and_join():
    try:
        df1 = pd.read_csv('raw_data/growing_season_et_and_flow.csv')
        df2 = pd.read_excel('raw_data/ucrc_cda_pr_means.xlsx')
    except:
        print("ERROR WHEN READING IN DATA")
        exit(1)

    df_data = df1.merge(df2, on=['station_id', 'site_name', 'year'], how='left')
    df_data.drop(['Unnamed: 0'], axis=1, inplace=True)

    return df_data


# Takes in 2 strings that correspond to the 2 variables that will be charted on
# the x and y axes of the scatter plot. This function will create a 6 x 2 grid of
# plots where each plot corresponds to a site.
def create_site_plots(fl_var, pr_var):

    # Data is loaded in
    df_data = load_raw_data_and_join()
    df_metadata = load_metadata()

    # Name of file that the grid plot will be exported to
    output_file(fl_var + '_vs_' + pr_var + '.html')

    # A plot is created for each site and then appended onto 'list_of_monthly_figs'
    list_of_monthly_figs = []
    for site in list_site:

        site_name = df_metadata.loc[df_metadata['station_id'] == int(site), 'site_name'].iloc[0]
        df_station = df_data[df_data["site_name"] == site_name]

        p_site = figure(width=500, height=500)
        p_site.xgrid.grid_line_color = None
        p_site.ygrid.grid_line_color = None
        circle = p_site.circle(x=pr_var, y=fl_var,
                               source=ColumnDataSource(df_station),
                               color='black', fill_color="#add8e6",
                               size=8)

        p_site.title.text = site_name + '\n' + dict_var_to_string_conversion[fl_var] + ' vs '\
                                             + dict_var_to_string_conversion[pr_var]
        p_site.title.text_font_size = '9pt'
        p_site.yaxis.axis_label = dict_var_to_string_conversion[fl_var]
        p_site.xaxis.axis_label = dict_var_to_string_conversion[pr_var]

        # Calculate the least-square regression line
        regression_line = np.polyfit(df_station[pr_var], df_station[fl_var], 1, full=True)
        slope = regression_line[0][0]
        intercept = regression_line[0][1]
        y_predicted = [slope * i + intercept for i in df_station[pr_var]]
        p_site.line(df_station[pr_var], y_predicted, color='black')

        # Calculations to be used in the stats label on every scatter plot
        pearson_r, pearson_p = stats.pearsonr(df_station[fl_var], df_station[pr_var])
        kendall_r, kendall_p = stats.kendalltau(df_station[fl_var], df_station[pr_var])

        # The stats label to be added.
        label_text = 'Slope: ' + str(round(slope, 3)) + '\n' + \
                     'Intercept: ' + str(round(intercept, 3)) + '\n' + \
                     'Pearson r: ' + str(round(pearson_r, 3)) + '\n' + \
                     'Pearson P-Value: ' + str(round(pearson_p, 3)) + '\n' + \
                     'Kendall Tau: ' + str(round(kendall_r, 3)) + '\n' + \
                     'Kendall P-Value: ' + str(round(kendall_p, 3)) + '\n' + \
                     'n: ' + str(len(df_station))
        label = Label(x=320, y=20, x_units='screen', y_units='screen',
                      text_font_size='8pt', text=label_text)
        p_site.add_layout(label)

        # This hover tool used to display the data for each point on the plot
        hover = HoverTool()
        hover.renderers = [circle]
        hover.tooltips = [
            ('Year', '@year'),
            (dict_var_to_string_conversion[pr_var], '@' + pr_var),
            (dict_var_to_string_conversion[fl_var], '@' + fl_var)
        ]
        p_site.add_tools(hover)

        list_of_monthly_figs.append(p_site)

    # If a 'plots' directory does not exist, make it.
    path = os.getcwd() + '/plots'
    if not (os.path.isdir(path)):
        os.mkdir('plots')

    # Save the 6 plots to a 3 x 2 grid.
    # This section will need to be changed if more sites are added to 'list-sites'
    os.chdir('plots')
    save(gridplot([[list_of_monthly_figs[0], list_of_monthly_figs[1], list_of_monthly_figs[2]],
                   [list_of_monthly_figs[3], list_of_monthly_figs[4], list_of_monthly_figs[5]]]))
    os.chdir('..')


# Creates a massive scatter plot that contains all the sites.
# Each growing season value is normalized by dividing
def create_normalized_combined_plot(fl_var, pr_var):
    df_metadata = load_metadata()
    df_data = load_raw_data_and_join()
    output_file('normalized_' + fl_var + '_vs_' + pr_var + '.html')

    list_of_dfs = []
    for site in list_site:

        # Break data down by Site
        site_name = df_metadata.loc[df_metadata['station_id'] == int(site), 'site_name'].iloc[0]
        df_station = df_data[df_data["site_name"] == site_name]

        # Normalize the Data
        mean = df_station['mean_gs_flow'].mean()
        df_station = df_station.assign(discharge_mean_cfs=lambda x: (x['mean_gs_flow'] / mean))
        list_of_dfs.append(df_station)
    df = pd.concat(list_of_dfs)

    p = figure(width=900, height=900)
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    circle = p.circle(x=pr_var, y=fl_var,
                      source=ColumnDataSource(df),
                      color='black', fill_color="#add8e6",
                      size=8)

    p.title.text =  dict_var_to_string_conversion[fl_var] + ' vs ' \
                        + dict_var_to_string_conversion[pr_var]
    p.title.text_font_size = '15pt'
    p.yaxis.axis_label = dict_var_to_string_conversion[fl_var]
    p.xaxis.axis_label = dict_var_to_string_conversion[pr_var]

    # Calculate the least-square regression line
    regression_line = np.polyfit(df[pr_var], df[fl_var], 1, full=True)
    slope = regression_line[0][0]
    intercept = regression_line[0][1]
    y_predicted = [slope * i + intercept for i in df[pr_var]]
    p.line(df[pr_var], y_predicted, color='black')

    # Calculations to be used in the stats label on every scatter plot
    pearson_r, pearson_p = stats.pearsonr(df[fl_var], df[pr_var])
    kendall_r, kendall_p = stats.kendalltau(df[fl_var], df[pr_var])

    # The stats label to be added.
    label_text = 'Slope: ' + str(round(slope, 3)) + '\n' + \
                 'Intercept: ' + str(round(intercept, 3)) + '\n' + \
                 'Pearson r: ' + str(round(pearson_r, 3)) + '\n' + \
                 'Pearson P-Value: ' + str(round(pearson_p, 3)) + '\n' + \
                 'Kendall Tau: ' + str(round(kendall_r, 3)) + '\n' + \
                 'Kendall P-Value: ' + str(round(kendall_p, 3)) + '\n' + \
                 'n: ' + str(len(df))
    label = Label(x=690, y=20, x_units='screen', y_units='screen',
                  text_font_size='8pt', text=label_text)
    p.add_layout(label)

    hover = HoverTool()
    hover.renderers = [circle]
    hover.tooltips = [
        ('Year', '@year'),
        ('Site', '@site_name'),
        (dict_var_to_string_conversion[fl_var], '@' + fl_var),
        (dict_var_to_string_conversion[pr_var], '@' + pr_var)
    ]
    p.add_tools(hover)

    # If a 'plots' directory does not exist, make it.
    path = os.getcwd() + '/plots'
    if not (os.path.isdir(path)):
        os.mkdir('plots')

    os.chdir('plots')
    save(p)
    os.chdir('..')


def main():

    create_site_plots('mean_gs_flow', 'ann_pr')
    create_site_plots('mean_gs_flow', 'wy_pr')
    create_site_plots('mean_gs_flow', 'gs_pr')

    create_normalized_combined_plot('mean_gs_flow', 'ann_pr')
    create_normalized_combined_plot('mean_gs_flow', 'wy_pr')
    create_normalized_combined_plot('mean_gs_flow', 'gs_pr')

main()