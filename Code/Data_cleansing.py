import pandas as pd
import os

# LOADING DATA
path = os.getcwd()[0:-5] + '\\Data\\kprm-with-salary-update-20231115.json'
df = pd.read_json(path, lines=True)

# Dropping unnecessary columns:
# '6' has been split on 2 columns due to an error during the download,
# while '8' is a duplicate of '9' with minor differences. However, '9' is
# believed to be the correct version.
df.drop(columns=[6,8], inplace=True)

# Renaming columns.
df.columns = [
    'Ad ID', 'Job title', 'Employer (entity)', 'Employer location', 'Office address', 'Workplace', 'Department',
    'Posted on', 'Expiration date', 'Detailed recruitment results', 'Salary (monthly)', 'Vacancies', 'Full-time ratio',
    'Recruitment results', 'Description of duties', 'Required level of education', 'Prerequisites',
    'Optional requirements', 'Application instructions', 'Number of views'
]

#print(df['Recruitment results'].nunique())
# The data contains no active posts at the time of the download:
# the column "Recruitment results" contains only one unique value - "Koniec naboru"
# (recruitment finished).
# Thus, we can drop the column.
df.drop(columns=["Recruitment results"], inplace=True)


# REDUCING DATA SIZE
# We're removing unnecessary text from rows, such as "NR" (an abbreviation for number)
# in every cell of the "Ad ID" column.

for index, row in df.iterrows():
    if row['Ad ID'][0] == 'N' and row['Ad ID'][2] == ' ':
        df.at[index, 'Ad ID'] = row['Ad ID'][3:]

    # Removing "Adres urzędu: " from each row.
    if row['Office address'][12] == ':' and row['Office address'][13] == ' ':
        df.at[index, 'Office address'] = row['Office address'][14:]
    elif row['Office address'][12] == ':':
        df.at[index, 'Office address'] = row['Office address'][13:]

    # Removing "Miejsce wykonywania pracy: " from each row.
    if row['Workplace'][25] == ':' and row['Workplace'][26] == ' ':
        df.at[index, 'Workplace'] = row['Workplace'][27:]
    elif row['Workplace'][25] == ':':
        df.at[index, 'Workplace'] = row['Workplace'][26:]

    # Removing "Wykształcenie: " from each row.
    if row['Required level of education'][13] == ':' and row['Required level of education'][14] == ' ':
        df.at[index, 'Required level of education'] = row['Required level of education'][15:]
    elif row['Required level of education'][13] == ':':
        df.at[index, 'Required level of education'] = row['Required level of education'][14:]

    # Removing "Wyniki naboru: " from each row.
    if row['Detailed recruitment results'][14] == ' ' and row['Detailed recruitment results'][13] == ':':
        df.at[index, 'Detailed recruitment results'] = row['Detailed recruitment results'][15:]
    elif row['Detailed recruitment results'][13] == ':':
        df.at[index, 'Detailed recruitment results'] = row['Detailed recruitment results'][14:]

    # Removing "Liczba odwiedzin: " from each row.
    # One additional condition since the first character in most entries is a space.
    if row['Required level of education'][0] == ' ':
        if row['Number of views'][18] == ':' and row['Number of views'][19] == ' ':
            df.at[index, 'Number of views'] = row['Number of views'][20:]
        elif row['Number of views'][18] == ':' and row['Number of views'][1].lower() == 'l':
            df.at[index, 'Number of views'] = row['Number of views'][19:]
    else:
        if row['Number of views'][17] == ':' and row['Number of views'][18] == ' ':
            df.at[index, 'Number of views'] = row['Number of views'][19:]
        elif row['Number of views'][16] == ':' and row['Number of views'][0].lower() == 'l':
            df.at[index, 'Number of views'] = row['Number of views'][17:]
#df.head()

# DATA SPLIT
# Splitting the data and exploring the frequency of different recruitment results.

# Announcements that ended with the employment of a candidate.
df_success = df[df['Detailed recruitment results'].str.contains(
    r'wyborem kandydatki/kandydata|informacja o zatrudnieniu kandydatki|zatrudnieniem'
)][['Detailed recruitment results']]
success_count = len(df_success)

