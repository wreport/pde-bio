#!/usr/bin/env python

"""PDE-BIO: Publication Data Extractor for Biological Studies"""

__author__      = "Alexander Shynkarenko"
__copyright__   = "Copyright 2019, Alex Shynkarenko"

__license__ = "GNU GPLv3"
__version__ = "1.0"
__maintainer__ = "Alexander Shynkarenko"
__email__ = "oleksandrszynkarenko@gmail.com"
__status__ = "Production"


from Bio import Entrez
import csv
import os
import itertools


def get_ids(term, date, email, api_key = None, database = 'pmc'):

    """
    Gets a list of IDs for a given keyword.

    :param term: a query to be searched.
    :param date: date range to be searched.
    :param email: email for Entrez databaze.
    :param api_key: optional. NCBI api key. if entered, increases max amount of requests per second from 3 to 10.
    :return: dictionary containing fetched data with relevant metadata.
    """

    id_dict = {'term': term,
               'year': date.split('/')[0],
               'date': date}

    searchquery = '{} AND {}[Publication Date]'.format(term, date)

    if email is not None:
        Entrez.email = email

    if api_key is not None:
        Entrez.api_key = api_key

    handle = Entrez.esearch(db = database, retmax = 100000, term = searchquery)
    record = Entrez.read(handle)
    handle.close()

    id_dict.update({'count': record['Count'],
                    'pmcid_list': ','.join(record['IdList'])})
    return id_dict


def construct_csv(id_dict, output_file='output.csv'):

    """
    Makes a csv file with the data fetched from the PMC. In case the file already exsisting, appends a new line to the
    file.

    :param id_dict: dictionary containing fetched data with relevant metadata.
    :param output_file: file to output data to.
    :return: returns None. makes csv file containing fetched data.
    """

    with open(os.path.relpath(output_file),'a+',newline='') as write_file:
        writer = csv.DictWriter(write_file, fieldnames=['term','year','date','count','pmcid_list'])
        if len(open(os.path.relpath(output_file)).readlines()) == 0:
            writer.writeheader()
        writer.writerow({'term': id_dict['term'],
                         'year': id_dict['year'],
                         'date': id_dict['date'],
                         'count': id_dict['count'],
                         'pmcid_list': id_dict['pmcid_list']})

    return None


def permutate_dates(starting_year, final_year):

    """
    Splits years by months.
    
    :param starting_year: used to create a starting year for the list of dates.
    :param final_year: used to create a final year for the list of dates.
    :return: a list of months usable for Entrez esearch.
    """""

    starting_year, final_year = int(starting_year), int(final_year)

    years = [str(x) for x in  range(starting_year,final_year+1)]
    month_appendages = [str(x) for x in range(1,13)]
    day_appendages_start = ['1']
    day_appendages_finish = ['31']

    appendages_start = ['/{}/{}'.format(x[0],x[1]) for x in itertools.product(month_appendages,day_appendages_start)]
    appendages_finish = ['/{}/{}'.format(x[0], x[1]) for x in itertools.product(month_appendages,day_appendages_finish)]
    dates_start = ['{}{}'.format(x[0],x[1]) for x in itertools.product(years,appendages_start)]
    dates_finish = ['{}{}'.format(x[0], x[1]) for x in itertools.product(years, appendages_finish)]

    dates = ['{}:{}'.format(x[0],x[1]) for x in zip(dates_start,dates_finish)]

    return dates


def get_data(term, starting_year, final_year, email,
             api_key=None,output_file='summary.csv',list_output=False, database = 'pmc', verbose = False):
    """
    Intended to be called by users. Gets data from PMC and scribes it into a csv file

    :param term: a query to be searched.
    :param starting_year: used to create a starting year for the list of dates.
    :param final_year: used to create a final year for the list of dates.
    :param email: email for Entrez databaze.
    :param api_key: optional. NCBI api key. if entered, increases max amount of requests per second from 3 to 10.
    :param output_file: name of a file for data to be stored in. default value is 'summary.csv'.
    :param list_output: if set to True, instead of creating csv file, function returns a list of fetched data.
    :param verbose: optional. If set to True, function will print the current term and date combination fetched.
    :param database: NCBI database to search for. Default set to pmc.
    :return: returns None. makes csv file containing fetched data. if list_output = True, returns list of fetched data.
    """

    dates = permutate_dates(starting_year,final_year)
    data_list = []

    i = 1
    maxdates = len(dates)
    for date in dates:
        if verbose:
            print('Processing {} out of {} requests for {}.'.format(i,maxdates,term))
        i = i + 1
        data_list.append(get_ids(term, date, email, api_key, database))
    if list_output == False:
        for entry in data_list:
            construct_csv(entry,output_file=output_file,)
        return None
    else:
        return data_list


def transform_id(pmcid,email,api_key=None):
    """
    Transforms pmcid into pmid

    :param pmcid: Pubmed Central entry Id
    :param email: email for Entrez databaze.
    :param api_key: optional. NCBI api key. if entered, increases max amount of requests per second from 3 to 10.
    :return: returns Pubmed Id that is used for abstract fetching
    """
    Entrez.email = email

    if api_key is not None:
        Entrez.api_key = api_key

    handle = Entrez.elink(dbfrom="pmc", db="pubmed", linkname="pmc_pubmed", id=pmcid)

    record = Entrez.read(handle)
    try:
        pmid = record[0]['LinkSetDb'][0]['Link'][0]['Id']
    except IndexError:
        return False
    handle.close()

    return pmid


