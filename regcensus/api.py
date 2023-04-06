import json
import re
import requests
import pandas as pd
import pprint

pp = pprint.PrettyPrinter()

date_format = re.compile(r'\d{4}(?:-\d{2}-\d{2})?')

URL = 'https://64gzqlrrd2.execute-api.us-east-1.amazonaws.com/dev'


def get_values(series, jurisdiction, year, documentType=1, summary=True,
               dateIsRange=True, country=False, agency=None, cluster=None,
               industry=None, filtered=True, industryLevel=None, version=None,
               download=False, verbose=0):
    """
    Get values for a specific jurisdiction and series

    Args:
        jurisdiction: Jurisdiction ID(s) (name may also be passed)
        series: Series ID(s)
        year: Year(s) of data
        documentType (optional): ID for type of document
        summary (optional): Return summary instead of document level data
        dateIsRange (optional): Indicating whether the time parameter is range
            or should be treated as single data points
        country (optional): Get values for all subjurisdictions
        agency (optional): Agency ID (if no ID is passed and the series
            contains agency data, returns data for all agencies)
        industry (optional): Industry code using the jurisdiction-specific
            coding system (returns all 3-digit industries by default)
        filtered (optional): Exclude poorly-performing industry results
            (use of unfiltered results is NOT recommended)
        industryLevel (optional): Level of NAICS industries to include
            (default is 3 in the API)
        version (optional): Version ID for datasets with multiple versions
            (if no ID is given, returns most recent version)
        download (optional): If not False, a path location for a
            downloaded csv of the results
        verbose (optional): Print out the url of the API call
            (useful for debugging)

    Returns: pandas dataframe with the values and various metadata

    Returns empty if required parameters are not given
    """

    # Use /datafinder endpoint to get the appropriate values endpoint
    endpoint = get_endpoint(series, jurisdiction, year, summary)
    url_call = URL + endpoint + '?'

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

    # If multiple jurisdiction names are given, parses the list into a string
    if type(jurisdiction) == list and re.search(r'\D', str(jurisdiction[0])):
        url_call += f'&jurisdictionName={",".join(i for i in jurisdiction)}'
    # If multiple jurisdiction IDs are given, parses the list into a string
    elif type(jurisdiction) == list:
        url_call += f'&jurisdiction={",".join(str(i) for i in jurisdiction)}'
    # If jurisdiction name is passed, use jurisdictionName
    elif jurisdiction and re.search(r'\D', str(jurisdiction)):
        url_call += f'&jurisdictionName={jurisdiction}'
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

    # If multiple industries are given, parses the list into a string
    if type(industry) == list:
        url_call += f'&label={",".join(str(i) for i in industry)}'
    elif industry:
        url_call += f'&label={industry}'
    # Specify level of industry (NAICS only)
    if industryLevel:
        url_call += f'&labelLevel={industryLevel}'

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
        if industry:
            print('WARNING: Returning document-level industry results. '
                  'This query make take several minutes.')
        url_call = url_call.replace('/summary', '/documents')

    # Allows for unfiltered industry results to be retrieved. Includes
    # warning message explaining that these results should not be trusted.
    if industry and not filtered:
        print('WARNING: Returning unfiltered industry results. '
              'Use of these results is NOT recommended.')
        url_call += '&filteredOnly=false'

    # Adds documentType argument (default is 1 in API)
    if documentType:
        url_call += f'&documenttype={documentType}'

    # Adds country argument if country-level data is requested
    if country:
        url_call += '&national=True'

    # Adds version argument if different version is requested
    if version:
        url_call += f'&version={version}'

    # Prints the url call if verbosity is flagged
    if verbose:
        print(f'API call: {url_call.replace(" ", "%20")}')

    # Puts flattened JSON output into a pandas DataFrame
    output = json_normalize(json.loads(requests.get(url_call).json()))
    # Prints error message if call fails
    if False:#(output.columns[:3] == ['title', 'status', 'detail']).all():
        print('WARNING:', output.iloc[0][-1])
        return
    elif download:
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


