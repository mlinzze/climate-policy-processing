#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

import numpy as np
import pandas as pd

## ============================================================
## read in the data and drop duplicate entries
## ============================================================

df = pd.read_csv('./input/climate_policy_database_policies_export.csv')
df = df.loc[~df.duplicated(subset=['Policy ID', 'Country ISO', 'Policy name'], keep='first'), :]

## ============================================================
## add missing policies
## these are carbon pricing policies not included in the climate policy database
## ============================================================

df_additional = pd.read_csv('./input/climatepolicies_additional.csv', sep=';')
df = pd.concat([df, df_additional], ignore_index=True)

## ============================================================
## fill in some missing information
## ============================================================

df.loc[df['Policy ID'] == 4330., 'Type of policy instrument'] = 'Grants and subsidies, Direct investment' # https://www.iea.org/policies/2644-movea-planpromotion-of-alternative-energy-vehicles
df.loc[df['Policy ID'] == 4882., 'Type of policy instrument'] = 'Grants and subsidies' # https://www.climate-laws.org/geographies/spain/policies/royal-decree-635-2013-developing-the-plan-to-promote-the-environment-in-the-hotel-sector-pima-sol-for-the-energy-renovation-of-its-installations-and-regulating-the-further-acquisition-of-carbon-credits-by-the-carbon-fund-for-a-sustainable-economy
df.loc[df['Policy ID'] == 4882., 'Sector name'] = 'Buildings' # https://www.climate-laws.org/geographies/spain/policies/royal-decree-635-2013-developing-the-plan-to-promote-the-environment-in-the-hotel-sector-pima-sol-for-the-energy-renovation-of-its-installations-and-regulating-the-further-acquisition-of-carbon-credits-by-the-carbon-fund-for-a-sustainable-economy
df.loc[df['Policy ID'] == 4839., 'Sector name'] = 'Electricity and heat' # data
df.loc[df['Policy ID'] == 4851., 'Sector name'] = 'Electricity and heat' # https://www.iea.org/policies/6379-resolution-on-further-development-of-renewable-energy-and-energy-efficiency-2017-2025
df.loc[df['Policy ID'] == 3888., 'Sector name'] = 'Industry' # https://www.iea.org/policies/2384-fnee-aid-programme-for-desalination-plants
df.loc[df['Policy ID'] == 3528., 'Sector name'] = 'Electricity and heat, Industry, Transport, Buildings' # https://www.edf.org/sites/default/files/EDF_IETA_Switzerland_Case_Study_May_2013.pdf

## ============================================================
## drop policies without information on sector or type of policy (if any remaining)
## ============================================================

df = df.loc[~(df['Type of policy instrument'].isnull() | df['Sector name'].isnull()), :]

## ============================================================
## add new binary column for every instrument type
## the names of these columns start with "IT" for easier filtering/sorting
## ============================================================

## read in information on assignment of instruments to types
coding_instruments = pd.read_csv('./input/operationalisation_instruments.csv', sep=',')

# replace some level 1 with level 2 instrument types
indices = (coding_instruments.iloc[:, 2].notnull())

coding_instruments.loc[indices, 'IEA category'] = coding_instruments.loc[indices, 'IEA subcategory'].values
type_dict = dict(zip(coding_instruments.iloc[:, 0].values, coding_instruments.iloc[:, 1].values))
type_values = [z for z in list(dict.fromkeys(type_dict.values())) if pd.notnull(z)]

df['types'] = df['Type of policy instrument'].apply(lambda x: x.split(','))
df['types_list'] = df['types'].apply(lambda x: [z for z in [type_dict[t.strip()] for t in list(x)] if pd.notnull(z)])
for instrument_type in type_values:
	df['IT ' + instrument_type] = df['types_list'].apply(lambda x: instrument_type in x)
df = df.drop(columns=['types_list'])

## ============================================================
## add new binary column for carbon pricing
## use information from the carbon pricing dashboard of the World Bank to match with policies
## after this, change name of instrument type "Financial incentives" to "Grants and subsidies"
## because it no longer includes carbon pricing policies
## ============================================================

df_cp = pd.read_csv('./input/carbon_pricing.csv', sep=',')
df_cp = df_cp.loc[df_cp['Policy ID'].notnull(), :]

