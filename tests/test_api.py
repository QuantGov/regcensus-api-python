import os
import regcensus as rc


# UTILITY FUNCTIONS
def order_results(results, column, descending=False):
    if descending:
        return list(reversed(results[column].sort_values().tail(10).values))
    else:
        return list(results[column].sort_values().head(10).values)


# TEST FUNCTIONS

# Tests for get_() functions
def test_get_series():
    results = rc.get_series(verbose=1)
    assert order_results(results, 'seriesID') == [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    ]


def test_get_agencies():
    results = rc.get_agencies(jurisdictionID=38, verbose=1)
    assert order_results(results, 'agencyID') == [
        0, 9519, 9520, 9521, 9522, 9523, 9524, 9525, 9526, 9527
    ]


def test_get_agencies_keyword():
    results = rc.get_agencies(keyword='Education', verbose=1)
    assert order_results(results, 'agencyID') == [
        46, 47, 48, 263, 264, 270, 271, 286, 394, 403
    ]


def test_get_agencies_error(capsys):
    results = rc.get_agencies()
    assert not results
    assert capsys.readouterr().out == (
        'Must include either "jurisdictionID" or "keyword."\n')


def test_get_jurisdictions():
    results = rc.get_jurisdictions(38, verbose=1)
    assert order_results(results, 'jurisdictionID') == [38]


def test_get_industries():
    results = rc.get_industries(verbose=1)
    assert order_results(results, 'industryCode') == [
        '0', '111', '112', '114', '115', '211', '212', '213', '221', '236'
    ]


def test_get_industries_keyword():
    results = rc.get_industries(keyword='Fishing', codeLevel=6, verbose=1)
    assert order_results(results, 'industryCode') == [
        '114111', '114112', '114119'
    ]


def test_get_documents_jurisdiction():
    results = rc.get_documents(date=2020, jurisdictionID=44, verbose=1)
    assert order_results(results, 'documentID') == [
        3800000001, 3800000002, 3800000003, 3800000004, 3800000005,
        3800000006, 3800000007, 3800000008, 3800000009, 3800000010
    ]


def test_get_documents_missing_jurisdiction(capsys):
    results = rc.get_documents(date=2020, jurisdictionID=None, verbose=1)
    assert not results
    assert capsys.readouterr().out == (
        'Must include either "jurisdictionID and date" or "documentID."\n'
    )


def test_get_documents_document_id():
    results = rc.get_documents(date=2020, documentID=3800000001, verbose=1)
    assert results['documentReference'].values[0] == (
        'Agency 01, Title 01, Chapter 01'
    )


def test_get_versions():
    results = rc.get_versions(38, verbose=1)
    assert order_results(results, 'sourceName') == [
        'Occupation Data (dataset)', 'Occupation Data (dataset)',
        'RegData US 3.2 Annual (dataset)', 'RegData US 4.0 Annual (dataset)'
    ]


# Tests for get_values()
def test_get_document_values():
    results = rc.get_document_values(
        series=[1, 2], jurisdiction=20, date='2020-06-02', verbose=1
    )
    assert order_results(results, 'seriesValue', descending=True) == [
        1958601.0, 466414.0, 248869.0, 236149.0, 133169.0,
        103682.0, 98257.0, 90961.0, 90862.0, 90758.0
    ]


def test_get_reading_time():
    results = rc.get_reading_time(
        jurisdiction=20, date=[2015, 2021], documentType=1, verbose=1
    )
    assert order_results(results, 'seriesValue') == [
        '23 weeks, 4 days',
        '23 weeks, 7 hours',
        '31 weeks, 2 days, 2 hours'
    ]


def test_get_values_multiple_series():
    results = rc.get_values(
        series=[1, 2], jurisdiction='United States', date=1970, verbose=1
    )
    assert order_results(results, 'seriesValue') == [409520.0, 33588985.0]


