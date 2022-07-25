# Task 3
import pandas as pd
import os
from scipy import stats
import numpy as np
from bokeh.io import output_file, save
from bokeh.plotting import figure
from bokeh.models import LinearAxis, Range1d, ColumnDataSource
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
def load_metadata():
    
    try:
        df_metadata = pd.read_csv('raw_data/metadata.csv')
    except:
        print("ERROR WITH READING METADATA")
        exit(1)
        
    return df_metadata


# Reads the data in for the given site
def load_raw_data_and_join(site):
    try:
        df_fl = pd.read_csv('../raw_data/flow/' + site + '_monthly_summary.csv')
        df_et = pd.read_csv('../raw_data/ucrb_riparain_et/' + site + '_EEMETRIC_monthly_et_etof.csv')
    except:
        print("ERROR WHEN READING DATA FROM SITE: " + site)
        exit(1)

    # Truncates a column in the evap data so that it matches a column in the flow data.
    # The columns need to match so that a left join can be performed
    df_et['END_DATE'] = df_et['END_DATE'].apply(lambda x: x[0:7])
    df_et.rename({'END_DATE': "date"}, axis=1, inplace=True)
    df_data = df_et.merge(df_fl, on='date', how='left')

    # Changes the start date column from type 'string' to 'datetime'
    # This is needed for plotting the x axis
    df_data['START_DATE'] = df_et['START_DATE'].apply(lambda x: pd.to_datetime(x))

    # Here the month column is changed from int to string.
    # Example: 1 --> 'jan'
    df_data['month'] = df_data['month'].apply(lambda x: month_dict[x])
    
    return df_data

