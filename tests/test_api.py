import os
import regcensus as rc


# UTILITY FUNCTIONS
def order_results(results, column, descending=False):
    if descending:
        return list(reversed(results[column].sort_values().tail(10).values))
    else:
        return list(results[column].sort_values().head(10).values)


# TEST FUNCTIONS
def test_get_series():
    results = rc.get_series(verbose=1)
    assert order_results(results, 'seriesID') == [1] * 10


def test_get_agencies():
    results = rc.get_agencies(jurisdictionID=38, verbose=1)
    assert order_results(results, 'agencyID') == [
        0, 1, 64, 65, 66, 67, 68, 69, 70, 71
    ]


def test_get_agencies_keyword():
    results = rc.get_agencies(keyword='Education', verbose=1)
    assert order_results(results, 'agencyID') == [
        225, 348, 375, 403, 475, 521, 539, 572, 595, 603
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


def test_get_documents():
    results = rc.get_documents(jurisdictionID=44, verbose=1)
    assert order_results(results, 'documentID') == [
        4441363, 4441364, 4441365, 4441366, 4441367,
        4441368, 4441369, 4441370, 4441371, 4441372
    ]


def test_get_versions():
    results = rc.get_versions(38, verbose=1)
    assert order_results(results, 'sourceName') == [
        'Occupation Data (dataset)', 'Occupation Data (dataset)',
        'RegData US 3.2 Annual (dataset)', 'RegData US 4.0 Annual (dataset)'
    ]


def test_get_document_values():
    results = rc.get_document_values(
        series=[1, 2], jurisdiction=20, date='2020-06-02', verbose=1
    )
    assert order_results(results, 'seriesValue', descending=True) == [
        1958601.0, 466414.0, 248869.0, 236149.0, 133169.0,
        103682.0, 98257.0, 90961.0, 90862.0, 90758.0
    ]


def test_get_values_multiple_series():
    results = rc.get_values(
        series=[1, 2], jurisdiction=38, date=1970, verbose=1
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


def test_get_values_all_industries():
    results = rc.get_values(
        series=9, jurisdiction=58, date=2019, filtered=False
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
        series=9, jurisdiction=58, date=2019, industry=['22', '49', '50']
    )
    assert order_results(results, 'seriesValue') == [
        50.07550010907289, 649.0292048707197, 811.9319063696239
    ]


def test_get_values_one_industry():
    results = rc.get_document_values(
        series=9, jurisdiction=20, date='2021-06-02', industry='42'
    )
    assert order_results(results, 'seriesValue', descending=True) == [
        0.9973999857902527, 0.9355999827384949,
        0.906499981880188, 0.7311000227928162,
        0.6862999796867371, 0.49320000410079956,
        0.2345000058412552, 0.21660000085830688,
        0.21389999985694885, 0.14239999651908875
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
    results = rc.get_values(series=1, jurisdiction=38, date=None)
    assert not results
    assert capsys.readouterr().out == (
        'Valid date is required. Select from the following list:\n')


def test_get_values_country():
    results = rc.get_values(series=1, jurisdiction=38, date=2019, country=True)
    assert order_results(results, 'seriesValue') == [
        43940.0, 51925.0, 52569.0, 60086.0, 63735.0,
        70969.0, 78676.0, 92522.0, 104562.0, 107063.0
    ]


def test_get_values_agency():
    results = rc.get_values(series=13, jurisdiction=38, date=2019, agency=195)
    assert order_results(results, 'seriesValue') == [62.0]


def test_get_values_all_agencies():
    results = rc.get_values(
        series=13, jurisdiction=38, date=2019
    )
    assert order_results(results, 'seriesValue') == [
        0.0, 0.0, 1.0, 1.0, 5.0, 18.0, 33.0, 34.0, 50.0, 59.0
    ]


def test_get_values_multiple_agencies():
    results = rc.get_values(
        series=13, jurisdiction=38, date=2019, agency=[111, 99]
    )
    assert order_results(results, 'seriesValue') == [34167.0, 91087.0]


def test_get_values_version():
    results = rc.get_values(
        series=1, jurisdiction=38, date=2019, version=1, verbose=1
    )
    assert order_results(results, 'seriesValue') == [1078213.0]


def test_get_values_download():
    results = rc.get_values(
        series=13, jurisdiction=38, date=2019, agency=195, download='test.csv'
    )
    assert not results
    assert os.path.exists('test.csv')
    os.remove('test.csv')


def test_get_values_incorrect_download(capsys):
    results = rc.get_values(
        series=13, jurisdiction=38, date=2019, agency=195, download=True
    )
    assert not results
    assert capsys.readouterr().out == 'Valid outpath required to download.\n'


def test_get_values_error(capsys):
    results = rc.get_values(series=1, jurisdiction=38, date=1900, verbose=1)
    assert not results
    assert capsys.readouterr().out == (
        'API call: https://api.quantgov.org/values'
        '?series=1&jurisdiction=38&date=1900&documentType=1\n'
        'WARNING: SeriesValue was not found for the specified parameters. '
        'Please check that you have selected the right combination of '
        'parameters.  When in doubt, please use the /periods endpoint to find '
        'out the combinations of series, jurisdiction, periods, agencies, '
        'document types for which there are data available.{parameters='
        '{jurisdiction=[US_UNITED_STATES], date=[1900], industry=null, '
        'agency=null, dateIsRange=false, filteredOnly=true, '
        'series=[SERIES_1], documentType=REGULATION_TEXT_ALL_REGULATIONS, '
        'documentID=null, national=false}}\n'
    )


def test_list_document_types():
    results = rc.list_document_types()
    assert results['Regulation text All regulations'] == 1


def test_list_series():
    results = rc.list_series()
    assert results['Complexity Conditionals'] == 53


def test_list_agencies():
    results = rc.list_agencies(jurisdictionID=38)
    assert results['Administrative Conference of the United States'] == 195


def test_list_agencies_keyword():
    results = rc.list_agencies(keyword='Education')
    assert results['California Department of Education'] == 770


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
    assert results['Wood Container and Pallet Manufacturing'] == 1170


def test_list_industries_keyword():
    results = rc.list_industries(codeLevel=4, keyword='fishing')
    assert results['Fishing'] == 126


def test_list_bea_industries():
    results = rc.list_industries(standard='BEA')
    assert results['Accommodation and food services (BEA)'] == 1974
