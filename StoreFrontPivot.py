import numpy as np
import pandas as pd
import os


def store_front():
    df1 = pd.read_csv('storefrontYesterday.csv', usecols=['Date', 'Area '])[['Date', 'Area ']]
    df1['Appointments'] = int(1)
    df1 = df1.rename(columns={"Area ": "Site"})
    df2 = pd.read_csv('CumulativeData.csv')

    data = pd.concat([df1, df2], axis=0, ignore_index=True)
    data['Site'] = data['Site'].str.rstrip()
    pivot_chart = pd.pivot_table(data, index = 'Date', columns = 'Site', values = 'Appointments', aggfunc = np.sum,
                                fill_value = 'N/A', margins = True, margins_name='Total')

    pivot_chart.to_csv("PivotTable.csv")
    os.remove("CumulativeData.csv")
    data.to_csv("CumulativeData.csv", index=False)