def test_get_values_incorrect_series(capsys):
    results = rc.get_values(series=None, jurisdiction=38, date=2019)
    assert not results
    assert capsys.readouterr().out == (
        'Valid series ID required. Select from the following list:\n'
    )


def test_get_values_multiple_jurisdictions():
    results = rc.get_values(series=1, jurisdiction=[58, 59], date=2019)
    assert order_results(results, 'seriesValue') == [52569.0, 107063.0]


def test_get_values_multiple_jurisdiction_names():
    results = rc.get_values(
        series=1, jurisdiction=['Alaska', 'Alabama'], date=2019)
    assert order_results(results, 'seriesValue') == [52569.0, 107063.0]


def test_get_values_all_industries():
    results = rc.get_values(
        series=28, jurisdiction=58, date=2019, filtered=False
    )
    assert order_results(results, 'seriesValue', descending=True) == [
        2399.6540837686553, 2346.9849032768325,
        2231.579487334733, 1910.4039869066692,
        1858.660280573211, 1845.9105216636453,
        1756.3024117016612, 1272.998498038447,
        1214.762196061427, 1155.1694051386294
    ]


def test_get_values_multiple_industries():
    results = rc.get_values(
        series=28, jurisdiction=58, date=2019, industry=['22', '49', '50']
    )
    assert order_results(results, 'seriesValue') == [
        50.07550010907289, 649.0292048707197, 811.9319063696239
    ]


def test_get_values_one_industry():
    results = rc.get_document_values(
        series=28, jurisdiction=58, date='2019-05-15', industry='22'
    )
    assert order_results(results, 'seriesValue', descending=True) == [
        0.9902999997138977, 0.9789999723434448,
        0.9735000133514404, 0.9034000039100647,
        0.847599983215332, 0.6302000284194946,
        0.5533000230789185, 0.3864000141620636,
        0.3547999858856201, 0.3547999858856201
    ]


def test_get_values_4digit_industries():
    results = rc.get_values(
        series=28, jurisdiction=38, date=2019, filtered=False, industryLevel=4
    )
    assert order_results(results, 'seriesValue', descending=True) == [
        48819.60270605631,
        19666.03264030083,
        18530.05033682113,
        15972.102057352553,
        15476.846815471901,
        15132.83348125431,
        6506.98745361498,
        6490.635489263841,
        6228.529536121532,
        5282.724979804712
    ]


def test_get_values_incorrect_jurisdiction(capsys):
    results = rc.get_values(series=1, jurisdiction=None, date=2019)
    assert not results
    assert capsys.readouterr().out == 'Valid jurisdiction ID required.\n'


def test_get_values_date_range():
    results = rc.get_values(series=1, jurisdiction=38, date=[1970, 2019])
    assert order_results(results, 'seriesValue') == [
        409520.0, 420478.0, 456373.0, 475121.0, 505136.0,
        530148.0, 554052.0, 579879.0, 590779.0, 625123.0
    ]


def test_get_values_multiple_dates():
    results = rc.get_values(
        series=1, jurisdiction=38, date=[1970, 1980, 1990, 2000]
    )
    assert order_results(results, 'seriesValue') == [
        409520.0, 643935.0, 786512.0, 853667.0
    ]


def test_get_values_incorrect_dates(capsys):
    results = rc.get_values(series=1, jurisdiction=38, date=None, verbose=1)
    assert not results
    assert capsys.readouterr().out == (
        'Valid date is required. Select from the following list:\n'
        'API call: https://api.quantgov.org/seriesperiod?jurisdiction=38\n')


def test_get_values_country():
    results = rc.get_values(series=1, jurisdiction=38, date=2019, country=True)
    assert order_results(results, 'seriesValue') == [
        43940.0, 50646.0, 51925.0, 52569.0, 60086.0,
        63735.0, 70969.0, 78004.0, 82706.0, 92522.0
    ]