def get_datafinder(jurisdiction, documentType=None):
    if documentType:
        return json_normalize(json.loads(requests.get(
            URL + (f'/datafinder?jurisdiction={jurisdiction}&'
                   f'documentType={documentType}')
        ).json()))
    else:
        return json_normalize(json.loads(requests.get(
            URL + f'/datafinder?jurisdiction={jurisdiction}'
        ).json()))


def get_endpoint(series, jurisdiction, year, summary=True):
    if type(year) == list:
        year = [int(y) for y in year]
    datafinder = clean_columns(get_datafinder(jurisdiction)).query(
        f'series_id == {series} and year == {year}')
    if summary:
        return datafinder.summary_endpoints.values[0]
    else:
        return datafinder.document_endpoints.values[0]


def get_series(jurisdictionID=None, documentType=None, verbose=0):
    """
    Get series metadata for all or one specific jurisdiction

    Args: jurisdictionID (optional): ID for the jurisdiction

    Returns: pandas dataframe with the metadata
    """
    url_call = series_url(jurisdictionID, documentType)
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(
        json.loads(requests.get(url_call).json())))


def get_periods(jurisdictionID=None, documentType=None, verbose=0):
    """
    Get date metadata for all or one specific jurisdiction

    Args: jurisdictionID (optional): ID for the jurisdiction

    Returns: pandas dataframe with the metadata
    """
    url_call = periods_url(jurisdictionID, documentType)
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(
        json.loads(requests.get(url_call).json())))


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


def get_jurisdictions(jurisdictionID=None, verbose=0):
    """
    Get metadata for all or one specific jurisdiction

    Args: jurisdictionID (optional): ID for the jurisdiction

    Returns: pandas dataframe with the metadata
    """
    url_call = jurisdictions_url(jurisdictionID)
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(
        json.loads(requests.get(url_call).json())))


def get_industries(keyword=None, codeLevel=3, standard=None, verbose=0):
    """
    Get metadata for all industries available in a specific jurisdiction

    Args:
        keyword: search for keyword in industry name
        codeLevel: NAICS level (2 to 6-digit)
        standard: classification standard (NAICS, BEA, SOC)

    Returns: pandas dataframe with the metadata
    """
    url_call = industries_url(keyword, codeLevel, standard)
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(
        json.loads(requests.get(url_call).json())))


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
        url_call = URL + f'/documentMetadata/documents?documentID={documentID}'
    elif jurisdictionID and date:
        url_call = URL + (f'/documentMetadata?jurisdiction={jurisdictionID}&'
                          f'documentType={documentType}')
    else:
        print('Must include either "jurisdictionID and date" or "documentID."')
        return
    if type(date) == list:
        url_call += f'&date={",".join(str(i) for i in date)}'
        if len(date) == 2:
            url_call += '&dateIsRange=true'
        else:
            url_call += '&dateIsRange=false'
    else:
        url_call += f'&date={date}'
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(
        json.loads(requests.get(url_call).json())))


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


def get_documentation():
    """
    Get documentation for projects, including citations.
    """
    return clean_columns(json_normalize(json.loads(requests.get(
        URL + '/documentation'
    ).json())))


def list_document_types(jurisdictionID=None, verbose=0):
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
    return dict(sorted({
        d["document_type"]: d["document_type_id"]
        for d in content if d["document_type"]}.items()))


def list_series(jurisdictionID, documentType=None):
    """
    Args:
        jurisdictionID: ID for the jurisdiction
        documentType (optional): ID for type of document

    Returns: dictionary containing names of series and associated IDs
    """
    url_call = series_url(jurisdictionID, documentType)
    content = json.loads(requests.get(url_call).json())
    return dict(sorted({
        s["series_name"]: s["series_id"]
        for s in content}.items()))


