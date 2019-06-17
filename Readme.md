# PDE-BIO: Publication Data Extractor for Biological Studies

The main purpose of this script is to assist anyone who is performing data analyses on academic data, meta-analyses, systematic reviews or any other activity that requires amassing high volumes of academic data. It comes to me that there is no ready-to-use solution for article data acquisition. As it is using Pubmed and PMC databases from NCBI, PDE-BIO is an extension over NCBI Entrez API and therefore requires a valid NCBI account and Entrez API key to run.

### Requirements

1. Python 3.5+: https://www.python.org/downloads/
2. Biopython: https://biopython.org/
3. NCBI account with Entrez API key: https://www.ncbi.nlm.nih.gov/account/

### Installation

PDE-BIO is used as a standalone Python module. Simply put **pdebio.py** into your project folder and write

**import pdebio**

in your desired .py file to start using PDE-BIO


### How to use

PDE-BIO has two functions callable by user.

**get_data(term, starting_year, final_year, email,api_key=None,output_file='summary.csv',list_output=False, verbose = False)**

Produces csv file containing amount of articles for term queried split by month in a range from starting_year to final_year. Example of output can be seen in examples/summary.csv and examples/summary.xlsx (post-processed for better readability).

Parameters:

    term: a query to be searched. Follows rules for NCBI queries, so queries like "cancer AND immunology" will produce only articles containing both terms. 
    starting_year: used to create a starting year for the list of dates.
    final_year: used to create a final year for the list of dates.
    email: email for Entrez databaze.
    api_key: optional. NCBI api key. if entered, increases max amount of requests per second from 3 to 10. Highly recommended.
    output_file: name of a file for data to be stored in. default value is 'summary.csv'.
    list_output: if set to True, instead of creating csv file, function returns a list of fetched data.
    verbose: optional. If set to True, function will print the current term and date combination fetched. Reduces speed.

**get_abstracts(email, input_file = 'summary.csv', output_file = 'articles.csv', api_key = None, verbose = False)**

Using file created by get_data(), fetches data (authors, publication date, journal, abstract) for each article found by get_data(). Is a highly time-intensive process. Even with active Entrez API key, fetches 1-5 articles per second. As it is likely that for large datasets you will run get_abstracts() in several runs for one get_data() file, get_abstracts() can continue previous run if interrupted, as long as input and output files aren't changed. Example of output can be seen in examples/articles.csv and examples/articles.xlsx (post-processed for better readability).

Parameters:

	email: email for Entrez databaze.
    input_file: csv file containing fetched data for abstract data fetching. default value is 'summary.csv'.
    output_file: name of a file for data to be stored in. default value is 'articles.csv'.
    api_key: optional. NCBI api key. if entered, increases max amount of requests per second from 3 to 10. Highly recommended.
    verbose: optional. If set to True, function will print the current article fetched. Reduces speed.

### Frequently Unasked Questions

1. **Why does get_data() utilizes PMC for article search instead of PubMed? PMC contains far less articles.**
	
	While PMC contains less articles, as this database contains full texts of articles, instead of only abstracts, it is actually possible to find MORE articles for a given request. This is especially true for methods-related queries. Regarding overwhelming majority biology topics, you will be able to get a well representing dataset.

2. **Why then does get_abstracts() queries PubMed instead of PMC?**

	Entrez database doesn't allow to get full-text articles from PMC. The best that is possible to get is abstracts from PubMed.

3. **Is there any additional work planned for PDE-BIO?**
	
	Most likely I will return to this project to add more functionality and, possibly, add google scholar support. As I don't want to turn this into webcrawler, until google scholar releases its API, PDE-BIO won't work with that database.

### Awknoledgements

I would like to thank all members of Ukrainian bioinformatics community for supporting me on my way to becoming better specialist, especially Anton Kulaga and Yulia Sytnikova for their continuing help and mentorship, as well as r/bioinformatics community. Special thanks to Anthony Fejes for introducing me to the wider world of bioinformatics.

### License

PDE-BIO by Alexander Shynkarenko is licensed under GNU GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html

PDE-BIO utilizes E-utilities (Entrez) by NCBI. Disclaimer: https://www.ncbi.nlm.nih.gov/About/disclaimer.html

### Contact

You can contact me via my email: oleksandrszynkarenko@gmail.com
