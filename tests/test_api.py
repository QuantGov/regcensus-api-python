import pytest
import regcensus as rc


# UTILITY FUNCTIONS
def order_results(results, column):
    return list(results[column].sort_values().head(10).values)


# TEST FUNCTIONS
def test_get_series():
    results = rc.get_series()
    assert order_results(results, 'seriesCode') == [
        'NY.GDP.MKTP.CD', 'NY.GDP.MKTP.KD', 'NY.GDP.MKTP.KD.ZG',
        'NY.GDP.PCAP.KD.ZG', 'RG_OCL1000002A', 'RG_OCLI1000001A',
        'RG_QLTY1000470Z', 'RG_QLTY1000471Z',
        'RG_QLTY1000472Z', 'RG_QLTY1000473Z'
    ]


def test_get_agencies():
    results = rc.get_agencies()
    assert order_results(results, 'agencyID') == [
        0, 1, 64, 65, 66, 67, 68, 69, 70, 71
    ]


def test_get_jurisdictions():
    results = rc.get_jurisdictions()
    assert order_results(results, 'jurisdictionID') == [
        2, 4, 10, 11, 14, 15, 17, 20, 23, 24
    ]


def test_get_periods():
    results = rc.get_periods()
    assert order_results(results, 'seresYearID') == [
        102994, 102995, 102996, 102997, 102998,
        102999, 103000, 103001, 103002, 103003
    ]


def test_get_industries():
    results = rc.get_industries(jurisdictionID=38)
    assert order_results(results, 'industryCode') == [
        '0', '11', '111', '1111', '11111', '111110',
        '11112', '111120', '11113', '111130'
    ]


def test_get_documents():
    results = rc.get_documents(jurisdictionID=44)
    assert order_results(results, 'documentID') == [
        4441363, 4441364, 4441365, 4441366, 4441367,
        4441368, 4441369, 4441370, 4441371, 4441372
    ]


def test_get_values_multiple_series():
    results = rc.get_values(
        series=[1, 2], jurisdiction=38, date=1970, verbose=1
    )
    assert order_results(results, 'seriesValue') == [405647.0, 35420432.0]


def test_get_values_incorrect_series():
    results = rc.get_values(series=None, jurisdiction=38, date=2019)
    assert not results


def test_get_values_multiple_jurisdictions():
    results = rc.get_values(series=1, jurisdiction=[58, 59], date=2019)
    assert order_results(results, 'seriesValue') == [52569.0, 107063.0]


def test_get_values_all_industries():
    results = rc.get_values(
        series=9, jurisdiction=58, date=2019, industry='all', filtered=False
    )
    assert order_results(results, 'seriesValue') == [
        16.487800191811402, 28.080800290597836, 36.27130037093593,
        36.53810011051246, 40.113500030507566, 45.02970027324045,
        48.842899827621295, 50.17920009633963, 72.05880061667267,
        82.19629916545819
    ]


def test_get_values_multiple_industries():
    results = rc.get_values(
        series=9, jurisdiction=58, date=2019, industry=['111', '325', '326']
    )
    assert order_results(results, 'seriesValue') == [
        255.2682025779941, 649.0292048707197, 1858.660280573211
    ]


def test_get_values_one_industry():
    results = rc.get_values(
        series=9, jurisdiction=58, date=2019, industry='111', summary=False
    )
    # No document-level industry results exists for this jurisdiction
    assert not results


def test_get_values_incorrect_jurisdiction():
    results = rc.get_values(series=1, jurisdiction=None, date=2019)
    assert not results


def test_get_values_date_range():
    results = rc.get_values(series=1, jurisdiction=38, date=[1970, 2019])
    assert order_results(results, 'seriesValue') == [
        405647.0, 416532.0, 452114.0, 470561.0, 500133.0,
        524992.0, 548579.0, 572123.0, 581408.0, 615181.0
    ]


def test_get_values_multiple_dates():
    results = rc.get_values(
        series=1, jurisdiction=38, date=[1970, 1980, 1990, 2000]
    )
    assert order_results(results, 'seriesValue') == [
        405647.0, 633754.0, 772537.0, 853661.0
    ]


def test_get_values_incorrect_dates():
    results = rc.get_values(series=1, jurisdiction=38, date=None)
    assert not results


def test_get_values_country():
    results = rc.get_values(series=1, jurisdiction=38, date=2019, country=True)
    assert order_results(results, 'seriesValue') == [
        43940.0, 52569.0, 60086.0, 63203.0, 63735.0,
        70969.0, 78676.0, 92522.0, 104562.0, 107063.0
    ]


def test_get_values_agency():
    results = rc.get_values(series=91, jurisdiction=38, date=2019, agency=195)
    assert order_results(results, 'seriesValue') == [62.0]


def test_get_values_multiple_agencies():
    results = rc.get_values(
        series=91, jurisdiction=38, date=2019, agency=[111, 99]
    )
    assert order_results(results, 'seriesValue') == [34167.0, 91227.0]


def test_list_document_types():
    results = rc.list_document_types()
    assert results['All Regulations'] == 3


def test_list_series():
    results = rc.list_series()
    assert results['Conditionals'] == 135


def test_list_agencies():
    results = rc.list_agencies()
    assert results['Administrative Conference of the United States'] == 195


def test_list_jurisdictions():
    results = rc.list_jurisdictions()
    assert results['Alabama'] == 59


def test_list_industries():
    results = rc.list_industries(jurisdictionID=38)
    assert results['Wood Container and Pallet Manufacturing'] == '321920'
