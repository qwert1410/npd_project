import argparse
import numpy as np
import pandas as pd
from data import Data  # Assuming this is a custom module you've created
import matplotlib.pyplot as plt
from IPython.display import display, HTML

def main(args):
    test = Data(
        args.titles_akas,
        args.gdp,
        args.population,
        args.mapping,
        args.title_ratings,
        args.title_basics,
        args.start_year,
        args.end_year,
        args.world,
    )

    test.get_region()
    test.get_macro()
    test.join_data()

    # Task 1
    best_movies_5 = test.titles.loc[lambda x: 
                    (x['numVotes'] > 10_000) & 
                    (x['titleType'].isin(['movie']))
                    ].groupby('regionName')['averageRating'].apply(lambda x: x.nlargest(5).mean()).sort_values()
    best_movies_10 = test.titles.loc[lambda x: 
                    (x['numVotes'] > 10_000) & 
                    (x['titleType'].isin(['movie']))
                    ].groupby('regionName')['averageRating'].apply(lambda x: x.nlargest(10).mean()).sort_values()
    best_movies_20 = test.titles.loc[lambda x: 
                    (x['numVotes'] > 10_000) & 
                    (x['titleType'].isin(['movie']))
                    ].groupby('regionName')['averageRating'].apply(lambda x: x.nlargest(20).mean()).sort_values()
    
    # Task 2
    ranking = test.titles.groupby('regionName').agg({'gdp':'mean', 'population':'mean', 'gdp_pc':'mean', 'numVotes':'sum'})
    ranking = ranking.join(best_movies_5).dropna()
    ranking = ranking.rank(ascending=False) 

    ranking['weak_impact_gdp'] = ranking['numVotes'] - ranking['gdp']
    ranking['weak_impact_population'] = ranking['numVotes'] - ranking['population']
    ranking['weak_impact_gdp_pc'] = ranking['numVotes'] - ranking['gdp_pc']

    ranking['strong_impact_gdp'] = ranking['averageRating'] - ranking['gdp']
    ranking['strong_impact_population'] = ranking['averageRating'] - ranking['population']
    ranking['strong_impact_gdp_pc'] = ranking['averageRating'] - ranking['gdp_pc']

    # Task 3
    polish_movies = test.titles.loc[lambda x: (x['regionName'] == 'Poland') & (x['titleType'] == 'movie') & (x['numVotes'] > 3_000)].copy()
    polish_comedies = polish_movies.dropna(subset=['genres'])
    polish_comedies = polish_comedies.loc[polish_comedies.genres.str.contains('Comedy')].copy()

    fig, axes = plt.subplots(2, 1, figsize=(10, 6))

    if len(polish_movies) > 0:
        (polish_movies.groupby('startYear')[['averageRating']]
        .agg([lambda x: x.nlargest(5).mean()])
        .plot(ax=axes[0], title='Average rating of five best movies from each year', legend=False)).set_xlabel('Year')
    else:
        axes[0].text(0.5, 0.5, 'No data', fontsize=20, ha='center')
        axes[0].set_title('Average rating of five best movies from each year')
    if len(polish_comedies) > 0:
        (polish_comedies.groupby('startYear')[['averageRating']]
        .agg([lambda x: x.mean()])
        .plot(ax=axes[1], title='Average rating of comedies from each year', legend=False)).set_xlabel('Year')
    else:
        axes[1].text(0.5, 0.5, 'No data', fontsize=20, ha='center')
        axes[1].set_title('Average rating of five best comedies from each year')

    plt.tight_layout()
    plt.savefig('polish_movies_analysis.png')
    plt.close()

    html_output = f"""
    <h1>Assumptions used for the analysis</h1>
    <p>
        Certain countries are joined as regions. These are English speaking region, Spanish speaking region,
        German speaking region, Portuguese speaking region. 
        If for some movie, the country of origin was not to be found, it was categorised as international production. 
        If you do not want to see this region in analysis, use flag --world=False.
    </p>

    <h1>Best Movies by Region</h1>

    <h2>Top 5 movies from each region<h2>
    {best_movies_5.tail(20).to_frame().round(2).to_html()}
    <h2>Top 10 movies from each region<h2>
    {best_movies_10.tail(20).to_frame().round(2).to_html()}
    <h2>Top 20 movies from each region<h2>
    {best_movies_20.tail(20).to_frame().round(2).to_html()}
    
    <h1>Best Movie Makers by Weak Impact</h1>
    <h2>Vs GDP<h2>
    {ranking.sort_values('weak_impact_gdp')[-5:][['weak_impact_gdp']].round(2).to_html()}
    <h2>Vs Population<h2>
    {ranking.sort_values('weak_impact_population')[-5:][['weak_impact_population']].to_html()}
    <h2>Vs GDP per capita<h2>
    {ranking.sort_values('weak_impact_gdp_pc')[-5:][['weak_impact_gdp_pc']].to_html()}
    
    <h1>Best Movie Makers by Strong Impact</h1>
    <h2>Vs GDP<h2>
    {ranking.sort_values('strong_impact_gdp')[-5:][['strong_impact_gdp']].to_html()}
    <h2>Vs Population<h2>
    {ranking.sort_values('strong_impact_population')[-5:][['strong_impact_population']].to_html()}
    <h2>Vs GDP per capita<h2>
    {ranking.sort_values('strong_impact_gdp')[-5:][['strong_impact_gdp_pc']].to_html()}

    <h1>Polish Movies Analysis</h1>
    <img src="polish_movies_analysis.png" alt="Polish Movies Analysis">
    """
    try:
        with open('results.html', 'w') as f:
            f.write(html_output)
        print('The results have been saved successfully. You can find them as results.html. The plots are saved as polish_movies_analysis.png')
    except Exception as e:
        print(f'Issues while saving to html: {e}')
    
    view_results = input('Do you want to view the results in the command line? (Y/N)')
    if view_results.upper() == 'Y':
        print('Best regions by top 5, 10, 20 movies')
        display(best_movies_5.tail(20).to_frame().round(2))
        display(best_movies_10.tail(20).to_frame().round(2))
        display(best_movies_20.tail(20).to_frame().round(2))
        print('Countries with the strongest weak impact vs gdp, population, gdp per capita')
        display(ranking.sort_values('weak_impact_gdp')[-5:][['weak_impact_gdp']].round(2))
        display(ranking.sort_values('weak_impact_population')[-5:][['weak_impact_population']].round(2))
        display(ranking.sort_values('weak_impact_gdp_pc')[-5:][['weak_impact_gdp_pc']].round(2))
        print('Countries with the strongest strong impact vs gdp, population, gdp per capita')
        display(ranking.sort_values('strong_impact_gdp')[-5:][['strong_impact_gdp']].round(2))
        display(ranking.sort_values('strong_impact_population')[-5:][['strong_impact_population']].round(2))
        display(ranking.sort_values('strong_impact_gdp_pc')[-5:][['strong_impact_gdp_pc']].round(2))
        
        fig, axes = plt.subplots(2, 1, figsize=(10, 6))

        if len(polish_movies) > 0:
            (polish_movies.groupby('startYear')[['averageRating']]
            .agg([lambda x: x.nlargest(5).mean()])
            .plot(ax=axes[0], title='Average rating of five best movies from each year'))
        else:
            axes[0].text(0.5, 0.5, 'No data', fontsize=20, ha='center')
            axes[0].set_title('Average rating of five best movies from each year')
        if len(polish_comedies) > 0:
            (polish_comedies.groupby('startYear')[['averageRating']]
            .agg([lambda x: x.mean()])
            .plot(ax=axes[1], title='Average rating of comedies from each year'))
        else:
            axes[1].text(0.5, 0.5, 'No data', fontsize=20, ha='center')
            axes[1].set_title('Average rating of five best comedies from each year')

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze movie data")
    parser.add_argument('--titles_akas', type=str, required=True, help='Path to title.akas.tsv')
    parser.add_argument('--title_ratings', type=str, required=True, help='Path to title.ratings.tsv')
    parser.add_argument('--title_basics', type=str, required=True, help='Path to title.basics.tsv')
    parser.add_argument('--start_year', type=int, required=True, help='Starting year')
    parser.add_argument('--end_year', type=int, required=True, help='Ending year')
    parser.add_argument('--gdp', type=str, default='World_Bank_Data/gdp.csv', help='Path to gdp file')
    parser.add_argument('--population', type=str, default='World_Bank_Data/population.csv', help='Path to population file')
    parser.add_argument('--mapping', type=str, default='World_Bank_Data/code_mapping.csv', help='Path to mapping')
    parser.add_argument('--world', type=bool, default=True, help='Flag for including world region')

    args = parser.parse_args()
    main(args)
