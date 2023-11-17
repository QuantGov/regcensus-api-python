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
    assert order_results(results, 'series_id') == [
        1, 2, 3, 4, 5, 6, 7, 8, 10, 11
    ]


def test_get_agencies():
    results = rc.get_agencies(jurisdictionID=38, verbose=1)
    assert order_results(results, 'agency_id') == [
        0, 9519, 9520, 9521, 9522, 9523, 9524, 9525, 9526, 9527
    ]


def test_get_agencies_keyword():
    results = rc.get_agencies(
        jurisdictionID=51, keyword='Education', verbose=1)
    assert order_results(results, 'agency_id') == [
       3548, 3573, 3574, 3575, 3576, 3577, 3578, 3579, 3580, 3581
    ]


def test_get_agencies_error(capsys):
    results = rc.get_agencies()
    assert not results
    assert capsys.readouterr().out == (
        'Must include either "jurisdictionID" or "keyword."\n')


def test_get_jurisdictions():
    results = rc.get_jurisdictions(verbose=1)
    assert order_results(results, 'jurisdiction_id') == [
        2, 4, 10, 11, 14, 15, 17, 20, 23, 24
    ]


def test_get_industries():
    results = rc.get_industries(verbose=1)
    assert order_results(results, 'label_code') == [
        '111', '112', '114', '115', '211', '212', '213', '221', '236', '311'
    ]


# def test_get_industries_keyword():
#     results = rc.get_industries(keyword='Fishing', labellevel=6, verbose=1)
#     assert order_results(results, 'label_code') == [
#         '114111', '114112', '114119'
#     ]


# def test_get_versions():
#     results = rc.get_versions(38, verbose=1)
#     assert order_results(results, 'source_name') == [
#         'Occupation Data (dataset)', 'Occupation Data (dataset)',
#         'RegData US 3.2 Annual (dataset)', 'RegData US 4.0 Annual (dataset)'
#     ]


# Tests for get_values()
def test_get_document_values():
    results = rc.get_document_values(
        series=[1, 2], jurisdiction=20, year=2020, verbose=1
    )
    assert order_results(results, 'restrictions', descending=True) == [
        27390, 11776, 3523, 2633, 1866, 1742, 1504, 1420, 1411, 1396
    ]


def test_get_reading_time():
    results = rc.get_reading_time(
        jurisdiction=20, year=[2015, 2021], documentType=1, verbose=1
    )
    assert order_results(results, 'series_value') == [
        '23 weeks, 4 days',
        '23 weeks, 7 hours',
        '31 weeks, 2 days, 2 hours'
    ]


def test_get_values_multiple_series():
    results = rc.get_values(
        series=[1, 2], jurisdiction='United States', year=1970, verbose=1
    )
    assert order_results(results, 'series_value') == [409520.0, 33588985.0]


def test_get_values_incorrect_series(capsys):
    results = rc.get_values(series=None, jurisdiction=38, year=2019)
    assert not results
    assert capsys.readouterr().out.split('\n')[0] == (
        'No data was found for these parameters. For this jurisdiction, consider the following:'
    )


def test_get_values_multiple_jurisdictions():
    results = rc.get_values(series=1, jurisdiction=[58, 59], year=2019)
    assert order_results(results, 'series_value') == [52569.0, 107063.0]


def test_get_values_multiple_jurisdiction_names():
    results = rc.get_values(
        series=1, jurisdiction=['Alaska', 'Alabama'], year=2019)
    assert order_results(results, 'series_value') == [52569.0, 107063.0]


# def test_get_values_all_industries():
#     results = rc.get_values(
#         series=28, jurisdiction=58, year=2019, filtered=False
#     )
#     assert order_results(results, 'series_value', descending=True) == [
#         3596.1658897194,
#         3594.9787034937,
#         2399.6540837687,
#         2346.9849032768,
#         2231.5794873347,
#         1910.4039869067,
#         1858.6602805732,
#         1845.9105216636,
#         1756.3024117017,
#         1449.754496272
#     ]


def test_get_values_multiple_industries():
    results = rc.get_values(
        series=28, jurisdiction=58, year=2019, label=[111, 325, 621]
    )
    assert order_results(results, 'series_value') == [
        16.4878001918,
        18.2179003567,
        28.033600058,
        28.0808002906,
        29.5395007168,
        31.0861005918,
        32.408500284,
        33.9612003003,
        35.1842004247,
        35.3924005719
    ]


def test_get_values_one_industry():
    results = rc.get_document_values(
        series=28, jurisdiction=58, year=2019, label=111
    )
    assert order_results(results, 'label_value', descending=True) == [
        0.9903, 0.979, 0.9735, 0.9034, 0.8476,
        0.6302, 0.5533, 0.3864, 0.3548, 0.3548
    ]


# def test_get_values_4digit_industries():
#     results = rc.get_values(
#         series=28, jurisdiction=38, year=2019, filtered=False, industryLevel=4
#     )
#     assert order_results(results, 'series_value', descending=True) == [
#         48819.60270605631,
#         19666.03264030083,
#         18530.05033682113,
#         15972.102057352553,
#         15476.846815471901,
#         15132.83348125431,
#         6506.98745361498,
#         6490.635489263841,
#         6228.529536121532,
#         5282.724979804712
#     ]