df_cp['IT Carbon pricing'] = True
df_cp['IT Carbon pricing tax'] = False
df_cp['IT Carbon pricing ets'] = False

df_cp.loc[df_cp['Type of the initiative'] == 'Carbon tax', 'IT Carbon pricing tax'] = True
df_cp.loc[df_cp['Type of the initiative'] == 'ETS', 'IT Carbon pricing ets'] = True

df_cp = df_cp.loc[:, ['Policy ID', 'IT Carbon pricing', 'IT Carbon pricing tax', 'IT Carbon pricing ets']]

df = df.merge(df_cp, on='Policy ID', how='left')

df.loc[df['IT Carbon pricing'] == True, 'IT Financial incentives'] = False
df = df.rename(columns={'IT Financial incentives': 'IT Grants and subsidies'})
df['IT Carbon pricing'] = df['IT Carbon pricing'].fillna(False)
df['IT Carbon pricing tax'] = df['IT Carbon pricing tax'].fillna(False)
df['IT Carbon pricing ets'] = df['IT Carbon pricing ets'].fillna(False)

## ============================================================
## add new binary column for every sector
## the names of these columns start with "SE" for easier filtering/sorting
## ============================================================

coding_sectors = pd.read_csv('./input/operationalisation_sectors.csv', sep=',')
sector_dict = dict(zip(coding_sectors.iloc[:, 0].values, coding_sectors.iloc[:, 1].values))
sector_values = [z for z in list(dict.fromkeys(sector_dict.values())) if pd.notnull(z)]

df['sectors'] = df['Sector name'].apply(lambda x: x.split(','))
df['sectors_list'] = df['sectors'].apply(lambda x: [z for z in [sector_dict[t.strip()] for t in list(x)] if pd.notnull(z)])
for sector in sector_values:
	df['SE ' + sector] = df['sectors_list'].apply(lambda x: sector in x)
df = df.drop(columns=['sectors_list'])

## ============================================================
## select only countries with plausibly complete policy coverage
## G20 and selected other large emitters
## ============================================================

g20 =['ARG', 'AUS', 'BRA', 'CAN', 'CHN', 'DEU', 'EUE', 'FRA', 'GBR', 'IDN', 'IND', 'ITA', 'JPN', 'KOR', 'MEX', 'RUS', 'SAU', 'TUR', 'USA', 'ZAF']
large_emitters = ['CHL', 'COL', 'CHE', 'UKR', 'ESP', 'EGY', 'IRN', 'IRQ', 'KAZ', 'KWT', 'MYS', 'NIG', 'PAK', 'THA', 'ARE', 'UZB', 'VEN', 'VNM']

df = df.loc[df['Country ISO'].isin(g20 + large_emitters), :]

## ============================================================
## add EUE policies to member states
## set year of adoption/implementation as min(year adoption/implementation, year of joining EU)
## after that, drop EUE as a jurisdiction/country
## ============================================================

year_ascension = \
{\
'BEL': 1957, 
'FRA': 1957,
'DEU': 1957, 
'ITA': 1957, 
'LUX': 1957, 
'NLD': 1957,
'DNK': 1973, 
'IRL': 1973,
'GBR': 1973,
'GRC': 1981,
'ESP': 1986,
'PRT': 1986,
'AUT': 1995,
'FIN': 1995,
'SWE': 1995,
'CYP': 2004,
'CZE': 2004,
'EST': 2004,
'HUN': 2004,
'LVA': 2004,
'LTU': 2004,
'MLT': 2004,
'POL': 2004,
'SVK': 2004,
'SVN': 2004,
'BGR': 2007,
'ROU': 2007,
'HRV': 2013
}

df_ascension = pd.DataFrame({'iso': list(year_ascension.keys()), 'year': list(year_ascension.values())})
countries_eu = df_ascension['iso'].unique()
df['EU policy'] = False

for policy in df.loc[df['Country ISO'] == 'EUE', 'Policy ID'].unique():
	new_entry = df.loc[df['Policy ID'] == policy, :]
	year_decision = new_entry['Date of decision'].values[0]
	year_implementation = new_entry['Start date of implementation'].values[0]
	new_entry['EU policy'] = True
	for country in countries_eu:
		new_entry['Country ISO'] = country
		year_ascension = df_ascension.loc[df_ascension['iso'] == country, 'year'].values[0]
		new_entry['Date of decision'] = np.max([year_decision, year_ascension])
		new_entry['Start date of implementation'] = np.max([year_implementation, year_ascension])
		new_entry['Jurisdiction'] = 'Country'
		df = pd.concat([df, new_entry], axis=0, ignore_index=True)

