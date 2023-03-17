# About this repository

This repository contains Python code that can be used to process data on climate policies from the [Climate Policy Database](https://climatepolicydatabase.org/) for further statistical analysis.

The code assigns every policy in the original dataset one or several of certain instrument types and sectors. The instrument types follow the IEA classification. The sectors correspond to the sectors used in IPCC reports. The script also applies policies of the European Union to individual member countries. Furthermore, it identifies policies that are categorised as carbon pricing policies (carbon taxes and ETS) by the World Bank as provided with the [Carbon Pricing Dashboard](https://carbonpricingdashboard.worldbank.org/). The code also transforms the data into different formats that can be used more easily for statistical analysis.

The code was originally produced for the academic journal article [Policy sequencing towards carbon pricing among the world's largest emitters](https://www.nature.com/articles/s41558-022-01538-8) by Manuel Linsenmeier, Adil Mohommad, and Gregor Schwerhoff, which was published in the journal Nature Climate Change in 2022. Please cite this article when you use this code as a reference.

For background on the original policy data, please see the academic journal article [Twenty years of climate policy: G20 coverage and gaps](https://doi.org/10.1080/14693062.2021.1993776) by Leonardo Nascimento, Takeshi Kuramochi, Gabriela Iacobuta, Michel den Elzen, Hanna Fekete, Marie Weishaupt, Heleen Laura van Soest, Mark Roelfsema, Gustavo De Vivero-Serrano, Swithin Lui, Frederic Hans, Maria Jose de Villafranca Casas, and Niklas Höhne.

# Content

The repository contains two folders, [input](input) and [output](output). The folder input contains several files that can be changed by the user for their purposes.
- The file `climatepolicies_additional.csv` contains a list of climate policies that are missing in the original dataset and are merged into the database.
- The file `operationalisation_instruments.csv` contains three columns with instrument types. The first column contains the categories used in the original dataset. The second column contains new categories that are assigned by the script. The third column contains subcategories for some of the categories that will also be assigned by the script.-
The file `operationalisation_sectors.csv` contains two columns with sectors which correspond to the first two columns of the previous file, just for sectors instead of instrument types.-
The file `carbon_pricing.csv` is based on data that can be downloaded from the Carbon Pricing Dashboard of the World Bank and contains Policy IDs that match an existing policy either in the original policy data or in the file `climatepolicies_additional.csv`. The file also includes the instrument type (i.e. carbon tax or ETS). The script currently only matches carbon pricing policies among the G20 economies and a few selected large emitters for which the policy data is relatively complete.

# Usage

The code requires the user to download the original data from the Climate Policy Database and deposit it as a csv file with the name `climate_policy_database_policies_export.csv` in the folder [input](input). The data can be downloaded as bulk on [https://climatepolicydatabase.org/policies](https://climatepolicydatabase.org/policies) at the bottom of the page by clicking on the button Download Policies. Once the file is deposited in the [input](/input) folder, the user can then run the script `p_prepare_data_policies.py` which will produce three new files in the folder [output](output) than contain the policy data in different formats.

Note that for the correct identification of carbon pricing policies, the two files `climatepolicies_additional.csv` and `carbon_pricing.csv` might need to be updated. For example, the script currently only matches carbon pricing policies among the G20 economies and a few selected large emitters for which the policy data is relatively complete. This can be updated by matching the carbon pricing policies in the file `carbon_pricing.csv` with existing policies in the original policy data or in the file `climatepolicies_additional.csv` using the Policy ID columns.

Also note that the script currently first filters the original data and keeps only policies at the supranational (EU) or national level and only policies that include mitigation as an objective.

# Requirements

The code requires Python 3 and the following packages:
- os
- sys
- numpy
- pandas

# License

The code is provided with a [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license.