def test_get_values_agency():
    results = rc.get_values(series=13, jurisdiction=66, date=2021, agency=8777)
    assert order_results(results, 'seriesValue') == [4305.0]


def test_get_values_all_agencies():
    results = rc.get_values(
        series=13, jurisdiction=66, date=2021
    )
    assert order_results(results, 'seriesValue') == [
        0.0, 1.0, 1.0, 2.0, 2.0, 2.0, 4.0, 4.0, 5.0, 5.0


def test_get_values_multiple_agencies():
    results = rc.get_values(
        series=13, jurisdiction=66, date=2021, agency=[8777, 8813]
    )
    assert order_results(results, 'seriesValue') == [3311.0, 4305.0]


def test_get_values_version():
    results = rc.get_values(
        series=1, jurisdiction=38, date=2019, version=1, verbose=1
    )
    assert order_results(results, 'seriesValue') == [1078213.0]


def test_get_values_download():
    results = rc.get_values(
        series=13, jurisdiction=66, date=2021, agency=8777, download='test.csv'
    )
    assert not results
    assert os.path.exists('test.csv')
    os.remove('test.csv')


def test_get_values_incorrect_download(capsys):
    results = rc.get_values(
        series=13, jurisdiction=66, date=2021, agency=8777, download=True
    )
    assert not results
    assert capsys.readouterr().out == 'Valid outpath required to download.\n'


def test_get_values_error(capsys):
    results = rc.get_values(series=1, jurisdiction=38, date=1900)
    assert not results
    assert capsys.readouterr().out == (
        'WARNING: SeriesValue was not found for the specified parameters. '
        'Please check that you have selected the right combination of '
        'parameters.  When in doubt, please use the /periods endpoint to '
        'find out the combinations of series, jurisdiction, periods, '
        'agencies, document types for which there are data available.'
        '{parameters={jurisdiction=[US_UNITED_STATES], date=[1900], '
        'labelLevel=[3], agency=null, dateIsRange=false, filteredOnly=false, '
        'label=null, series=[SERIES_1], documentType=null, '
        'national=false, cluster=null}}\n')


# Tests for list_() functions
def test_list_document_types():
    results = rc.list_document_types()
    assert results['Regulation text All regulations'] == 1


def test_list_document_types_jurisdiction():
    results = rc.list_document_types(jurisdictionID=38)
    assert results['Regulation text All regulations'] == 1


def test_list_series():
    results = rc.list_series()
    assert results['Complexity Conditionals'] == 53


def test_list_dates():
    results = rc.list_dates(44)
    assert list(reversed(results))[:12] == [
        '2021-05-11', '2021',
        '2020-04-28', '2020',
        '2019-07-01', '2019',
        '2018-05-23', '2018'
    ]


def test_list_agencies():
    results = rc.list_agencies(jurisdictionID=66)
    assert results['wild animals'] == 8867


def test_list_agencies_keyword():
    results = rc.list_agencies(keyword='Education')
    assert results['california department of education (California)'] == 3576


def test_list_agencies_error(capsys):
    results = rc.list_agencies()
    assert not results
    assert capsys.readouterr().out == (
        'Must include either "jurisdictionID" or "keyword."\n')


def test_list_jurisdictions():
    results = rc.list_jurisdictions()
    assert results['Alabama'] == 59


def test_list_industries():
    results = rc.list_industries(codeLevel=6)
    assert results['Wood Container and Pallet Manufacturing (321920)'] == 1170


def test_list_industries_onlyID():
    results = rc.list_industries(codeLevel=6, onlyID=True)
    assert results['321920'] == 1170


def test_list_industries_keyword():
    results = rc.list_industries(codeLevel=4, keyword='fishing')
    assert results['Fishing (1141)'] == 126


def test_list_bea_industries():
    results = rc.list_industries(standard='BEA')
    assert results['Accommodation and food services (BEA) (79)'] == 1974
