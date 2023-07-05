import json
import re
import requests
import pandas as pd
import pprint

from regcensus.cache import Memoized

pp = pprint.PrettyPrinter()

date_format = re.compile(r'\d{4}(?:-\d{2}-\d{2})?')

URL = 'https://api.quantgov.org'


def get_values(series, jurisdiction, year, documentType=1, summary=True,
               dateIsRange=True, country=False, agency=None, cluster=None,
               label=None, industry=None, filtered=True,
               labellevel=3, industryLevel=None,
               labelsource='NAICS', version=None,
               download=False, page=None, date=None, verbose=0):
    """
    Get values for a specific jurisdiction, series, and year

    Args:
        jurisdiction: Jurisdiction ID(s) (name may also be passed)
        series: Series ID(s)
        year: Year(s) of data
        documentType (optional): ID for type of document,
            e.g. 1 is regulations, 2 is statutes
        summary (optional): Return summary instead of document level data,
            only one year of data is allowed for document level data
        dateIsRange (optional): Indicating whether the time parameter is range
            or should be treated as single data points
        country (optional): Get values for all subjurisdictions
        agency (optional): Agency ID (if no ID is passed and the series
            contains agency data, returns data for all agencies)
        label (formerly industry) (optional):
            Industry code using the jurisdiction-specific
            coding system (returns all 3-digit industries by default)
        filtered (optional): Exclude poorly-performing industry results
            (use of unfiltered results is NOT recommended)
        labellevel (formerly industryLevel) (optional):
            Level of NAICS industries to include
        version (optional): Version ID for datasets with multiple versions
            (if no ID is given, returns most recent version)
        download (optional): If not False, a path location for a
            downloaded csv of the results
        verbose (optional): Print out the url of the API call
            (useful for debugging)

    Returns: pandas dataframe with the values and various metadata

    Returns empty if required parameters are not given
    """
    if date:
        print('WARNING: date is deprecated, use year')
        return

    # If multiple jurisdiction names are given, find list of IDs
    if type(jurisdiction) == list and re.search(
            r'[A-Za-z]', str(jurisdiction[0])):
        jurisdiction = [list_jurisdictions()[i] for i in jurisdiction]
    # If jurisdiction name is passed, find ID
    elif jurisdiction and re.search(r'[A-Za-z]', str(jurisdiction)):
        jurisdiction = list_jurisdictions()[jurisdiction]

    # Use /datafinder endpoint to get the appropriate values endpoint
    try:
        endpoint = get_endpoint(
            series, jurisdiction, year, documentType, summary)
    # If endpoint is not found with given parameters, print datafinder table
    except IndexError:
        print('No data was found for these parameters. '
              'For this jurisdiction, consider the following:\n')
        with pd.option_context(
                'display.max_rows', None, 'display.max_columns', None):
            print(get_datafinder(
                jurisdiction, documentType).to_string(index=False))
            return

    if endpoint:
        url_call = URL + endpoint + '?'
    else:
        with pd.option_context(
                'display.max_rows', None, 'display.max_columns', None):
            try:
                print(
                    'No data was found for these parameters. '
                    'For this jurisdiction, consider the following:\n\n',
                    get_datafinder(
                        jurisdiction, documentType).to_string(index=False))
            except TypeError:
                print("Valid jurisdiction ID required. Consider the following:\n")
                pp.pprint(list_jurisdictions())
            return

    # If multiple series are given, parses the list into a string
    if type(series) == list:
        url_call += f'series={",".join(str(i) for i in series)}'
    elif type(series) in [int, str]:
        url_call += f'series={series}'
    # If no appropriate series is given, prints warning message and
    # list of available series, and function returns empty.
    else:
        print("Valid series ID required. Select from the following list:")
        pp.pprint(list_series())
        return

    # If multiple jurisdiction IDs are given, parses the list into a string
    if type(jurisdiction) == list:
        url_call += f'&jurisdiction={",".join(str(i) for i in jurisdiction)}'
    # If jurisdiction is just an ID, use jurisdiction
    elif type(jurisdiction) in [int, str]:
        url_call += f'&jurisdiction={jurisdiction}'
    # If no appropriate jurisdiction is given, prints warning message and
    # list of available jurisdictions, and function returns empty.
    else:
        print("Valid jurisdiction ID required.")
        pp.pprint(list_jurisdictions())
        return

    # If multiple agencies are given, parses the list into a string
    if type(agency) == list:
        url_call += f'&agency={",".join(str(i) for i in agency)}'
    elif agency:
        url_call += f'&agency={agency}'

    # If multiple clusters are given, parses the list into a string
    if type(cluster) == list:
        url_call += f'&cluster={",".join(str(i) for i in cluster)}'
    elif cluster:
        url_call += f'&cluster={cluster}'

    # Display deprecation message and rename industry args
    if industry:
        print('WARNING: industry is deprecated; use label')
        label = industry
    if industryLevel:
        print('WARNING: industryLevel is deprecated; use labellevel')
        labellevel = industryLevel
    # If multiple industries are given, parses the list into a string
    if type(label) == list:
        if labelsource == 'NAICS':
            label = [list_industries(labellevel=labellevel,
                                     labelsource=labelsource,
                                     onlyID=True)[str(i)] for i in label]
        url_call += f'&label={",".join(str(i) for i in label)}'
    elif label:
        if labelsource == 'NAICS':
            label = list_industries(labellevel=labellevel,
                                    labelsource=labelsource,
                                    onlyID=True)[str(label)]
        url_call += f'&label={label}'
    # Specify level of industry (NAICS only)
    if labellevel:
        url_call += f'&labelLevel={labellevel}'

    # If multiple years are given, parses the list into a string
    if type(year) == list:
        # If dateIsRange, parses the list to include all years
        if dateIsRange and len(year) == 2:
            year = range(int(year[0]), int(year[1]) + 1)
        url_call += f'&year={",".join(str(i) for i in year)}'
    # Checks to see if date is in correct format
    elif date_format.match(str(year)):
        url_call += f'&year={year}'
    # If no appropriate date is given, prints warning message and
    # list of available dates for the given jurisdiction(s),
    # and function returns empty.
    else:
        print("Valid date is required. Select from the following list:")
        dates = list_dates(jurisdiction, verbose=verbose)
        pp.pprint(dates)
        return

    # Allows for document-level data to be retrieved.
    # Includes warning message explaning that this query may take a while.
    if not summary:
        if label:
            print('WARNING: Returning document-level industry results. '
                  'This query make take several minutes.')
        url_call = url_call.replace('/summary', '/documents')

    # Allows for unfiltered industry results to be retrieved. Includes
    # warning message explaining that these results should not be trusted.
    if label and not filtered:
        print('WARNING: Returning unfiltered industry results. '
              'Use of these results is NOT recommended.')
        url_call += '&filteredOnly=false'

    # Adds documentType argument (default is 1 in API)
    if documentType:
        url_call += f'&documenttype={documentType}'

    # Adds country argument if country-level data is requested
    if country:
        print('WARNING: country is deprecated')

    # Adds version argument if different version is requested
    if version:
        # url_call += f'&version={version}'
        print('WARNING: version is temporarily deprecated')

    # Prints the url call if verbosity is flagged
    if verbose:
        print(f'API call: {url_call.replace(" ", "%20")}')

    # Allows user to manually select a page of the output
    # If page is not passed, pagination is done automatically (see below)
    # for output larger than 5000 rows
    if page:
        url_call += f'&page={page}'

    # Puts flattened JSON output into a pandas DataFrame
    try:
        json_output = requests.get(url_call).json()
        output = json_normalize(json.loads(json_output))
    # Prints error message if call errors
    except TypeError:
        print_error(json_output)
        return

    # If output is truncated, paginates until all data is found
    if len(output) == 5000 and not page:
        full_output = output
        page = 1
        while len(output) == 5000:
            if verbose:
                print(f'Output truncated, found page {page}')
            page += 1
            output = json_normalize(json.loads(requests.get(
                url_call + f'&page={page}').json()))
            full_output = pd.concat([full_output, output])
        output = full_output

    # If download path is given, write csv instead of returning dataframe
    if download:
        if type(download) == str:
            clean_columns(output).to_csv(download, index=False)
        else:
            print("Valid outpath required to download.")
    # Returns clean data if no error
    else:
        return clean_columns(output)


