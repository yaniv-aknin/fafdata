import datetime
import urlobject

from fafscrape.fetch import construct_url

START_DATE = datetime.date(1970, 1, 1)
API_BASE = urlobject.URLObject('http://test')

def test_construct_url():
    built = construct_url('entity', ['include'], 'timefield', START_DATE, 10, api_base=API_BASE)
    expected = (
        'http://test/data/entity' # base
        '?page%5Bsize%5D=10'    # page size
        '&page%5Bnumber%5D=1'   # page number 1 (unspecified)
        '&page%5Btotals%5D=&'   # total pages should be unspecified (maybe cargo culted?)
        'filter=timefield%3Dge%3D1970-01-01T00%3A00%3A00Z&' # only end time filter on 'timefield'
        'include=include'   # inclusions (not comma delimeted)
        '&sort=timefield'         # sort (default ASC)
    )
    assert built == expected

    # page 2
    assert '&page%5Bnumber%5D=2' in construct_url('entity', ['include'], 'timefield', START_DATE, 10, page_number=2, api_base=API_BASE)

    # desc
    assert '&sort=-timefield' in construct_url('entity', ['include'], 'timefield', START_DATE, 10, page_number=1, sort='DESC', api_base=API_BASE)

    # two inclusions
    assert 'incA%2CincB' in construct_url('entity', ['incA', 'incB'], 'timefield', START_DATE, 10, api_base=API_BASE)