def list_dates(jurisdictionID, documentType=None, verbose=0):
    """
    Args:
        jurisdictionID: ID for the jurisdiction
        documentType (optional): ID for type of document

    Returns: list of dates available for the jurisdiction
    """
    return sorted(get_datafinder(
        jurisdictionID, documentType)['year'].unique())


def list_agencies(jurisdictionID=None, keyword=None):
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
    # Add jurisdiction name to key if keyword is used
    if keyword:
        return dict(sorted({
            f'{a["agency_name"]} ({a["jurisdiction_name"]})': a["agency_id"]
            for a in content if a["agency_name"]}.items()))
    else:
        return dict(sorted({
            a["agency_name"]: a["agency_id"]
            for a in content if a["agency_name"]}.items()))


def list_clusters():
    """
    Returns: dictionary containing names of clusters and associated IDs
    """
    url_call = URL + '/clusters'
    content = json.loads(requests.get(url_call).json())
    return dict(sorted({
        a["cluster_name"]: a["agency_cluster"]
        for a in content if a["cluster_name"]}.items()))


def list_jurisdictions():
    """
    Returns: dictionary containing names of jurisdictions and associated IDs
    """
    url_call = jurisdictions_url(None)
    content = json.loads(requests.get(url_call).json())
    return dict(sorted({
        j["jurisdiction_name"]: j["jurisdiction_id"] for j in content}.items()))


def list_industries(keyword=None, codeLevel=3, standard='NAICS', onlyID=False):
    """
    Args:
        keyword: search for keyword in industry name
        codeLevel: NAICS level (2 to 6-digit)
        standard: classification standard (NAICS (default), BEA, SOC)
        onlyID: uses the NAICS code instead of name as key of dictionary

    Returns: dictionary containing names of industries and associated IDs
    """
    url_call = industries_url(keyword, codeLevel, standard)
    content = json.loads(requests.get(url_call).json())
    # If industry has codes, include the code in the key
    try:
        if onlyID:
            return dict(sorted({
                i["label_code"]: i["label_id"] for i in content}.items()))
        else:
            return dict(sorted({
                f'{i["label_name"]} ({i["label_code"]})':
                i["label_id"] for i in content}.items()))
    except KeyError:
        return dict(sorted({
            i["label_name"]: i["label_id"] for i in content}.items()))


def series_url(jurisdictionID, documentType=None):
    """Gets url call for series endpoint."""
    url_call = URL + '/dataseries'
    if jurisdictionID and documentType:
        url_call += (
            f'?jurisdiction={jurisdictionID}&'
            f'documentType={documentType}')
    elif jurisdictionID:
        url_call += f'?jurisdiction={jurisdictionID}'
    elif documentType:
        url_call += f'?documentType={documentType}'
    return url_call


def periods_url(jurisdictionID, documentType=None):
    """Gets url call for series endpoint."""
    url_call = URL + '/seriesperiod'
    if jurisdictionID and documentType:
        url_call += (
            f'?jurisdiction={jurisdictionID}&'
            f'documentType={documentType}')
    elif jurisdictionID:
        url_call += f'?jurisdiction={jurisdictionID}'
    elif documentType:
        url_call += f'?documentType={documentType}'
    return url_call


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


def jurisdictions_url(jurisdictionID):
    """Gets url call for jurisdictions endpoint."""
    url_call = URL + '/jurisdictions/'
    if jurisdictionID:
        url_call += f'/specific?jurisdiction={jurisdictionID}'
    return url_call


def industries_url(keyword, codeLevel, standard):
    """Gets url call for label (formerly industries) endpoint."""
    if keyword:
        url_call = (
            URL + f'/labels?'
                  f'codeLevel={codeLevel}&keyword={keyword}')
    else:
        url_call = URL + f'/labels?codeLevel={codeLevel}'
    if standard:
        url_call += f'&standard={standard}'
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