def fetch_article_data(pmid, term, date, year, email, api_key=None):
    """
    Fetches article data from pubmed by pmid, then outputs as a dictionary

    :param pmid: PubMed ID
    :param term: a query to be searched.
    :param date: date range to be searched.
    :param year: year of the published article
    :param email: email for Entrez databaze.
    :param api_key: optional. NCBI api key. if entered, increases max amount of requests per second from 3 to 10.
    :return: dictionary containing article data.
    """
    if pmid is False:
        article_data = {'term': term,
                        'year': year,
                        'date': date,
                        'pmid': '',
                        'link': '',
                        'title': '',
                        'journal': '',
                        'authors': '',
                        'abstract': ''
                        }
        return article_data

    Entrez.email = email

    if api_key is not None:
        Entrez.api_key = api_key

    handle = Entrez.efetch(db="pubmed", id=pmid, rettype="gb", )
    record = Entrez.read(handle)
    handle.close()

    title = ''
    journal = ''
    authors = ''
    abstract = ''
    try:
        title = record['PubmedArticle'][0]['MedlineCitation']['Article']['ArticleTitle']
        if 'Abstract' in record['PubmedArticle'][0]['MedlineCitation']['Article']:
            abstract = record['PubmedArticle'][0]['MedlineCitation']['Article']['Abstract']['AbstractText'][0]
        else:
            abstract = ''
        journal = record['PubmedArticle'][0]['MedlineCitation']['Article']['Journal']['Title']

        authors = []
        for author in record['PubmedArticle'][0]['MedlineCitation']['Article']['AuthorList']:
            authors.append('{} {}'.format(author['LastName'], author['Initials']))
        authors = ', '.join(authors)
    except KeyError:
        pass

    article_data = {'term': term,
                    'year': year,
                    'date': date,
                    'pmid': pmid,
                    'link': 'https://www.ncbi.nlm.nih.gov/pubmed/{}'.format(pmid),
                    'title': title,
                    'journal': journal,
                    'authors': authors,
                    'abstract': abstract
                    }
    return article_data


def get_abstracts(email, input_file = 'summary.csv', output_file = 'articles.csv', api_key = None, verbose = False):
    """
    Transforms output file into per-article data format


    :return: none. makes OR extends csvfile containing per-article structured data made from info provided by get_data
    """
    csvrdr = ''
    with open(os.path.relpath(input_file),'r') as read_file:
        csvrdr = csv.DictReader(read_file)

        csvdr_iterable = []
        for item in csvrdr:
            csvdr_iterable.append(item)

    exists = os.path.isfile(output_file)

    # identifies current article to be fetched
    current = None

    # identifies whether to skip the current article. Used to identify whe
    skip = False

    # once the script founds current 'pointer', it doesn't need to see whether the next article becomes current
    # so it can just automatically approve every single one that's coming
    go_on = False

    # if there is no output file, creates one and puts header.
    if not exists:
        with open(os.path.relpath(output_file),'w+') as write_file:
            write_file.write('term,year,date,pmid,pmcid,link,title,journal,authors,abstract\n')

    else:
        # if there is, checks for the last analysed article so that there will be no duplicates
        with open(os.path.relpath(output_file),'r') as read_file2:
            csvrdr2 = csv.DictReader(read_file2)

            csvdr_iterable2 = []
            for item in csvrdr2:
                csvdr_iterable2.append(item)
            current = '{}-{}-{}'.format(csvdr_iterable2[-1]['term'],
                                    csvdr_iterable2[-1]['date'],
                                    csvdr_iterable2[-1]['pmcid'])
            skip = True

    # makes sure that there is always current article
    if current is None:
        current = '{}-{}-{}'.format(csvdr_iterable[0]['term'],
                                    csvdr_iterable[0]['date'],
                                    csvdr_iterable[0]['pmcid_list'].split(',')[0])

    # iterates through each and every article and fetches relevant data, then writes it into the csv file
    for termdate in  csvdr_iterable:
        if (termdate['term'] == current.split('-')[0] and termdate['date'] == current.split('-')[1]) or go_on is True:
            pmcids = termdate['pmcid_list'].split(',')
            for index,pmcid in enumerate(pmcids):
                if pmcid == current.split('-')[2] or go_on is True:
                    if skip is False:

                        pmid = transform_id(pmcid, email, api_key)

                        if verbose:
                            print('Fetching and writing article data for PMID {}, PMCID {}, term {}, date {}'
                                  .format(pmid,
                                          pmcid,
                                          termdate['term'],
                                          termdate['date']))

                        article_data = fetch_article_data(pmid,
                                                          termdate['term'],
                                                          termdate['date'],
                                                          termdate['year'],
                                                          email,
                                                          api_key)

                        with open(os.path.relpath(output_file),'a+', encoding='utf-8', newline='') as write_file:
                            csvwrtr = csv.DictWriter(write_file, fieldnames=['term',
                                                                             'year',
                                                                             'date',
                                                                             'pmid',
                                                                             'pmcid',
                                                                             'link',
                                                                             'title',
                                                                             'journal',
                                                                             'authors',
                                                                             'abstract'])

                            csvwrtr.writerow({'term': article_data['term'],
                                              'year': article_data['year'],
                                              'date': article_data['date'],
                                              'pmid': pmid,
                                              'pmcid': pmcid,
                                              'link': 'https://www.ncbi.nlm.nih.gov/pubmed/{}'.format(pmid),
                                              'title': article_data['title'],
                                              'journal': article_data['journal'],
                                              'authors': article_data['authors'],
                                              'abstract': article_data['abstract']})

                    if pmcid != pmcids[-1]:
                        current = '{}-{}-{}'.format(termdate['term'],
                                                    termdate['date'],
                                                    pmcids[index+1])

                    # after the first article in each run, the programm will fetch each next article
                    skip = False
                    go_on = True