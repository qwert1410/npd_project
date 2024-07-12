import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
from data import Data, get_data

class TestDataMethods(unittest.TestCase):

    def setUp(self):
        self.titles_akas_path = 'Data_test/titles.akas.csv'
        self.gdp_path = 'Data_test/gdp.csv'
        self.population_path = 'Data_test/population.csv'
        self.mapping_path = 'Data_test/code_mapping.csv'
        self.ratings_path = 'Data_test/title.ratings.csv'
        self.basics_path = 'Data_test/title.basics.csv'
        self.start_date = 1900,
        self.end_date = 2022,
        
        self.data = Data(
            self.titles_akas_path,
            self.gdp_path,
            self.population_path,
            self.mapping_path,
            self.ratings_path,
            self.basics_path,
            self.start_date,
            self.end_date,
        )

    @patch('pandas.read_csv')
    def test_get_data_success(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        result = get_data('dummy_path', 'imdb')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)

    @patch('pandas.read_csv')
    def test_get_region(self, mock_read_csv):
        mock_read_csv.side_effect = [
            pd.DataFrame({
                'titleId': ['1', '1', '1', '2', '2', '2', '3', '3', '3'],
                'isOriginalTitle': [1, 0, 0, 1, 0, 0, 1, 0, 0],
                'region': ['\\N', 'GB', 'AU', '\\N', 'PL', 'DE', '\\N', 'PL', 'DE'],
                'title': ['Title1', 'Title1', 'Title1', 'Title2', 'Title2_2', 'Title2', 'Title3', 'Title3', 'Title3']
            }).set_index('titleId')
        ]
        
        self.data.get_region()
        self.assertTrue(hasattr(self.data, 'region'))
        self.assertEqual(len(self.data.region), 3)
        self.assertEqual(self.data.region['region'].tolist(), ['EN', 'DE', 'WD'])


    @patch('pandas.read_csv')
    def test_get_macro(self, mock_read_csv):
        mock_read_csv.side_effect = [
            pd.DataFrame({
                'Country Name': ['United States', 'United Kingdom', 'Poland'],
                'Country Code': ['USA', 'UKA', 'POL'],
                '2022': [1000, 500, 60]
            }),
            pd.DataFrame({
                'Country Name': ['United States', 'United Kingdom', 'Poland'],
                'Country Code': ['USA', 'UKA', 'POL'],
                '2022': [300, 60, 40]
            }),
            pd.DataFrame({
                'name': ['United States', 'United Kingdom', 'Poland'],
                'alpha-3': ['USA', 'UKA', 'POL'],
                'alpha-2': ['US', 'GB', 'PL'],
            }).set_index('alpha-3')
        ]
        result = self.data.get_macro(year='2022')

        self.assertTrue(hasattr(self.data, 'macro_data'))
        self.assertEqual(result.loc['EN', 'gdp'], 1500)
        self.assertEqual(result.loc['PL', 'population'], 40)

    @patch('pandas.read_csv')
    def test_join_data(self, mock_read_csv):
        mock_read_csv.side_effect = [
            pd.DataFrame({
                'titleId': ['1', '1', '1', '2', '2', '2', '3', '3', '3'],
                'isOriginalTitle': [1, 0, 0, 1, 0, 0, 1, 0, 0],
                'region': ['\\N', 'GB', 'AU', '\\N', 'PL', 'DE', '\\N', 'PL', 'DE'],
                'title': ['Title1', 'Title1', 'Title1', 'Title2', 'Title2_2', 'Title2', 'Title3', 'Title3', 'Title3']
            }).set_index('titleId'),
            pd.DataFrame({
                'Country Name': ['United States', 'United Kingdom', 'Poland', 'Germany', 'World'],
                'Country Code': ['USA', 'UKA', 'POL', 'DEU', 'WLD'],
                '2022': [1000, 500, 60, 120, 3000]
            }),
            pd.DataFrame({
                'Country Name': ['United States', 'United Kingdom', 'Poland', 'Germany', 'World'],
                'Country Code': ['USA', 'UKA', 'POL', 'DEU', 'WLD'],
                '2022': [300, 60, 40, 80, 7000]
            }),
            pd.DataFrame({
                'name': ['United States', 'United Kingdom', 'Poland', 'Germany', 'World'],
                'alpha-3': ['USA', 'UKA', 'POL', 'DEU', 'WLD'],
                'alpha-2': ['US', 'GB', 'PL', 'DE', 'WD'],
            }).set_index('alpha-3'),
            pd.DataFrame({
                'tconst': ['1', '2', '3'],
                'averageRating': [8.0, 7.0, 6.0],
                'numVotes': [1000, 500, 2000]
            }).set_index('tconst'),
            pd.DataFrame({
                'tconst': ['1', '2', '3'],
                'titleType': ['movie', 'movie', 'short'],
                'startYear': [2000, 2010, 2020]
            }).set_index('tconst')
        ]
        
        result = self.data.join_data()
        self.assertTrue(hasattr(self.data, 'titles'))
        self.assertEqual(len(self.data.titles), 3)
        self.assertEqual(self.data.titles.regionName.tolist(), ['International English', 'International German', 'World'])
        self.assertEqual(len(self.data.titles), 3)

if __name__ == '__main__':
    unittest.main()