# Takes in a 'cfs' variable and compares it against EToF.
# Makes 3 plots for each site.
# Series, scatter, and a 4 * 3 monthly scatter plot.
def make_plots(cfs_var):

    df_metadata = load_metadata()
    
    # Create a folder for 'plots'
    path = os.getcwd() + '/plots'
    if not (os.path.isdir(path)):
        os.mkdir('plots')
    os.chdir('plots')

    for site in site_list:

        site_name = df_metadata.loc[df_metadata['station_id'] == int(site), 'site_name'].iloc[0]
        output_file(site + '_time_series__EToF_vs_' + cfs_var + '.html')

        df_data = load_raw_data_and_join(site)

        # If a directory for the site does not exist, make it.
        path = os.getcwd() + '/' + site + '_plots'
        if not (os.path.isdir(path)):
            os.mkdir(site + '_plots')

        #######################################################
        # Series plot Configuration
        p = figure(x_axis_type="datetime", width=1500)
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        circle = p.circle(x='START_DATE', y=cfs_var,
                 legend_label= cfs_var + ', Monthly (cfs)',
                 source=ColumnDataSource(df_data),
                 color='blue', size=6)
        p.line(x='START_DATE', y=cfs_var,
               source=ColumnDataSource(df_data),
               color='blue')

        p.extra_y_ranges = {"foo": Range1d(start=df_data['EToF_MEAN'].min() - 5, end=df_data['EToF_MEAN'].max() + 5)}
        circle2 = p.circle(x='START_DATE', y='EToF_MEAN',
                 source=ColumnDataSource(df_data),
                 y_range_name='foo',
                 legend_label='EToF_MEAN, Monthly (mm/month)',  # idk if this is the right units
                 color='green', size=6)
        p.line(x='START_DATE', y='EToF_MEAN',
               source=ColumnDataSource(df_data),
               y_range_name='foo',
               color='green')

        p.title.text = 'SITE: ' + site_name + ', ' + site + ' - EToF_MEAN vs. ' + cfs_var
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = cfs_var + ', Monthly (cfs)'
        p.add_layout(LinearAxis(y_range_name="foo", axis_label='EToF_MEAN, Monthly (mm/month)'), 'right')

        hover = HoverTool()
        hover.renderers = [circle, circle2]
        p.legend.click_policy = 'hide'
        hover.tooltips = [
            ('Year', '@year'),
            ('Month', '@month'),
            ('EToF_MEAN', '@EToF_MEAN'),
            (cfs_var, '@' + cfs_var)
        ]
        p.add_tools(hover)

        os.chdir(path)
        save(p)

        #######################################################
        # Scatter plot Configuration
        output_file(site + '_scatter_plot__EToF_vs_' + cfs_var + '.html')

        p2 = figure(width=900, height=900)
        p2.xgrid.grid_line_color = None
        p2.ygrid.grid_line_color = None
        circle3 = p2.circle(x=cfs_var, y='EToF_MEAN',
                  source=ColumnDataSource(df_data),
                  color='black', fill_color="#add8e6",
                  size=8)

        p2.title.text = 'SITE: ' + site_name + ', ' + site + ' - Flow vs. EToF'
        p2.yaxis.axis_label = 'EToF_MEAN, Monthly (mm/month)'
        p2.xaxis.axis_label = cfs_var + ', Monthly (cfs)'

        # Calculate the least-square regression line
        regression_line = np.polyfit(df_data[cfs_var], df_data['EToF_MEAN'], 1, full=True)
        slope = regression_line[0][0]
        intercept = regression_line[0][1]
        y_predicted = [slope * i + intercept for i in df_data[cfs_var]]
        p2.line(df_data[cfs_var], y_predicted, color='black')

        # Calculations to be used in the stats label on every scatter plot
        pearson_r, pearson_p = stats.pearsonr(df_data['EToF_MEAN'], df_data[cfs_var])
        kendall_r, kendall_p = stats.kendalltau(df_data['EToF_MEAN'], df_data[cfs_var])

        # The stats label to be added.
        label_text = 'Slope: ' + str(round(slope * 1e4, 3)) + ' 1e-4' + '\n' + \
                     'Intercept: ' + str(round(intercept, 3)) + '\n' + \
                     'Pearson r: ' + str(round(pearson_r, 3)) + '\n' + \
                     'Pearson P-Value: ' + str(round(pearson_p, 3)) + '\n' + \
                     'Kendall Tau: ' + str(round(kendall_r, 3)) + '\n' + \
                     'Kendall P-Value: ' + str(round(kendall_p, 3)) + '\n' + \
                     'n: ' + str(len(df_data))
        label = Label(x=620, y=70, x_units='screen', y_units='screen', text=label_text)
        p2.add_layout(label)

        hover2 = HoverTool()
        hover2.renderers = [circle3]
        hover2.tooltips = [
            ('Year', '@year'),
            ('Month', '@month'),
            ('EToF_MEAN', '@EToF_MEAN'),
            (cfs_var, '@' + cfs_var)
        ]
        p2.add_tools(hover2)

        save(p2)

        #######################################################
        # Monthly scatter plot

        output_file(site + '_monthly_scatter_plot__EToF_vs_' + cfs_var + '.html')
        list_of_monthly_figs = []

        for i in range(12):
            df_monthly = df_data[df_data["month"] == month_dict[i + 1]]

            p_month = figure(width=450, height=450)
            p_month.xgrid.grid_line_color = None
            p_month.ygrid.grid_line_color = None
            circle4 = p_month.circle(x=cfs_var, y='EToF_MEAN',
                           source=ColumnDataSource(df_monthly),
                           color='black', fill_color="#add8e6",
                           size=8)

            p_month.title.text = month_dict[i + 1] + ' - ' + site_name + ', ' + site
            p_month.yaxis.axis_label = 'EToF_MEAN, Monthly (mm/month)'
            p_month.xaxis.axis_label = cfs_var + ', Monthly (cfs)'

            # Calculate the least-square regression line
            regression_line = np.polyfit(df_monthly[cfs_var], df_monthly['EToF_MEAN'], 1, full=True)
            slope = regression_line[0][0]
            intercept = regression_line[0][1]
            y_predicted = [slope * i + intercept for i in df_monthly[cfs_var]]
            p_month.line(df_monthly[cfs_var], y_predicted, color='black')

            # Calculations to be used in the stats label on every scatter plot
            pearson_r, pearson_p = stats.pearsonr(df_monthly['EToF_MEAN'], df_monthly[cfs_var])
            kendall_r, kendall_p = stats.kendalltau(df_monthly['EToF_MEAN'], df_monthly[cfs_var])

            # The stats label to be added.
            label_text = 'Slope: ' + str(round(slope * 1e4, 3)) + ' 1e-4' + '\n' + \
                         'Intercept: ' + str(round(intercept, 3)) + '\n' + \
                         'Pearson r: ' + str(round(pearson_r, 3)) + '\n' + \
                         'Pearson P-Value: ' + str(round(pearson_p, 3)) + '\n' + \
                         'Kendall Tau: ' + str(round(kendall_r, 3)) + '\n' + \
                         'Kendall P-Value: ' + str(round(kendall_p, 3)) + '\n' + \
                         'n: ' + str(len(df_monthly))
            label = Label(x=255, y=20, x_units='screen', y_units='screen',
                          text_font_size='8pt', text=label_text)
            p_month.add_layout(label)

            hover3 = HoverTool()
            hover3.renderers = [circle4]
            hover3.tooltips = [
                ('Year', '@year'),
                ('EToF_MEAN', '@EToF_MEAN'),
                (cfs_var, '@' + cfs_var)
            ]
            p_month.add_tools(hover3)

            list_of_monthly_figs.append(p_month)

        save(gridplot([[list_of_monthly_figs[0], list_of_monthly_figs[1], list_of_monthly_figs[2], list_of_monthly_figs[3]],
                       [list_of_monthly_figs[4], list_of_monthly_figs[5], list_of_monthly_figs[6], list_of_monthly_figs[7]],
                       [list_of_monthly_figs[8], list_of_monthly_figs[9], list_of_monthly_figs[10],
                        list_of_monthly_figs[11]]]))

        os.chdir('..')
    os.chdir('..')

