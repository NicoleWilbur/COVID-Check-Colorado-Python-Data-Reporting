import matplotlib.pyplot as plt
import numpy as np
from datetime import date, timedelta


class GraphObject:
    i = -1
    data = ()
    weekly = ()

    def __init__(self, i, data, weekly):
        self.i = i
        self.data = data
        self.weekly = weekly

    def func(self):
        boo_date = date.today() - timedelta(days=self.i)
        filtered_data = self.data[(self.data.BooDate == str(boo_date))]

        city_age_range = list(filtered_data["CityAgeRange"])
        already_vaccinated_percent = list(filtered_data["AlreadyVaccinatedWaitlistedPercent"])
        took_survey = list(filtered_data["TakeSurvey"])
        barriers_percent = list(filtered_data["BarriersPercent"])
        undecided_percent = list(filtered_data["UndecidedPercent"])
        signed_up_percent = list(filtered_data["SignedUpPercent"])
        did_not_sign_up_percent = list(filtered_data["DidNotSignUpPercent"])

        A = np.array(already_vaccinated_percent)
        B = np.array(barriers_percent)
        C = np.array(undecided_percent)
        D = np.array(signed_up_percent)
        E = np.array(did_not_sign_up_percent)
        F = np.array(took_survey)

        fig = plt.figure()
        pos = range(len(city_age_range))
        plt.xticks(pos, city_age_range, size='small')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Percentages of Answers')
        plt.xlabel('City and Age Group')
        plt.title('Data Dive for ' + str(boo_date), fontsize=14)
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

        file_name = "Data " + str(boo_date) + ".png"
        fig.savefig(file_name)
        return file_name

