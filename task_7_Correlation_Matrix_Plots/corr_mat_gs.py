import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from matplotlib.lines import Line2D
import seaborn as sns

# Read the data into two DataFrames and then joins the DataFrames into a single DataFrame
try:
    et_df = pd.read_excel('raw_data/ucrc_riparian_means.xlsx')
    pr_df = pd.read_excel('raw_data/ucrc_cda_pr_means.xlsx')
except:
    print("ERROR WHEN READING IN DATA")
    exit(1)

joined_df = new_df = pd.merge(pr_df, et_df, how='left', left_on=['station_id', 'site_name', 'year'],
                                  right_on=['station_id', 'site_name', 'year'])

# site filter
# joined_df = joined_df[joined_df.station_id == 9379500]

var_list = ['gs_pr', 'ann_pr', 'wy_pr', 'gs_et',
       'gs_etof', 'gs_eto', 'ann_et', 'ann_etof', 'ann_eto']

#%%
corrMatrix = joined_df[var_list].corr().round(2)
ax1 = plt.axes()
mask = np.triu(np.ones_like(corrMatrix, dtype=bool))
sns.heatmap(corrMatrix, annot=True, vmax=1, vmin=-1, center=0, cmap='viridis', mask=mask)

ax1.set_title('Pearson R - All Sites')
plt.show()

#%%
plt.figure()
corrMatrix_tau = joined_df[var_list].corr(method='kendall').round(2)
ax2 = plt.axes()
mask = np.triu(np.ones_like(corrMatrix_tau, dtype=bool))
sns.heatmap(corrMatrix_tau, annot=True, vmax=1, vmin=-1, center=0, cmap='viridis', mask=mask)

ax2.set_title('Kendall Tau- All Sites')
plt.show()

#%%
# plt.figure()
ax1 = joined_df.plot.scatter(x='gs_etof',
           y='gs_et', c='DarkBlue')

#%%
# plt.figure()
ax1 = joined_df.plot.scatter(x='gs_eto',
           y='gs_et', c='DarkBlue')

#%%
# plt.figure()
ax1 = joined_df.plot.scatter(x='ann_pr',
           y='gs_etof', c='DarkBlue')
#%%
# plt.figure()
ax1 = joined_df.plot.scatter(x='wy_pr',
           y='gs_et', c='DarkBlue')

