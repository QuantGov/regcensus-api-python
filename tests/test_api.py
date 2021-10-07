import pytest
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
    assert order_results(results, 'seriesCode') == [
        'FRASE001', 'FRASE002', 'HC_THRESH', 'OL_THRESH',
        'Placeholder', 'Placeholder', 'Placeholder',
        'Placeholder', 'Placeholder', 'Placeholder']


def test_get_agencies():
    results = rc.get_agencies(38, verbose=1)
    assert order_results(results, 'agencyID') == [
        64, 65, 66, 67, 68, 70, 71, 72, 73, 74
    ]


def test_get_jurisdictions():
    results = rc.get_jurisdictions(verbose=1)
    assert order_results(results, 'jurisdictionID') == [
        2, 4, 10, 11, 14, 15, 17, 20, 23, 24
    ]


def test_get_periods():
    results = rc.get_periods(38, documentType=1, verbose=1)
    assert order_results(results, 'recordsAvailable', descending=True) == (
        [37004219] * 10
    )


def test_get_periods_one_series():
    results = rc.get_periods(20, documentType=1, seriesID=29, verbose=1)
    assert order_results(results, 'recordsAvailable') == [19844, 19844]


def test_get_industries():
    results = rc.get_industries(jurisdictionID=38, verbose=1)
    assert order_results(results, 'industryCode') == [
        '0', '10', '11', '11', '111', '1111',
        '11111', '111110', '11112', '111120'
    ]


def test_get_documents():
    results = rc.get_documents(jurisdictionID=44, verbose=1)
    assert order_results(results, 'documentID') == [
        4441363, 4441364, 4441365, 4441366, 4441367,
        4441368, 4441369, 4441370, 4441371, 4441372
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
        series=9, jurisdiction=58, date=2019, industry='all', filtered=False
    )
    assert order_results(results, 'seriesValue') == [
        16.487800191811402, 28.080800290597836, 32.408500283963804,
        36.27130037093593, 36.53810011051246, 36.72170047096006,
        40.113500030507566, 44.19190023323608, 45.02970027324045,
        48.842899827621295
    ]


def test_get_values_multiple_industries():
    results = rc.get_values(
        series=9, jurisdiction=58, date=2019, industry=['111', '325', '326']
    )
    assert order_results(results, 'seriesValue') == [266.73399629061896]


def test_get_values_one_industry():
    results = rc.get_values(
        series=9, jurisdiction=20, date='2020-06-02',
        industry='111', summary=False
    )
    assert order_results(results, 'seriesValue', descending=True) == [
        208.5117055773735, 177.00449323654175, 86.01110327243805,
        76.680001989007, 66.70080256462097, 61.46759942173958,
        58.94939732551575, 41.14539943635464, 36.53759956359863,
        33.51419833302498
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
    assert capsys.readouterr().out == 'Valid date is required.\n'


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
        series=13, jurisdiction=38, date=2019, agency='all'
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
        'API call: http://ec2-18-214-181-163.compute-1.amazonaws.com/values'
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
    results = rc.list_agencies(38)
    assert results['Administrative Conference of the United States'] == 195


def test_list_jurisdictions():
    results = rc.list_jurisdictions()
    assert results['Alabama'] == 59


def test_list_industries():
    results = rc.list_industries(jurisdictionID=38)
    assert results['Wood Container and Pallet Manufacturing'] == '321920'