def get_document_values(*args, **kwargs):
    """
    Get values for a specific jurisdition and series at the document level

    Simply returns get_values() with summary=False
    """
    return get_values(*args, **kwargs, summary=False)


def get_reading_time(*args, **kwargs):
    """
    Convert word counts to total reading time
    """
    results = get_values(series=2, *args, **kwargs)
    results['series_name'] = 'Reading Time'
    results['series_value'] = results['series_value'].apply(reading_time)
    results['footNote'] = (
        'Reading time calculation assumes an 8 hour work-day, '
        'a 5 day work-week, and a 50 week work-year.')
    return results


@Memoized
def get_datafinder(jurisdiction, documentType=None):
    """
    Get API info for a specific jurisdition and documentType

    Returns: pandas dataframe with the series and years available,
             along with the endpoints to access the data
    """
    if documentType:
        output = clean_columns(json_normalize(json.loads(requests.get(
            URL + (f'/datafinder?jurisdiction={jurisdiction}&'
                   f'documenttype={documentType}')
        ).json())))
    else:
        output = clean_columns(json_normalize(json.loads(requests.get(
            URL + f'/datafinder?jurisdiction={jurisdiction}'
        ).json())))
    return output.rename({
        'jurisdiction_id': 'jurisdiction',
        'document_type_id': 'documentType',
        'series_id': 'series'}, axis=1)