def make_tables(cfs_var):
    
    df_metadata = load_metadata()
    
    # These dfs are used for exporting stats to the .xlsx files.
    # Each time the loop is executed, a record is appended onto each df.
    # When the loop is finished, the dfs are exported to the corresponding .xlsx files.
    df_pearsons_r = pd.DataFrame({'station_id': [], 'site_name': [], 'January': [], 'February': [],
                                      'March': [], 'April': [], 'May': [], 'June': [], 'July': [], 'August': [],
                                      'September': [], 'October': [], 'November': [], 'December': []})
    df_pearson_p = df_pearsons_r.copy(deep=True)
    df_kendall_r = df_pearsons_r.copy(deep=True)
    df_kendall_p = df_pearsons_r.copy(deep=True)

    # If a 'tables' directory does not exist, make it
    path = os.getcwd() + '/tables'
    if not (os.path.isdir(path)):
        os.mkdir('tables')
    os.chdir('tables')

    for site in site_list:

        site_name = df_metadata.loc[df_metadata['station_id'] == int(site), 'site_name'].iloc[0]
        df_data = load_raw_data_and_join(site)

        ##########################################################################
        # Pearson Correlation Coefficient Calculations

        record_pearson_r = [site, site_name]
        record_pearson_p = [site, site_name]

        for i in range(12):
            df_monthly = df_data[df_data["month"] == month_dict[i + 1]]

            r_correlation, p_pearson = stats.pearsonr(df_monthly['EToF_MEAN'], df_monthly[cfs_var])

            record_pearson_r.append(round(r_correlation, 3))
            record_pearson_p.append(round(p_pearson, 3))

        df_pearsons_r.loc[len(df_pearsons_r.index)] = record_pearson_r
        df_pearson_p.loc[len(df_pearson_p.index)] = record_pearson_p

        #######################################################
        # Kendall Rank Correlation Coefficient Calculations

        record_kendall_r = [site, site_name]
        record_kendall_p = [site, site_name]

        for i in range(12):
            df_monthly = df_data[df_data["month"] == month_dict[i + 1]]

            tau_correlation_mediancfs, p_pearson = stats.kendalltau(df_monthly['EToF_MEAN'], df_monthly[cfs_var])

            record_kendall_r.append(round(tau_correlation_mediancfs, 3))
            record_kendall_p.append(round(p_pearson, 3))

        df_kendall_r.loc[len(df_kendall_r.index)] = record_kendall_r
        df_kendall_p.loc[len(df_kendall_p.index)] = record_kendall_p

    ################################################################
    # Set the metadata for the .xlsx files and export the dataframes.
    # We do this for both kendall and pearson files.

    # Pearson start
    df_pearsons_r = df_pearsons_r.transpose()
    df_pearson_p = df_pearson_p.transpose()

    writer = pd.ExcelWriter('pearson_correlations_EToF_vs_' + cfs_var + '.xlsx', engine='xlsxwriter')

    df_pearsons_r.to_excel(writer, sheet_name=cfs_var, index=True)
    df_pearson_p.to_excel(writer, sheet_name=cfs_var, index=True, startrow=17)

    ws = writer.sheets[cfs_var]
    ws.write_string(0, 0, 'Pearson Correlation Coefficient: R')
    ws.write_string(17, 0, 'P-value')
    ws.set_column(0, 50, 35)

    # Kendall start
    df_kendall_r = df_kendall_r.transpose()
    df_kendall_p = df_kendall_p.transpose()

    writer2 = pd.ExcelWriter('kendall_correlations_EToF_vs_' + cfs_var + '.xlsx', engine='xlsxwriter')

    df_kendall_r.to_excel(writer2, sheet_name=cfs_var, index=True)
    df_kendall_p.to_excel(writer2, sheet_name=cfs_var, index=True, startrow=17)

    ws = writer2.sheets[cfs_var]
    ws.write_string(0, 0, "Kendall's Correlation: Tau")
    ws.write_string(17, 0, 'P-value')
    ws.set_column(0, 50, 35)

    writer.save()
    writer2.save()
    os.chdir('..')

def main():
    make_plots('median_cfs')
    make_plots('Q25_cfs')
    make_tables('median_cfs')
    make_tables('Q25_cfs')

main()