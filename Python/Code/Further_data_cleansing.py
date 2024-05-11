import pandas as pd
import os

path = os.getcwd()[0:-11] + "\\Cleansed_data\\Pre-processed_1\\kprm-20231115.csv\\kprm-20231115.csv"
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

# ASSIGNING POSITION LEVEL CATEGORIES

# Splitting job positions into categories, just like it's been done with 'failure' and 'success'.
assistent_df = cleansed_df[cleansed_df['job_title'].str.contains(r'asystent|pomocnik', case=False)][['job_title']]
junior_df = cleansed_df[cleansed_df['job_title'].str.contains(r'młodszy|mlodszy', case=False)][['job_title']]
senior_df = cleansed_df[cleansed_df['job_title'].str.contains(r'starszy', case=False)][['job_title']]
director_df = cleansed_df[cleansed_df['job_title'].str.contains(r'dyrektor|kierownik|kapitan|naczelnik', case=False)][['job_title']]
# 'Główny' is translated as 'head' or 'main'.
head_df = cleansed_df[cleansed_df['job_title'].str.contains(r'główny|glowny', case=False)][['job_title']]

# Separating "specjalista" and "ekspert" from "młodszy/starszy specjalista/ekspert",
# so that there are no duplicates with junior_df and senior_df.
expert_df = (
    cleansed_df[
        (cleansed_df['job_title'].str.contains(r'ekspert|specjalista', case=False) == True) &
        (cleansed_df['job_title'].str.contains(r'młodszy|mlodszy|starszy', case=False) == False)]
    [['job_title']]
)

# Categorizing ads that ended up without an assignment to the previous categories
# (regular positions, between junior and senior).
position_categories_indexes = (
        list(junior_df.index) + list(senior_df.index) + list(director_df.index) + list(expert_df.index) +
        list(assistent_df.index) + list(head_df.index)
)
mid_df = cleansed_df[~cleansed_df.index.isin(position_categories_indexes)]

# Assigning cleansed categories to a new column - specific categories might turn out useful later on,
# so I don't want to dispose of this information.

# Creating a new column by copying the existing one.
cleansed_df["job_position_category"] = cleansed_df["job_title"]
# Changing the values of the column so that it represents job level categories.
cleansed_df.loc[list(junior_df.index), 'job_position_category'] = 'junior'
cleansed_df.loc[list(senior_df.index), 'job_position_category'] = 'senior'
cleansed_df.loc[list(assistent_df.index), 'job_position_category'] = 'assistent'
cleansed_df.loc[list(head_df.index), 'job_position_category'] = 'head/main'
cleansed_df.loc[list(director_df.index), 'job_position_category'] = 'director/manager'
cleansed_df.loc[list(expert_df.index), 'job_position_category'] = 'expert'
cleansed_df.loc[list(mid_df.index), 'job_position_category'] = 'mid'


# DETERMINING THE FIELD OF THE JOB

vet_df = (
    cleansed_df[
        cleansed_df['job_title'].str.contains('weteryn.+', regex=True, case=False)
    ]
[['job_title']]
)
IT_n_maths_df = (
    cleansed_df[
        cleansed_df['job_title'].str.contains('.nformaty.+|IT|program.+|statyst.+|matemat.+|anali.+', regex=True, case=True)
    ]
    [['job_title']]
)
# Note: 'veterinary inspector' or 'pharmacy inspector' are categorized as 'vet' and 'pharmacy/chemistry', respectively.
law_df = (
    cleansed_df[
        (cleansed_df['job_title'].str.contains(
            'radca|prawnik|kontroler|skarb.+|prawny|wizytator|aplikant|oskarżyciel|aplikant|referendarz|podreferendarz|księgow.+|inspektor',
            regex=True, case=False)==True) &
        (cleansed_df['job_title'].str.contains('weteryn.+|farmac.+|aptek.+|lecznic.+|laborator.+', regex=True, case=False)==False)
    ]
    [['job_title']]
)
pharmacy_n_chemistry_df = (
    cleansed_df[
        cleansed_df['job_title'].str.contains('farmac.+|aptek.+|lecznic.+|laborator.+', regex=True, case=False)
    ]
    [['job_title']]
)
# Bossman, captain, port, etc.
water_df = (
    cleansed_df[
        cleansed_df['job_title'].str.contains('bossman.+|kapitan|bosman.+|port|wybrzeż.+', regex=True, case=False)
    ]
    [['job_title']]
)
tech_n_construction_df = (
    cleansed_df[
        cleansed_df['job_title'].str.contains('technik|techniczny|górni.+|budowl.+', regex=True, case=False)
    ]
    [['job_title']]
)
documents_df = (
    cleansed_df[
        (cleansed_df['job_title'].str.contains('referent|legalizator|archiwista', case=False)==True) &
        (cleansed_df['job_title'].str.contains('.nformaty.+|IT|program.+|statyst.+|matemat.+|anali.+', regex=True, case=False)==False)
    ]
    [['job_title']]
)
# Manager-like job positions that haven't been categorized in any of the previous fields.
manager_df = (
    cleansed_df[
        (cleansed_df['job_title'].str.contains(r'kierownik|dyrektor|naczelnik.+', regex=True, case=False)==True) &
        (cleansed_df['job_title'].str.contains('weteryn.+|informat.+|port.+|techni.+|górni.+|budowl.+', regex=True, case=False)==False)
    ]
    [['job_title']]
)