def test_get_values_incorrect_jurisdiction(capsys):
    results = rc.get_values(series=1, jurisdiction=None, year=2019)
    assert not results
    assert capsys.readouterr().out.split('\n')[0] == (
       'Valid jurisdiction ID required. Consider the following:'
    )


def test_get_values_year_range():
    results = rc.get_values(series=1, jurisdiction=38, year=[1970, 2019])
    assert order_results(results, 'series_value') == [
        409520.0, 420478.0, 456373.0, 475121.0, 505136.0,
        530148.0, 554052.0, 579879.0, 590779.0, 625123.0
    ]


def test_get_values_multiple_years():
    results = rc.get_values(
        series=1, jurisdiction=38, year=[1970, 1980, 1990, 2000]
    )
    assert order_results(results, 'series_value') == [
        409520.0, 643935.0, 785747.0, 853667.0
    ]


def test_get_values_incorrect_years(capsys):
    results = rc.get_values(series=1, jurisdiction=38, year=None, verbose=1)
    assert not results
    assert capsys.readouterr().out.split('\n')[0] == (
        'No data was found for these parameters. For this jurisdiction, consider the following:'
    )


# def test_get_values_country():
#     results = rc.get_values(series=1, jurisdiction=38, year=2019, country=True)
#     assert order_results(results, 'series_value') == [
#         43940.0, 50646.0, 51925.0, 52569.0, 60086.0,
#         63735.0, 70969.0, 78004.0, 82706.0, 92522.0
#     ]


def test_get_values_agency():
    results = rc.get_values(series=13, jurisdiction=66, year=2023, agency=24221)
    assert order_results(results, 'series_value') == [4198.0]


def test_get_values_all_agencies():
    results = rc.get_values(
        series=13, jurisdiction=66, year=2023
    )
    assert order_results(results, 'series_value') == [
        0.0, 1.0, 1.0, 2.0, 2.0, 2.0, 4.0, 4.0, 5.0, 5.0
    ]


def test_get_values_multiple_agencies():
    results = rc.get_values(
        series=13, jurisdiction=66, year=2023, agency=[24221, 24326]
    )
    assert order_results(results, 'series_value') == [275.0, 4198.0]


# def test_get_values_version():
#     results = rc.get_values(
#         series=1, jurisdiction=38, year=2019, version=1, verbose=1
#     )
#     assert order_results(results, 'series_value') == [1078213.0]


def test_get_values_download():
    results = rc.get_values(
        series=13, jurisdiction=66, year=2021, agency=8777, download='test.csv'
    )
    assert not results
    assert os.path.exists('test.csv')
    os.remove('test.csv')


def test_get_values_incorrect_download(capsys):
    results = rc.get_values(
        series=13, jurisdiction=66, year=2021, agency=8777, download=True
    )
    assert not results
    assert capsys.readouterr().out == 'Valid outpath required to download.\n'


def test_get_values_error(capsys):
    results = rc.get_values(series=1, jurisdiction=38, year=1900)
    assert not results
    assert capsys.readouterr().out.split('\n')[0] == (
        'No data was found for these parameters. For this jurisdiction, consider the following:'
    )


# Tests for list_() functions
def test_list_document_types():
    results = rc.list_document_types()
    assert results['Regulation text All regulations'] == 1


def test_list_document_types_jurisdiction():
    results = rc.list_document_types(jurisdictionID=38)
    assert results['Regulation text All regulations'] == 1


def test_list_series():
    results = rc.list_series()
    assert results['Conditionals'] == 53


def test_list_dates():
    results = rc.list_dates(44)
    assert list(reversed(results)) == [
        2023, 2022, 2021, 2020, 2019, 2018
    ]


def test_list_agencies():
    results = rc.list_agencies(jurisdictionID=66)
    assert results['wild animals'] == 24312


def test_list_agencies_keyword():
    results = rc.list_agencies(jurisdictionID=51, keyword='Education')
    assert results['california department of education (California)'] == 19967


def test_list_agencies_error(capsys):
    results = rc.list_agencies()
    assert not results
    assert capsys.readouterr().out == (
        'Must include either "jurisdictionID" or "keyword."\n')


def test_list_jurisdictions():
    results = rc.list_jurisdictions()
    assert results['Alabama'] == 59


def test_list_industries():
    results = rc.list_industries(labellevel=6)
    assert results['Wood Container and Pallet Manufacturing (321920)'] == 1170


def test_list_industries_onlyID():
    results = rc.list_industries(labellevel=6, onlyID=True)
    assert results['321920'] == 1170


# def test_list_industries_keyword():
#    results = rc.list_industries(labellevel=4, keyword='fishing')
#    assert results['Fishing (1141)'] == 126


# def test_list_bea_industries():
#     results = rc.list_industries(labelsource='BEA')
#     assert results['Accommodation and food services (BEA) (79)'] == 1974