@Memoized
def get_endpoint(series, jurisdiction, year, documentType, summary=True):
    """
    Get endpoint for a specific series, jurisdition, year, documentType combo

    Returns the endpoint, e.g. '/state-summary' for summary-level state data
    """
    if type(year) == list:
        year = [int(y) for y in year]
    if type(series) == list:
        series = [int(s) for s in series]
    try:
        datafinder = get_datafinder(jurisdiction, documentType).query(
            f'series == {series} and year == {year}')
        if summary:
            endpoint = datafinder.summary_endpoints.values[0]
        else:
            endpoint = datafinder.document_endpoints.values[0]
        # Handles document-level industry calls
        if not endpoint:
            endpoint = datafinder.label_endpoints.values[0]
        return endpoint
    except (KeyError, TypeError):
        return


@Memoized
def get_series(verbose=0):
    """
    Get series metadata for all or one specific jurisdiction

    Args: jurisdictionID (optional): ID for the jurisdiction

    Returns: pandas dataframe with the metadata
    """
    url_call = series_url()
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(
        json.loads(requests.get(url_call).json())))


@Memoized
def get_agencies(jurisdictionID=None, keyword=None, verbose=0):
    """
    Get metadata for all agencies of a specific jurisdiction

    Args: jurisdictionID: ID for the jurisdiction

    Returns: pandas dataframe with the metadata
    """
    url_call = agency_url(jurisdictionID, keyword)
    if not url_call:
        return
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(
        json.loads(requests.get(url_call).json())))


@Memoized
def get_jurisdictions(verbose=0):
    """
    Get metadata for all or one specific jurisdiction

    Args: jurisdictionID (optional): ID for the jurisdiction

    Returns: pandas dataframe with the metadata
    """
    url_call = jurisdictions_url()
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(
        json.loads(requests.get(url_call).json())))


@Memoized
def get_industries(keyword=None, labellevel=3, labelsource=None, verbose=0):
    """
    Get metadata for all industries available in a specific jurisdiction

    Args:
        keyword: search for keyword in industry name
        labellevel: NAICS level (2 to 6-digit)
        labelsource: classification standard (NAICS, BEA, SOC)

    Returns: pandas dataframe with the metadata
    """
    url_call = industries_url(keyword, labellevel, labelsource)
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(
        json.loads(requests.get(url_call).json())))


@Memoized
def get_documents(documentID=None, jurisdictionID=None, date=None,
                  documentType=1, verbose=0):
    """
    Get metadata for documents available in a specific jurisdiction or
    for a specific document ID

    Args:
        documentID: ID of the specific document
        jurisdictionID: ID for the jurisdiction
        date: Year(s) of the documents
        documentType (optional): ID for type of document

    Returns: pandas dataframe with the metadata
    """
    if documentID:
        print('documentID is no longer accessible as of version X.XX. '
              'Use previous version of API or use jurisdictionID and date '
              'combination')
        return
    elif jurisdictionID and date:
        return get_values(
            series=1,
            jurisdiction=jurisdictionID,
            year=date,
            documentType=documentType,
            summary=False)
    else:
        print('Must include "jurisdictionID and date"')
        return