# Indices of all obtained matches from the above criteria stored in one list.
job_field_indexes = (
        list(documents_df.index) + list(tech_n_construction_df.index) + list(water_df.index) + list(pharmacy_n_chemistry_df.index) +
        list(manager_df.index) + list(law_df.index) + list(IT_n_maths_df.index) + list(vet_df.index)
)

# Fields that haven't been categorized by the above criteria.
left_job_fields_df = cleansed_df[~cleansed_df.index.isin(job_field_indexes)]


# Most of the fields can be categorized simply by the 'job_title' column, however,
# without including the department name in the 'work_place2' or 'institution' columns,
# around 30% of ads are left without a specific category.

# Browsing through ads that haven't been categorized, to avoid double categorization.
environment_protection_df = (
    left_job_fields_df[
        (cleansed_df['institution'].str.contains('środowisk.+|leśn.+|las.+|roślin.+|nasiennictwa', regex=True, case=False))|
        (cleansed_df['work_place2'].str.contains('środowisk.+|leśn.+|las.+|roślin.+|nasiennictwa', regex=True, case=False))
    ]
)
# Working for the following entities: police, firefighters, military, border guards.
uniformed_services_df = (
    left_job_fields_df[
        (cleansed_df['institution'].str.contains('polic.+|straż.+|wojsk.+|żołnier.+', regex=True, case=False))|
        (cleansed_df['work_place2'].str.contains('polic.+|straż.+|wojsk.+|żołnier.+', regex=True, case=False))
    ]
)
uncategorized_med_df = (
    left_job_fields_df[
        (cleansed_df['institution'].str.contains('med.+|farmaceu.+|chemi.+|sanitar.+', regex=True, case=False))|
        (cleansed_df['work_place2'].str.contains('med.+|farmaceu.+|chemi.+|sanitar.+', regex=True, case=False))
    ]
)
uncategorized_tech_n_construction_df = (
    left_job_fields_df[
        (cleansed_df['institution'].str.contains('budowl.+|górni.+|techn.+|drog.+|dróg|autostrad.+|infrastruk.+', regex=True, case=False))|
        (cleansed_df['work_place2'].str.contains('budowl.+|górni.+|techn.+|drog.+|dróg|autostrad.+|infrastruk.+', regex=True, case=False))
    ]
)
uncategorized_IT_n_statistics_df = (
    left_job_fields_df[
        (cleansed_df['institution'].str.contains('informat.+|architektury danych|statyst.+|analiz.+', regex=True, case=False)==True)|
        (cleansed_df['work_place2'].str.contains('informat.+|architektury danych|statyst.+|analiz.+', regex=True, case=False)==True)&
        (cleansed_df['work_place2'].str.contains('teleinfromatyk.+', regex=True, case=False)==False)
        # ^some jobs at the ICT department are not associated with IT at all.
    ]
)
uncategorized_law_df = (
    left_job_fields_df[
        (cleansed_df['institution'].str.contains('prawn.+|księgow.+', regex=True, case=False))|
        (cleansed_df['work_place2'].str.contains('prawn.+|księgow.+', regex=True, case=False))
    ]
)
uncategorized_water_df = (
    left_job_fields_df[
        (cleansed_df['institution'].str.contains('morsk.+', regex=True, case=False))|
        (cleansed_df['work_place2'].str.contains('morsk.+', regex=True, case=False))
    ]
)
uncategorized_vet_df = (
    left_job_fields_df[
        (cleansed_df['institution'].str.contains('weteryn.+', regex=True, case=False))|
        (cleansed_df['work_place2'].str.contains('weteryn.+', regex=True, case=False))
    ]
)

