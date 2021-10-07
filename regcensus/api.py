import re
import requests
import pandas as pd
import pprint

pp = pprint.PrettyPrinter()

date_format = re.compile(r'\d{4}(?:-\d{2}-\d{2})?')

URL = 'http://ec2-18-214-181-163.compute-1.amazonaws.com'


def get_values(series, jurisdiction, date, filtered=True, summary=True,
               documentType=1, agency=None, industry=None, dateIsRange=True,
               country=False, industryType='3-Digit', version=None,
               download=False, verbose=0):
    """
    Get values for a specific jurisdition and series

    Args:
        jurisdiction: Jurisdiction ID(s)
        series: Series ID(s)
        date: Year(s) of data
        summary (optional): Return summary instead of document level data
        filtered (optional): Exclude poorly-performing industry results
        documentType (optional): ID for type of document
        agency (optional): Agency ID (use 'all' for all agencies,
            only works for a single jurisdiction)
        industry (optional): Industry code using the jurisdiction-specific
            coding system (use 'all' for all industries)
        dateIsRange (optional): Indicating whether the time parameter is range
            or should be treated as single data points
        country (optional): Get all values for country ID
        industryType (optional): Level of NAICS industries to include,
            default is '3-Digit'
        version (optional): Version ID for datasets with multiple versions,
            if no ID is given, API returns most recent version
        download (optional): If not False, a path location for a
            downloaded csv of the results
        verbose (optional): Print out the url of the API call

    Returns: pandas dataframe with the values and various metadata

    Returns empty if required parameters are not given
    """

    # If multiple series are given, parses the list into a string
    if type(series) == list:
        url_call = (URL + f'/values?series={",".join(str(i) for i in series)}')
    elif type(series) in [int, str]:
        url_call = URL + f'/values?series={series}'
    # If no appropriate series is given, prints warning message and
    # list of available series, and function returns empty.
    else:
        print("Valid series ID required. Select from the following list:")
        pp.pprint(list_series())
        return

    # If multiple jurisdictions are given, parses the list into a string
    if type(jurisdiction) == list:
        url_call += f'&jurisdiction={",".join(str(i) for i in jurisdiction)}'
    elif type(jurisdiction) in [int, str]:
        url_call += f'&jurisdiction={jurisdiction}'
    # If no appropriate jurisdiction is given, prints warning message and
    # list of available jurisdictions, and function returns empty.
    else:
        print("Valid jurisdiction ID required.")
        pp.pprint(list_jurisdictions())
        return

    # Allows for all agency data to be returned
    if str(agency).lower() == 'all':
        agency = list(list_agencies(jurisdiction).values())
    # If multiple agencies are given, parses the list into a string
    if type(agency) == list:
        url_call += f'&agency={",".join(str(i) for i in agency)}'
    elif agency:
        url_call += f'&agency={agency}'

    # Allows for all industry data to be returned
    if str(industry).lower() == 'all':
        url_call = url_call.replace('?', '/industryTypes?').replace(
            'jurisdiction', 'jurisdictions')
        url_call += f'&industryType={industryType}'
    # If multiple industries are given, parses the list into a string
    elif type(industry) == list:
        url_call += f'&industry={",".join(str(i) for i in industry)}'
    elif industry:
        url_call += f'&industry={industry}'

    # If multiple dates are given, parses the list into a string
    if type(date) == list:
        url_call += f'&date={",".join(str(i) for i in date)}'
        # Force dateIsRange to be false if more than 2 dates are given
        if len(date) > 2:
            dateIsRange = False
    # Checks to see if date is in correct format
    elif date_format.match(str(date)):
        url_call += f'&date={date}'
        # Force dateIsRange to be false if only 1 date is given
        dateIsRange = False
    # If no appropriate date is given, prints warning message and
    # list of available dates for the given jurisdiction(s),
    # and function returns empty.
    else:
        print("Valid date is required.")
        pp.pprint(get_periods(jurisdiction, documentType=3))
        return

    if dateIsRange:
        url_call += '&dateIsRange=true'

    # Allows for document-level data to be retrieved.
    # Includes warning message explaning that this query may take a while.
    if not summary:
        if industry:
            print('WARNING: Returning document-level industry results. '
                  'This query make take several minutes.')
        url_call = url_call.replace('/values', '/values/documents')

    # Allows for unfiltered industry results to be retrieved. Includes
    # warning message explaining that these results should not be trusted.
    if industry and not filtered:
        print('WARNING: Returning unfiltered industry results. '
              'Use of these results is NOT recommended.')
        url_call += '&filteredOnly=false'

    # Always include documentType in the API call
    url_call += f'&documentType={documentType}'

    # Adds country argument if country-level data is requested
    if country:
        url_call = url_call.replace(
            '?', '/country?').replace('jurisdiction', 'countries')

    # Adds version argument if different version is requested
    if version:
        url_call += f'&version={version}'

    # Prints the url call if verbosity is flagged
    if verbose:
        print(f'API call: {url_call}')

    # Puts flattened JSON output into a pandas DataFrame
    output = json_normalize(requests.get(url_call).json())
    # Prints error message if call fails
    if (output.columns[:3] == ['title', 'status', 'detail']).all():
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


