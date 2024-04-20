import pandas as pd
import os

path = os.getcwd() + "\\Cleansed_data\\kprm-20231115.csv\\kprm-20231115.csv"
new_df = pd.read_csv(path, sep=";")
# Correcting a typo.
new_df.rename(columns={"date_annouced": "date_announced"}, inplace=True)


# Converting required level of educations to hierarchical categorical variables:
# 1 - high school education
# 2 - specific profile of high school education
# 3 - higher education
# 4 - specific profile of higher education
# There are no ads that would require less than high school education.
for index, row in new_df.iterrows():
        if row["education"][0:7] == "średnie":
            if len(row["education"]) > 10:
                new_df.at[index, "education"] = 1
            else:
                new_df.at[index, "education"] = 2
        elif row["education"][0:6] == "wyższe":
            if len(row["education"]) > 9:
                new_df.at[index, "education"] = 3
            else:
                new_df.at[index, "education"] = 4


# Unifying the work_time column - the values there, representing a part of the full-time job, have been entered in various formats - e.g. 0.5 and 1/2.
# new_df.loc[:, 'work_time'].unique()
from fractions import Fraction

# Lines necessary for the code below it.
full_time_in_string_df = new_df[new_df['work_time'].str.contains(r'pełen|pełny|1|cały', na=False)]
full_time_in_string_indexes = list(full_time_in_string_df.index)
part_time_in_string_df = new_df[new_df['work_time'].str.contains(r'etatu|lub', na=False)]
part_time_in_string_indexes = list(part_time_in_string_df.index)

# Cleansing the work_time column.
for index, row in new_df.iterrows():
    try:
        new_df.loc[index, 'work_time'] = float(new_df.loc[index, 'work_time'])
    except ValueError:
        try:
            new_df.loc[index, 'work_time'] = float(Fraction(new_df.loc[index, 'work_time']))
        except ValueError:
            try:
                new_df.loc[index, 'work_time'] = float(new_df.loc[index, 'work_time'].replace(',', '.'))
            except ValueError:
                if new_df.loc[index, 'work_time'][9:13] == "0,75":
                    new_df.loc[index, 'work_time'] = 0.75
                elif index in full_time_in_string_indexes:
                    new_df.loc[index, 'work_time'] = 1.0
                elif index in part_time_in_string_indexes:
                    try:
                        new_df.loc[index, 'work_time'] = float(new_df.loc[index, 'work_time'][0:4].replace(',','.'))
                    except ValueError:
                        try:
                            new_df.loc[index, 'work_time'] = float(Fraction(new_df.loc[index, 'work_time'][0:3]))
                        except ValueError:
                            print(new_df.loc[index, 'work_time'])
                elif new_df.loc[index, 'work_time'] == '¼':
                    new_df.loc[index, 'work_time'] = 0.25
                elif new_df.loc[index, 'work_time'] == '3/ 4':
                    new_df.loc[index, 'work_time'] = 0.75
                elif new_df.loc[index, 'work_time'] == '2x0,5':
                    new_df.loc[index, 'work_time'] = 0.5
                # Assuming that more than 1.6 * full-time job is too much to be true.
                elif new_df.loc[index, 'work_time'] == "zastępstwo" or new_df.loc[index, 'work_time'] >= 1.6 or new_df.loc[index, 'work_time'] <= 0.01:
                    new_df.loc[index, 'work_time'] = None


# Filtering out ads with "recruitment canceled" without a reason given.
result2_new_df = new_df.loc[(new_df['result1'] == 'anulowano nabór') & (~new_df["result2"].isna())]
no_reason_cancel_df = new_df.loc[(new_df['result1'] == 'anulowano nabór') & (new_df["result2"].isna())]

# Converting a column to lower case.
result2_new_df.loc[:, ['result2']] = result2_new_df['result2'].str.lower()

# Determining the reason for the cancellation (in the case of only "anulowano nabór" present in result1)
# and assigning records to a corresponding dataframe, depending on if it's a failure or an error.
result2_new_df_error = result2_new_df[result2_new_df['result2'].str.contains(
    r'łędu|łąd|łędem|łędne|orekta ogłoszenia|łędnie|łędny|łędy w ogłoszeniu|rak informacji|ie uwzględniono|łędna|omyłkowo|omyłka|nie uwwzględniono|przypadkowo|dwukrotnie|podwójnie|razy wprowadzono te same|zdublowane|problem techniczny|miana treści|wymaga korekty|nie zawierało wszystkich|korekta|rak informacji|w wymaganiach|błędy|błędnie'
)][['result2']]

