# 2024-mgr-sluzba-cywilna
The project was a part of the authors' (Konrad Wasiak, Manuela Walczak) masters' thesis. The final goal was to dwell into results of the recruitment process in Polish civil service and explain, why some entities are able to staff more vacancies.
The answers to these question, alongside other key findings, are introduced in the paper.
<p>
One other crucial outcome of our work was creating the dataset for future research that can be found here:
https://doi.org/10.18150/Q23MGT

The dataset contains cleansed and merged data from: KPRM's website with job offers (web-scraped by Marcin Kostka), regional data from Polish districts taken from Bank Danych Lokalnych, and data describing individual institutions, which has been sent to us by KPRM.
</p>
Keywords: explainable AI, civil service, vacancies, civil service, Poland, statistics, DALEX

Strucutre of the repository:
1. Initial data cleansing: loading the data downloaded from the KPRM website and its initial
processing (Author: Konrad Wasiak).
2. Further data cleansing: the bulk of the data cleansing process is done in this notebook.
data cleansing. It also follows the categorization of data and isolation of succes and failures (Author: Konrad Wasiak).
3. KPRM data merge: merging the data sent to us by the KPRM into a single source (Author:
Manuela Walczak).
4. TERYT: obtaining county and province codes from the BDL for existing data
(Author: Manuela Walczak).
5. Main and KPRM data merge: merging merged additional data with data from
website (Author: Konrad Wasiak).
6. Maps: spatial visualizations (Author: Konrad Wasiak).
7. BDL merge: merging master data with data from the Bank of Local Data
(Author: Konrad Wasiak).
8. Feature engineering: as the name suggests, the feature engineering process is included here, but not
only. It is in this notebook that you will find most of the visualizations included in the paper, as well as
a machine learning model that examines the validity of features, which is described in the
fourth chapter (Author: Konrad Wasiak (with the exception of additional visualizations at the end of the
file by Manuela Walczak).
9. Run all files script: a standard Python script, running all the
notepads mentioned above in the order given, in order to replicate the results achieved. The results are reproducible - any non-deterministic algorithms use a random seed (Author: Konrad Wasiak).