# Indices of ads that are still left without a category.
# They are going to have 'other' category assigned.
newly_categorized_ads = (
    list(uncategorized_law_df.index) + list(uncategorized_IT_n_statistics_df.index) + list(uncategorized_tech_n_construction_df.index) + list(uncategorized_med_df.index) +
    list(uniformed_services_df.index) + list(uncategorized_law_df.index) + list(environment_protection_df.index) + list(uncategorized_water_df) + list(uncategorized_vet_df.index)
)
other_job_fields_df = left_job_fields_df[~left_job_fields_df.index.isin(newly_categorized_ads)]

# Again, it is undesired to drop the job_title column, so I'm creating a new one.
cleansed_df["job_field"] = cleansed_df["job_title"]
cleansed_df.loc[list(documents_df.index), 'job_field'] = 'documents'
cleansed_df.loc[list(tech_n_construction_df.index), 'job_field'] = 'tech/construction'
cleansed_df.loc[list(uncategorized_tech_n_construction_df.index), 'job_field'] = 'tech/construction'
cleansed_df.loc[list(water_df.index), 'job_field'] = 'water'
cleansed_df.loc[list(uncategorized_water_df.index), 'job_field'] = 'water'
cleansed_df.loc[list(pharmacy_n_chemistry_df.index), 'job_field'] = 'pharmacy/chemistry'
cleansed_df.loc[list(uncategorized_med_df.index), 'job_field'] = 'pharmacy/chemistry'
cleansed_df.loc[list(manager_df.index), 'job_field'] = 'other_manager'
cleansed_df.loc[list(law_df.index), 'job_field'] = 'law'
cleansed_df.loc[list(uncategorized_law_df.index), 'job_field'] = 'law'
cleansed_df.loc[list(IT_n_maths_df.index), 'job_field'] = 'IT/statistics'
cleansed_df.loc[list(uncategorized_IT_n_statistics_df.index), 'job_field'] = 'IT/statistics'
cleansed_df.loc[list(vet_df.index), 'job_field'] = 'vet'
cleansed_df.loc[list(uncategorized_vet_df.index), 'job_field'] = 'vet'
cleansed_df.loc[list(environment_protection_df.index), 'job_field'] = 'environment'
cleansed_df.loc[list(uniformed_services_df.index), 'job_field'] = 'uniformed services'
cleansed_df.loc[list(other_job_fields_df.index), 'job_field'] = 'other'


# FORMATTING
# Dropping unnecessary columns.
cleansed_df.drop(columns=['result2', 'date_documents', 'date_result', 'date_valid'], inplace=True)

# Reindexing and renaming columns so that the order is more intuitive.
cleansed_df = cleansed_df.reindex(columns=['job_id', 'result1', 'job_field', 'job_position_category', 'job_title', 'education', 'work_time', 'vacancies', 'salary', 'city', 'institution', 'work_place1', 'work_place2', 'address', 'responsibilities', 'requirements1', 'requirements2', 'date_announced', 'views'])

cleansed_df.rename({
    'job_id': 'ad_id', 'result1': 'result', 'job_field': 'job_field', 'job_position_category': 'position_category',
    'job_title': 'position', 'education': 'education_level', 'work_time': 'work_time', 'vacancies': 'vacancies',
    'salary': 'salary', 'city': 'city', 'institution': 'institution', 'address': 'institution_address',
    'work_place1': 'workplace', 'work_place2': 'department', 'responsibilities': 'responsibilities',
    'requirements1': 'requirements', 'requirements2': 'nice_to_have', 'date_announced': 'date_announced', 'views': 'views'
}, axis='columns', inplace=True)

path = os.getcwd()[0:-11] + 'Cleansed_data\\Cleaned_2\\'
cleansed_df.to_csv(path + 'cleaned_data.csv', index=False)