df = df.loc[df['Country ISO'] != 'EUE', :]

## ============================================================
## select only certain policies
## jurisdiction: national (includes now also EU policies, see above)
## policy objectives: include mitigation
## ============================================================

df['national_policy'] = (df['Jurisdiction'] == 'Country')
df['mitigation'] = df['Policy objective'].str.contains('Mitigation')

df = df.loc[df['national_policy'] & df['mitigation'], :]

## ============================================================
## write out the file with rows corresponding to individual policies
## ============================================================

df.to_csv('./output/climate_policy_database_policies_export_policies.csv', index=False)

## ============================================================
## create a new dataframe with new structure that only includes information
## on how many policies with a specific instrument type - sector combination
## were adopted in a specific country in a specific year
## ============================================================

df = pd.read_csv('./output/climate_policy_database_policies_export_policies.csv')

sectors_columns = [col for col in df.columns if col[:2] == 'SE']
instruments_columns = [col for col in df.columns if col[:2] == 'IT']

for col in sectors_columns + instruments_columns:
	df[col] = df[col].astype(int)

df = df.rename(columns={'Date of decision': 'year', 'Country ISO': 'iso'})
instruments_columns_lower = [c.replace('IT ', '').replace(' ', '_').replace(',', '').lower() for c in instruments_columns]
df = df.rename(columns=dict(zip(instruments_columns, instruments_columns_lower)))
sectors_columns_lower = [c.replace('SE ', '').replace(' ', '_').lower() for c in sectors_columns]
df = df.rename(columns=dict(zip(sectors_columns, sectors_columns_lower)))

df['year'] = df['year'].astype(float)

dfz = df.groupby(['iso', 'year'] + instruments_columns_lower + sectors_columns_lower)['Policy ID'].count().reset_index().rename(columns={'Policy ID': 'count'})
dfz = dfz.sort_values(by=['iso', 'year'], ascending=True).reset_index(drop=True)

dfz = dfz.melt(id_vars=['iso', 'year', 'count'] + instruments_columns_lower,
				value_vars=sectors_columns_lower,
				var_name=['sector'],
				value_name='dummy')
dfz = dfz.loc[dfz['dummy'] == 1., :]
dfz.loc[:, instruments_columns_lower] = dfz.loc[:, instruments_columns_lower].multiply(dfz['count'].values, axis=0)
dfz = dfz.drop(columns=['count', 'dummy'])
dfz = dfz.groupby(['iso', 'year', 'sector']).sum().reset_index()
dfz = dfz.sort_values(by=['iso', 'year'], ascending=True).reset_index(drop=True)

countries = dfz['iso'].unique()
years = dfz['year'].unique()
sectors = dfz['sector'].unique()

countries.sort()
years.sort()

dfz = dfz.set_index(['iso', 'year', 'sector'], drop=True)
multi_index = (pd.MultiIndex.from_product(iterables=[countries, years, sectors],
											names=['iso', 'year', 'sector']))
dfz = dfz.reindex(multi_index, fill_value=0.).reset_index()
dfz = dfz.sort_values(by=['iso', 'year'], ascending=True).reset_index(drop=True)

dfz.to_csv('./output/climate_policy_database_policies_export_counts.csv', index=False)

## ============================================================
## create a new dataframe with new structure that only includes information
## on whether a policy with a specific instrument type - sector combination
## had been adopted in a specific country up to the given year
## ============================================================

dfz = pd.read_csv('./output/climate_policy_database_policies_export_counts.csv')

dfz = dfz.sort_values(by=['iso', 'year'], ascending=True).reset_index(drop=True)
for col in instruments_columns_lower:
	dfz[col] = dfz.groupby(['iso', 'sector'])[col].transform(lambda x: x.cumsum() > 0.).astype(int)

dfz.to_csv('./output/climate_policy_database_policies_export_cumulative_binary.csv', index=False)