# Announcements that ended without employing a candidate.
# Jak skategoryzować ogłoszenia, które w rezultacie mają wpisane
# "decyzja o rezygnacji kandydata z obejmowanego stanowiska"?
# Na razie są wrzucone jako fail, aczkolwiek jest to dyskusyjne.
df_failure = df[df['Detailed recruitment results'].str.contains(r'bez wyboru kandydatki/kandydata|nie wybrano|nie zatrudniono|rak aplikacji|rak zgłoszeń|rak ofert|rak kandydatów|rak zapisu|kandydaci zrezygnowali|ikt się nie zgłosił|rak kandydatur|rak wniosków|bez zatrudnienia|kandydat zrezygnował|nie spełniały wymagań|nie wyłoniono|rezygnacji|rezygnacja|kandydat zrezygnował|zrezygnował z|nie zgłosił się|andydaci nie przybyli|zrezygnowali|braku kandydatur|kandydatka zrezygnowała|ezygnacja kandydatki|żadna oferta|rak złożonych ofert|ezygnacja kandydata|nadesłanych ofert|braku kandydatów|braku kandydatur')][['Detailed recruitment results']]
failure_count = len(df_failure)


# Announcements that have been cancelled as a results of an error; they are omitted in our analysis.
df_error1 = df[df['Detailed recruitment results'].str.contains(r'łędu|łąd|łędem|łędne|orekta ogłoszenia|łędnie|łędny|łędy w ogłoszeniu|rak informacji|ie uwzględniono|łędna|omyłkowo|omyłka|nie uwwzględniono|przypadkowo|dwukrotnie|podwójnie|razy wprowadzono te same|zdublowane|problem techniczny|miana treści|wymaga korekty')][['Detailed recruitment results']]
error1_count = len(df_error1)

df_error2 = df.loc[df['Detailed recruitment results'] == 'anulowano nabór|']
error2_count = len(df_error2)

error_count = error1_count + error2_count
print(f"Ads that led to employment: {success_count}\n"
      f"Ads that did not lead to employment: {failure_count}\n"
      f"Ads cancelled as a result of an error: {error1_count}")


# A relatively small amount of ads was left, and they're not a subject of our analysis (e.g. a decision to cancel a vacancy or the return of an employee to work).
# From now on, we're going to operate only on ads present in failure_df and success_df.
df_failure = df[df.index.isin(list(df_failure.index))]
df_success = df[df.index.isin(list(df_success.index))]
dfs_of_interest = [df_failure, df_success]


# Comparing frequency of "no salary given" in failure and success.
df_failure_no_salary = df_failure[df_failure['Salary (monthly)'].str.contains('nie podano')][['Salary (monthly)']]
df_success_no_salary = df_success[df_success['Salary (monthly)'].str.contains('nie podano')][['Salary (monthly)']]
failure_no_salary_count = len(df_failure_no_salary)
success_no_salary_count = len(df_success_no_salary)

failure_no_salary_percentage = failure_no_salary_count/failure_count
success_no_salary_percentage = success_no_salary_count/success_count

print(f"Percentage of no salary in df_success: {success_no_salary_percentage}\n"
      f"Percentage of no salary in df_failure: {failure_no_salary_percentage}")


# MAKING DATA READABLE FOR COMPUTERS

# 1. The salary column
#First, we're checking whether all salaries are given as gross (brutto)
# or if there are some given as net (netto).
df_netto = df[df['Salary (monthly)'].str.contains('netto')][['Salary (monthly)']]
count_netto = len(df_netto)
print(count_netto)

# 2. The required level of education column.
# Converting required level of educations to hierarchical categorical variables:
# 1 - high school education
# 2 - specific profile of high school education
# 3 - higher education
# 4 - specific profile of higher education
# There are no ads that would require less than high school education.

for df_of_interest in dfs_of_interest:
    for index, row in df_of_interest.iterrows():
        if row["Required level of education"][0:7] == "średnie":
            if len(row["Required level of education"]) > 10:
                df_of_interest.at[index, "Required level of education"] = 1
            else:
                df_of_interest.at[index, "Required level of education"] = 2
        elif row["Required level of education"][0:6] == "wyższe":
            if len(row["Required level of education"]) > 9:
                df_of_interest.at[index, "Required level of education"] = 3
            else:
                df_of_interest.at[index, "Required level of education"] = 4