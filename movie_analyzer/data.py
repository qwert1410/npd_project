import numpy as np
import pandas as pd

mapping = {
    'US':'EN',
    'GB':'EN',
    'CA':'EN',
    'NZ':'EN',
    'AU':'EN',
    'IE':'EN',
    'ZA':'EN',
    'IN':'EN',
    'ES':'ES',
    'MX':'ES',
    'EC':'ES',
    'CL':'ES',
    'AR':'ES',
    'PE':'ES',
    'BR':'PT',
    'PT':'PT',
    'DE':'DE',
    'AT':'DE',
    'CH':'DE',
}
mapping_countries = {
    'EN':'International English',
    'ES':'International Spanish',
    'PT':'International Portuguese',
    'DE':'International German',
}
def get_data(path, type, index_col=None, name=''):
    if type == 'imdb':
        try:
            data = pd.read_csv(path, index_col=index_col, sep='\t')
            return data
        except FileNotFoundError:
            print(f"The file {name} was not found. Please check the file")
        except pd.errors.ParserError:
            print(f"The file {name} is not in the correct CSV format.")
        except pd.errors.EmptyDataError:
            print(f"The file {name} is empty. Please provide a valid CSV file.")
        except Exception as e:
            print(f"An unexpected error occurred while getting file {name}: {e}")
    if type == 'world_bank':
        try:
            data = pd.read_csv(path, skiprows=3, sep=',')
            return data
        except FileNotFoundError:
            print(f"The file {name} was not found. Please check the file")
        except pd.errors.ParserError:
            print(f"The file {name} is not in the correct CSV format.")
        except pd.errors.EmptyDataError:
            print(f"The file {name} is empty. Please provide a valid CSV file.")
        except Exception as e:
            print(f"An unexpected error occurred while getting file {name}: {e}")

class Data():
    def __init__(self, titles_akas_path, gdp_path, population_path, mapping_path, ratings_path, basics_path, start_year, end_year, world=True):
        self.titles_akas_path = titles_akas_path
        self.gdp_path = gdp_path
        self.population_path = population_path
        self.mapping_path = mapping_path
        self.ratings_path = ratings_path
        self.basics_path = basics_path
        self.start_year = start_year
        self.end_year = end_year
        self.include_world = world

        if self.end_year < self.start_year:
            print(f'End date smaller than start date. Performing analysis for {start_year} only.')
            self.end_year = self.start_year
    def get_region(self):
        titles = get_data(self.titles_akas_path, 'imdb', 'titleId', 'titles.akas')
        titles = titles.replace({'\\N':np.NaN})
        titles_og = titles.loc[titles.isOriginalTitle == 1, 'title'].sort_values()
        titles.region = titles.region.replace(mapping)
        titles = titles.drop_duplicates(keep='first')
        titles_og = titles.loc[
            titles.title.isin(titles_og) & 
            (titles.isOriginalTitle==0) &
            (~titles.region.isna())
            ].groupby('titleId').agg(['nunique', 'last'])
        
        self.lost_region_count = len(titles_og.loc[titles_og['region']['nunique']!=1, 'region'][['last']])
        self.lost_region = titles.loc[titles.index.isin(titles_og.loc[titles_og['region']['nunique']!=1].index)].copy()
        international_titles = self.lost_region.loc[lambda x: x['isOriginalTitle'] == 1].copy()
        international_titles['region'] = 'WD'

        titles_x_country = titles_og.loc[titles_og['region']['nunique']==1, 'region'][['last']]
        titles_x_country.columns = ['region']
        if self.include_world:
            titles_x_country = pd.concat([titles_x_country, international_titles[['region']]])
        self.region = titles_x_country

    def get_titles_wo_region(self):
        if not hasattr(self, 'lost_region'):
            print('No data loaded. Transforming the data first.')
            self.get_region()
        print(f'The region for {self.lost_region_count} movies not found. To check manually these titles check self.lost_region')
        print(self.lost_region.head())

    def get_macro(self, year='2022'):
        gdp = get_data(self.gdp_path, 'world_bank')
        population = get_data(self.population_path, 'world_bank')

        if (len(gdp.filter(like=year).columns) == 0) or (len(population.filter(like=year).columns) == 0):
            print(f'There is no data for year {year}.')
            return -1
        
        gdp = gdp[['Country Code', 'Country Name', year]]
        gdp.columns = ['country_id', 'regionName', 'gdp']
        gdp = gdp.set_index('country_id')

        population = population[['Country Code', 'Country Name', year]]
        population.columns = ['country_id', 'regionName', 'population']
        population = population.set_index('country_id')
        macro_data = gdp.join(population[['population']])
        code_mapping = pd.read_csv(self.mapping_path, index_col='alpha-3')
        code_mapping.loc['WLD'] = 'WD'
        macro_data = macro_data.join(code_mapping[['alpha-2']])
        macro_data['alpha-2'] = macro_data['alpha-2'].replace(mapping)
        macro_data['regionName'] = macro_data.apply(lambda row: mapping_countries.get(row['alpha-2'], row['regionName']), axis=1)
        macro_data = macro_data.groupby('alpha-2').agg({'gdp':'sum', 'population':'sum', 'regionName':'first'})
        macro_data['gdp_pc'] = macro_data['gdp'] / macro_data['population']
        self.macro_data = macro_data

        return self.macro_data

    def join_data(self):
        if not hasattr(self, 'region'):
            print('No region data loaded. Transforming the data first.')
            self.get_region()
        if not hasattr(self, 'macro_data'):
            print('No macro data loaded. Transforming the data first.')
            self.get_macro()
        ratings = get_data(self.ratings_path, 'imdb', 'tconst', 'title.ratings')
        basics = get_data(self.basics_path, 'imdb', 'tconst', 'title.basics')
        basics['startYear'] = pd.to_numeric(basics['startYear'], errors='coerce')

        self.titles = self.region.join([ratings, basics], how='left')

        self.titles = pd.merge(self.titles, self.macro_data, left_on='region', right_index=True, how='left')
        self.titles = self.titles.replace({'\\N':np.NaN})
        self.titles = self.titles.dropna(subset=['startYear']).loc[lambda x: (x['startYear'] >= self.start_year) & (x['startYear'] <= self.end_year)].copy()
        return self.titles
    
    def get_crew(self):
        pass