# The reason for leaving out first letters of w ords in some cases is that there are cases with such typos.
result2_new_df_failure = result2_new_df[result2_new_df['result2'].str.contains(
    r'bez wyboru kandydatki/kandydata|nie wybrano|nie zatrudniono|rak aplikacji|rak zgłoszeń|rak ofert|rak kandydatów|rak zapisów|rak zapisu kandydatów|kandydaci zrezygnowali|ikt się nie zgłosił|rak kandydatur|rak wniosków|bez zatrudnienia|kandydat zrezygnował|nie spełniały wymagań|nie wyłoniono|rezygnacji kandydata|rezygnacja|kandydat zrezygnował|zrezygnował z|nie zgłosił się|andydaci nie przybyli|zrezygnowali|braku kandydatur|kandydatka zrezygnowała|ezygnacja kandydatki|żadna oferta|rak złożonych ofert|ezygnacja kandydata|nadesłanych ofert|braku kandydatów|braku kandydatur|adna aplikacja|adnej oferty|0 ofert|brak kandydatek|raku kandydatur|rak zgłoszeń|nie zgłosił|rezygnacja|zrezygnował|ie zgłosili się|Liczba kandydatów 2, w tym 1 oferta - nie spełnia niezbędnych wymagań, 1 oferta - wycofana w trakcie trwania naboru|bark zgłoszeń|brak kandydata|braku ofert')
][['result2']]

# Applying same steps to the rest of the records.
new_df.loc[:, ['result1']] = new_df['result1'].str.lower()
rest_new_df_error = new_df[new_df['result1'].str.contains(
    r'łędu|łąd|łędem|łędne|orekta ogłoszenia|łędnie|łędny|łędy w ogłoszeniu|rak informacji|ie uwzględniono|łędna|omyłkowo|omyłka|omyłką|mylnie|nie uwwzględniono|nie uwzględniono|przypadkowo|dwukrotnie|podwójnie|razy wprowadzono te same|zdublowane|problem techniczny|miana treści|wymaga korekty|nie zawierało wszystkich|korekta|rak informacji|w wymaganiach|błędy|błędnie')
][['result1']]
rest_new_df_failure = new_df[new_df['result1'].str.contains(
    r'bez wyboru kandydatki/kandydata|nie wybrano|nie zatrudniono|rak aplikacji|rak zgłoszeń|rak ofert|rak kandydatów|rak zapisów|rak zapisu kandydatów|kandydaci zrezygnowali|ikt się nie zgłosił|rak kandydatur|rak wniosków|bez zatrudnienia|kandydat zrezygnował|nie spełniały wymagań|nie wyłoniono|rezygnacji kandydata|rezygnacja|kandydat zrezygnował|zrezygnował z|nie zgłosił się|andydaci nie przybyli|zrezygnowali|braku kandydatur|kandydatka zrezygnowała|ezygnacja kandydatki|żadna oferta|rak złożonych ofert|ezygnacja kandydata|nadesłanych ofert|braku kandydatów|braku kandydatur|adna aplikacja|adnej oferty|0 ofert|brak kandydatek|raku kandydatur|rak zgłoszeń|nie zgłosił|rezygnacja|zrezygnował|ie zgłosili się|Liczba kandydatów 2, w tym 1 oferta - nie spełnia niezbędnych wymagań, 1 oferta - wycofana w trakcie trwania naboru|bark zgłoszeń|brak kandydata|braku ofert')
][['result1']]

# Ads that ended successfully - a candidate has been employed.
new_df_success = new_df[new_df['result1'].str.contains(
    r'wyborem kandydatki/kandydata|informacja o zatrudnieniu kandydatki|zatrudnieniem|obsadzono stanowisko|wybrano kandydat')
][['result1']]

# Displaying ads that ended up without an assignment.
assigned_ads_indexes = list(new_df_success.index) + list(rest_new_df_error.index) + list(rest_new_df_failure.index) + list(result2_new_df_failure.index) + list(result2_new_df_error.index) + list(no_reason_cancel_df.index)

left_ads_df = new_df[~new_df.index.isin(assigned_ads_indexes)]

# Turns out most of the left ads (1441) are irrelevant for the analysis - canceled for various reasons.
new_df = new_df[~new_df.index.isin(list(left_ads_df.index))]
# Excluding errors too.
cleansed_df = new_df[new_df.index.isin(list(new_df_success.index)+list(rest_new_df_failure.index)+list(result2_new_df_failure.index))]

# Assigning 1 for ads that led to employment, and 0 where there was no success.
cleansed_df.loc[list(new_df_success.index), 'result1'] = 1
cleansed_df.loc[list(result2_new_df_failure.index)+list(rest_new_df_failure.index), 'result1'] = 0