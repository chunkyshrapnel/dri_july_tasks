# Task 4
import pandas as pd

site_list = ['09180000',  # DOLORES RIVER NEAR CISCO, UT,
             '09209400',  # GREEN RIVER NEAR LA BARGE, WY,
             '09260000',  # LITTLE SNAKE RIVER NEAR LILY, CO
             '09302000',  # DUCHESNE RIVER NEAR RANDLETT, UT,
             '09306500',  # WHITE RIVER NEAR WATSON, UTAH
             '09379500',  # SAN JUAN RIVER NEAR BLUFF, UT
             ]


# Loads metadata in to match site numbers with site names
def load_metadata():
    try:
        df_metadata = pd.read_csv('raw_data/metadata.csv')
    except:
        print("ERROR WITH READING METADATA")
        exit(1)

    return df_metadata


# Loads in all et and flow data
def load_raw_data():

    list_of_flow_dfs = []
    for site in site_list:
        try:
            df_flow = pd.read_csv('raw_data/flow/' + site + '_daily.csv')
        except:
            print("ERROR WHEN READING DATA FROM SITE: " + site)
            exit(1)
        list_of_flow_dfs.append(df_flow)

    try:
        df_et = pd.read_excel('raw_data/ucrb_riparain_et/ucrc_riparian_means.xlsx')
    except:
        print("ERROR WHEN READING ET DATA")
        exit(1)

    return list_of_flow_dfs, df_et


# Combines all the flow data from the different sites and makes 1 big table.
def combine_flow_data(list_of_flow_dfs, df_metadata):

    # This loop adds 'site_name' as a column so that the sites can be differentiated from
    # each other when the dataframes are combined into one big data frame.
    for i, df in enumerate(list_of_flow_dfs):
        site_name = df_metadata.loc[df_metadata['station_id'] == int(site_list[i]), 'site_name'].iloc[0]
        df['site_name'] = site_name

    df_flow = pd.concat(list_of_flow_dfs)
    return(df_flow)


# Calculates the mean growing season flow
def group_by_and_agg(df_flow):

    # Remove all months that are not in growing season (Apr - Oct)
    df_flow = df_flow[df_flow.month != 1]
    df_flow = df_flow[df_flow.month != 2]
    df_flow = df_flow[df_flow.month != 3]
    df_flow = df_flow[df_flow.month != 10]
    df_flow = df_flow[df_flow.month != 11]
    df_flow = df_flow[df_flow.month != 12]

    # Group by and agg
    df_yearly_by_site = df_flow.groupby(['site_name', 'year']). \
        agg({'discharge_cfs': ['mean']})
    
    # Formatting changes to the table
    df_yearly_by_site.rename(columns={'discharge_cfs': 'mean_gs_flow'}, inplace=True)
    df_yearly_by_site.columns = df_yearly_by_site.columns.droplevel(1)

    return df_yearly_by_site
    
    
def main():

    # Loads metadata in to match site numbers with site names
    df_metadata = load_metadata()

    # Loads in all et and flow data
    list_of_flow_dfs, df_et = load_raw_data()

    # Combines all the flow data from the different sites and makes 1 big table.
    df_flow = combine_flow_data(list_of_flow_dfs, df_metadata)

    # Calculates the mean growing season flow
    df_flow = group_by_and_agg(df_flow)

    # Join Data and export to csv
    df_data = df_et.merge(df_flow, on=['site_name', 'year'], how='left')
    df_data.to_csv('growing_season_et_and_flow.csv')

main()