@Memoized
def get_versions(jurisdictionID, documentType=1, verbose=0):
    """
    Get metadata for versions available in a specific jurisdiction.

    Args:
        jurisdictionID: ID for the jurisdiction
        documentType (optional): ID for type of document

    Returns: pandas dataframe with the metadata
    """
    url_call = URL + (f'/version?jurisdiction={jurisdictionID}&'
                      f'documentType={documentType}')
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(
        json.loads(requests.get(url_call).json())))


@Memoized
def get_documentation():
    """
    Get documentation for projects, including citations.
    """
    return clean_columns(json_normalize(json.loads(requests.get(
        URL + '/documentation'
    ).json())))


@Memoized
def list_document_types(jurisdictionID=None, reverse=False, verbose=0):
    """
    Args: jurisdictionID (optional): ID for the jurisdiction

    Returns: a dictionary containing names of documenttypes and associated IDs
    """
    if jurisdictionID:
        url_call = URL + f'/documenttypes?jurisdiction={jurisdictionID}'
    else:
        url_call = URL + '/documenttypes'
    if verbose:
        print(f'API call: {url_call}')
    content = json.loads(requests.get(url_call).json())
    if reverse:
        return dict(sorted({
            d["document_type_id"]: d["document_type"]
            for d in content if d["document_type"]}.items()))
    else:
        return dict(sorted({
            d["document_type"]: d["document_type_id"]
            for d in content if d["document_type"]}.items()))


@Memoized
def list_series(reverse=False):
    """
    Args:
        jurisdictionID: ID for the jurisdiction
        documentType (optional): ID for type of document

    Returns: dictionary containing names of series and associated IDs
    """
    url_call = series_url()
    content = json.loads(requests.get(url_call).json())
    if reverse:
        return dict(sorted({
            s["series_id"]: s["series_name"]
            for s in content}.items()))
    else:
        return dict(sorted({
            s["series_name"]: s["series_id"]
            for s in content}.items()))


@Memoized
def list_dates(jurisdictionID, documentType=None):
    """
    Args:
        jurisdictionID: ID for the jurisdiction
        documentType (optional): ID for type of document

    Returns: list of dates available for the jurisdiction
    """
    return sorted(get_datafinder(
        jurisdictionID, documentType)['year'].unique())


@Memoized
def list_agencies(jurisdictionID=None, keyword=None, reverse=False):
    """
    Args:
        jurisdictionID: ID for the jurisdiction
        keyword: search for keyword in agency name

    Returns: dictionary containing names of agencies and associated IDs
    """
    url_call = agency_url(jurisdictionID, keyword)
    if not url_call:
        return
    content = json.loads(requests.get(url_call).json())

    jurisdictions_df = get_jurisdictions()
    jurisdiction_id_name = dict(zip(jurisdictions_df["jurisdiction_id"],
                                    jurisdictions_df["jurisdiction_name"]))

    # Add jurisdiction name to key if keyword is used
    if reverse:
        if keyword:
            return dict(sorted({
                a["agency_id"]:
                    f'{a["agency_name"]} ({jurisdiction_id_name[int(a["a_jurisdiction_id"])]})'
                for a in content if a["agency_name"]}.items()))
        else:
            return dict(sorted({
                a["agency_id"]: a["agency_name"]
                for a in content if a["agency_name"]}.items()))
    else:
        if keyword:
            return dict(sorted({
                f'{a["agency_name"]} ({jurisdiction_id_name[int(a["a_jurisdiction_id"])]})':
                    a["agency_id"]
                for a in content if a["agency_name"]}.items()))
        else:
            return dict(sorted({
                a["agency_name"]: a["agency_id"]
                for a in content if a["agency_name"]}.items()))


@Memoized
def list_clusters(reverse=False):
    """
    Returns: dictionary containing names of clusters and associated IDs
    """
    url_call = URL + '/clusters'
    content = json.loads(requests.get(url_call).json())
    if reverse:
        return dict(sorted({
            a["agency_cluster"]: a["cluster_name"]
            for a in content if a["cluster_name"]}.items()))
    else:
        return dict(sorted({
            a["cluster_name"]: a["agency_cluster"]
            for a in content if a["cluster_name"]}.items()))


@Memoized
def list_jurisdictions(reverse=False):
    """
    Returns: dictionary containing names of jurisdictions and associated IDs
    """
    url_call = jurisdictions_url()
    content = json.loads(requests.get(url_call).json())
    if reverse:
        return dict(sorted({
            j["jurisdiction_id"]: j["jurisdiction_name"]
            for j in content}.items()))
    else:
        return dict(sorted({
            j["jurisdiction_name"]: j["jurisdiction_id"]
            for j in content}.items()))


