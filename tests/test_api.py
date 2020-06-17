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


def test_get_values():
    results = rc.get_values(series=1, jurisdiction=38, date=[1970, 2019])
    assert order_results(results, 'seriesValue') == [
        405647.0, 416532.0, 452114.0, 470561.0, 500133.0,
        524992.0, 548579.0, 572123.0, 581408.0, 615181.0
    ]