def get_series(seriesID='', verbose=0):
    """
    Get metadata for all or one specific series

    Args: seriesID (optional): ID for the series

    Returns: pandas dataframe with the metadata
    """
    url_call = URL + f'/series/{seriesID}'
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(requests.get(url_call).json()))


def get_agencies(jurisdictionID, verbose=0):
    """
    Get metadata for all agencies of a specific jurisdiction

    Args: jurisdictionID: ID for the jurisdiction

    Returns: pandas dataframe with the metadata
    """
    url_call = URL + (f'/agencies/jurisdiction?'
                      f'jurisdictions={jurisdictionID}')
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(requests.get(url_call).json()))


def get_jurisdictions(jurisdictionID='', verbose=0):
    """
    Get metadata for all or one specific jurisdiction

    Args: jurisdictionID (optional): ID for the jurisdiction

    Returns: pandas dataframe with the metadata
    """
    url_call = URL + f'/jurisdictions/{jurisdictionID}'
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(requests.get(url_call).json()))


def get_periods(jurisdictionID, documentType, seriesID='', verbose=0):
    """
    Get dates available for all or one specific series for a jurisdiction

    Args:
        jurisdictionID: ID for the jurisdiction
        documentType: document type (regulations, statutes, etc.),
            see list_document_types()
        seriesID (optional): ID for the series

    Returns: pandas dataframe with the dates
    """
    if seriesID:
        url_call = (URL + (f'/periods?jurisdiction={jurisdictionID}&'
                           f'series={seriesID}&'
                           f'documentType={documentType}'))
    else:
        url_call = (URL + (f'/periods?jurisdiction={jurisdictionID}&'
                           f'documentType={documentType}'))
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(requests.get(url_call).json()))


def get_industries(jurisdictionID, verbose=0):
    """
    Get metadata for all industries available in a specific jurisdiction

    Args: jurisdictionID: ID for the jurisdiction

    Returns: pandas dataframe with the metadata
    """
    url_call = URL + f'/industries?jurisdiction={jurisdictionID}'
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(requests.get(url_call).json()))


def get_documents(jurisdictionID, documentType=1, verbose=0):
    """
    Get metadata for documents available in a specific jurisdiction, optional
    filtering by document type (see list_document_types() for options)

    Args:
        jurisdictionID: ID for the jurisdiction
        documentType (optional): ID for type of document

    Returns: pandas dataframe with the metadata
    """
    url_call = URL + (f'/documents?jurisdiction={jurisdictionID}&'
                      f'documentType={documentType}')
    if verbose:
        print(f'API call: {url_call}')
    return clean_columns(json_normalize(requests.get(url_call).json()))


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
    return clean_columns(json_normalize(requests.get(url_call).json()))


def list_document_types():
    """
    Returns: a dictionary containing names of documenttypes and associated IDs
    """
    json = requests.get(URL + '/documenttypes').json()
    return dict(sorted({
        d["subtypeName"]: d["documentSubtypeID"]
        for d in json if d["subtypeName"]}.items()))


def list_series():
    """
    Returns: dictionary containing names of series and associated IDs
    """
    json = requests.get(URL + '/series').json()
    return dict(sorted({s["seriesName"]: s["seriesID"] for s in json}.items()))


def list_agencies(jurisdictionID):
    """
    Args: jurisdictionID: ID for the jurisdiction

    Returns: dictionary containing names of agencies and associated IDs
    """
    json = requests.get(
        URL + f'/agencies/jurisdiction?jurisdictions={jurisdictionID}').json()
    return dict(sorted({
        a["agencyName"]: a["agencyID"]
        for a in json if a["agencyName"]}.items()))


def list_jurisdictions():
    """
    Returns: dictionary containing names of jurisdictions and associated IDs
    """
    json = requests.get(URL + '/jurisdictions').json()
    return dict(sorted({
        j["jurisdictionName"]: j["jurisdictionID"] for j in json}.items()))


def list_industries(jurisdictionID):
    """
    Args: jurisdictionID: ID for the jurisdiction

    Returns: dictionary containing names of industries and their NAICS codes
    """
    json = requests.get(
        URL + f'/industries?jurisdiction={jurisdictionID}').json()
    return dict(sorted({
        i["industryName"]: i["industryCode"] for i in json}.items()))


def clean_columns(df):
    """Removes JSON prefixes from column names"""
    df.columns = [c.split('.')[-1] for c in df.columns]
    return df


def json_normalize(output):
    """Backwards compatability for old versions of pandas"""
    try:
        return pd.json_normalize(output)
    except AttributeError:
        return pd.io.json.json_normalize(output)