@Memoized
def list_industries(
        keyword=None, labellevel=3, labelsource='NAICS',
        onlyID=False, reverse=False):
    """
    Args:
        keyword: search for keyword in industry name
        codeLevel: NAICS level (2 to 6-digit)
        standard: classification standard (NAICS (default), BEA, SOC)
        onlyID: uses the NAICS code instead of name as key of dictionary

    Returns: dictionary containing names of industries and associated IDs
    """
    url_call = industries_url(keyword, labellevel, labelsource)
    content = json.loads(requests.get(url_call).json())
    # If industry has codes, include the code in the key
    try:
        if onlyID:
            if reverse:
                return dict(sorted({
                    i["label_id"]: i["label_code"] for i in content}.items()))
            else:
                return dict(sorted({
                    i["label_code"]: i["label_id"] for i in content}.items()))
        else:
            if reverse:
                return dict(sorted({
                    i["label_id"]: f'{i["label_name"]} ({i["label_code"]})'
                    for i in content}.items()))
            else:
                return dict(sorted({
                    f'{i["label_name"]} ({i["label_code"]})': i["label_id"]
                    for i in content}.items()))
    except KeyError:
        if reverse:
            return dict(sorted({
                i["label_id"]: i["label_name"] for i in content}.items()))
        else:
            return dict(sorted({
                i["label_name"]: i["label_id"] for i in content}.items()))


def series_url():
    """Gets url call for dataseries endpoint."""
    return URL + '/dataseries'


def agency_url(jurisdictionID, keyword):
    """Gets url call for agencies endpoint."""
    if keyword:
        url_call = URL + (f'/agencies-keyword?'
                          f'keyword={keyword}')
    elif jurisdictionID:
        url_call = URL + (f'/agencies?'
                          f'jurisdiction={jurisdictionID}')
    else:
        print('Must include either "jurisdictionID" or "keyword."')
        return
    return url_call


def jurisdictions_url():
    """Gets url call for jurisdictions endpoint."""
    return URL + '/jurisdictions/'


def industries_url(keyword, labellevel, labelsource):
    """Gets url call for label (formerly industries) endpoint."""
    if keyword:
        url_call = (
            URL + f'/labels?'
                  f'labellevel={labellevel}&keyword={keyword}')
    else:
        url_call = URL + f'/labels?labellevel={labellevel}'
    if labelsource:
        url_call += f'&labelsource={labelsource}'
    return url_call


def clean_columns(df):
    """Removes prefixes from column names"""
    df.columns = [c.split('v_')[-1] for c in df.columns]
    return df


def json_normalize(output):
    """Backwards compatability for old versions of pandas"""
    try:
        return pd.json_normalize(output)
    except AttributeError:
        return pd.io.json.json_normalize(output)


def print_error(output):
    """Handle and print out error for invalid API call"""
    try:
        print('ERROR:', output['message'])
    except KeyError:
        print('ERROR', output["errorMessage"])
    return


def reading_time(words, workday=8, workweek=5, workyear=50):
    """
    Returns a string detailing how long it takes to read a document based on
    how many words the document has. The function assumes an 8 hour work-day,
    a 5 day work-week, and a 50 week work-year.
    """
    text = ''
    years = words / 36000000
    weeks = (years - int(years)) * workyear
    days = (weeks - int(weeks)) * workweek
    hours = (days - int(days)) * workday
    minutes = (hours - int(hours)) * 60
    if int(years):
        text += str(int(years)) + ' year, '
        if int(years) > 1:
            text = text.replace('year', 'years')
    if int(weeks):
        text += str(int(weeks)) + ' week, '
        if int(weeks) > 1:
            text = text.replace('week', 'weeks')
    if int(days):
        text += str(int(days)) + ' day, '
        if int(days) > 1:
            text = text.replace('day', 'days')
    if int(hours) and not int(years):
        text += str(int(hours)) + ' hour, '
        if int(hours) > 1:
            text = text.replace('hour', 'hours')
    if int(minutes) and not int(years) and not int(weeks):
        text += str(int(minutes)) + ' minute'
        if int(minutes) > 1:
            text = text.replace('minute', 'minutes')
    if text:
        return text.strip(', ')
    else:
        return 'Less than a minute'
