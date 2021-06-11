import numpy as np
import pandas as pd
import pyodbc as pyodbc
import yagmail
from GraphObject import GraphObject
from StoreFrontPivot import store_front
import os
from PIL import Image
from fpdf import FPDF
import matplotlib.pyplot as plt

name_array = []


def update_ssms_tables(cnxn):
    cursor = cnxn.cursor()
    stored_procedure = "Exec UpdateFooTables"
    cursor.execute(stored_procedure)
    cursor.commit()
    print("SSMS tables updated")


def summary_data(cnxn):
    summary = pd.DataFrame(
        pd.read_sql("SELECT SUM([Yes_signed_up_for_vaccine_appointment])+ SUM([Yes_added_to_the_waitlist]) "
                    "As AppointmentsMade, LEFT(BooDate,11) BooDate FROM [dbo].[FooDataFormatted] "
                    "WHERE FORMAT(CONVERT(DATETIME, BooDate),'yyyy-MM-dd') >= GETDATE()- 14 "
                    "GROUP BY BooDate", cnxn))
    pivot_chart = pd.pivot_table(summary, index='BooDate', values='AppointmentsMade', aggfunc=np.sum,
                                fill_value='N/A', margins=True, margins_name='Total')

    file_name = "Data.csv"
    pivot_chart.to_csv(file_name)
    return file_name


def weekly(cnxn):
    weekly_data = pd.DataFrame(pd.read_sql("SELECT * FROM FooDataWeekly", cnxn))

    city = list(weekly_data["City"])
    already_vaccinated_percent = list(weekly_data["AlreadyVaccinatedWaitlistedPercent"])
    took_survey = list(weekly_data["TakeSurvey"])
    barriers_percent = list(weekly_data["BarriersPercent"])
    undecided_percent = list(weekly_data["UndecidedPercent"])
    signed_up_percent = list(weekly_data["SignedUpPercent"])
    did_not_sign_up_percent = list(weekly_data["DidNotSignUpPercent"])

    A = np.array(already_vaccinated_percent)
    B = np.array(barriers_percent)
    C = np.array(undecided_percent)
    D = np.array(signed_up_percent)
    E = np.array(did_not_sign_up_percent)
    F = np.array(took_survey)

    fig = plt.figure()
    pos = range(len(city))
    plt.xticks(pos, city, size='small')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Percentages of Answers')
    plt.xlabel('City')
    plt.title('Data Dive for the Past Week', fontsize=14)
    plt.ylim([0, 200])

    plt.bar(pos, A)
    plt.bar(pos, B, bottom=A)
    plt.bar(pos, C, bottom=A + B)
    plt.bar(pos, D, bottom=A + B + C)
    plt.bar(pos, E, bottom=A + B + C + D)

    plt.legend(['Already Vaccinated', 'Barriers', 'Undecided', 'SignedUp', 'NotSignedUp'], loc=0)
    ax2 = plt.twinx()
    ax2.plot(F, color='black')
    ax2.set_ylabel('Number of Surveys Taken')
    plt.tight_layout()

    file_name = "Data Past Week.png"
    fig.savefig(file_name)
    return file_name


def graphing(cnxn):
    pdf = FPDF()
    w, h = 0, 0

    data = pd.DataFrame(pd.read_sql
                        ("SELECT * FROM FooData WHERE BooDate >= CAST(getdate() - 8 as date) ORDER BY "
                         "CityAgeRange", cnxn))

    name_array.append(weekly(cnxn))

    for i in range(1, 8):
        graph = GraphObject(i, data, weekly)
        name_array.append(graph.func())

    for i in range(len(name_array)):
        fname = name_array[i]
        if os.path.exists(fname):
            if i == 0:
                cover = Image.open(fname)
                w, h = cover.size
                pdf = FPDF(unit="pt", format=[w, h])
            image = fname
            pdf.add_page()
            pdf.image(image, 0, 0, w, h)
        else:
            print("File not found:", fname)
        print("processed %d" % i)
    pdf.output("Graphs.pdf", "F")
    print("Done")

    yag = yagmail.SMTP('nwilbur@gmail.org')
    contents = [
        "Please see attached data.", 'Graphs.pdf', 'Data.csv',
        'PivotTable.csv']
    yag.send(
        ['nwilbur@gmail.org', 'jsmith@gmail.org'], 'Graphs and Data Updates',
        contents)
    print("Sent")
    return name_array


def main():
    cnxn_str = ("Driver={SQL Server Native Client 11.0};"
                "Server=foo.database.windows.net;"
                "Database=FooDataBase;"
                "UID=foo;"
                "PWD=Password; autocommit=True")
    cnxn = pyodbc.connect(cnxn_str)
    #update_ssms_tables(cnxn)
    summary_data(cnxn)
    store_front()
    graphing(cnxn)
    for i in range(len(name_array)):
        os.remove(name_array[i])
    os.remove("Graphs.pdf")
    os.remove("Data.csv")
    os.remove("PivotTable.csv")
    cnxn.close()


main()
