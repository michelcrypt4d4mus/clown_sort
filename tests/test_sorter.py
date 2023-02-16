from image_namer.sorter import get_sort_folders

SIGNATURE = """Signature

Bank"""


def test_get_sort_folder():
    assert get_sort_folders('fuck crypto.com it sucks') == ['Crypto.com']
    assert get_sort_folders('fuck $cro it sucks') == ['Crypto.com']
    assert get_sort_folders('fuck #cro it sucks') == ['Crypto.com']
    assert get_sort_folders('fuck justinsuntron it sucks') == ['Justin Sun']
    assert get_sort_folders('fuck paoloardoino it sucks') == ['Tether']
    assert get_sort_folders('fuck bitfinex it sucks') == ['Tether']
    assert get_sort_folders('fuck bitfinexed it sucks') == []
    assert get_sort_folders('fuck $SI it sucks') == ['Silvergate']
    assert get_sort_folders('fuck okx it sucks') == ['OKX']
    assert get_sort_folders('fuck okcoin it sucks') == ['OKX']
    assert get_sort_folders('fuck okex it sucks') == ['OKX']
    assert get_sort_folders('fuck tron it sucks') == ['Tron']
    assert get_sort_folders('fuck tronchain it sucks') == ['Tron']
    assert get_sort_folders('fuck tron chain it sucks') == ['Tron']
    assert get_sort_folders('fuck @circle it sucks') == ['Circle']
    assert get_sort_folders('fuck #circle it sucks') == ['Circle']
    assert get_sort_folders('fuck USDC it sucks') == ['Circle']
    assert get_sort_folders('fuck $HUT it sucks') == ['Miners']
    assert get_sort_folders('fuck $CORZ it sucks') == ['Miners']
    assert get_sort_folders('fuck CoreScientific it sucks') == ['Miners']
    assert get_sort_folders('fuck Core Scientific it sucks') == ['Miners']
    assert get_sort_folders('fuck Seba Bank') == ['Banks']
    assert get_sort_folders('fuck $CUBI') == ['Banks']
    assert get_sort_folders(SIGNATURE) == ['SBNY']
