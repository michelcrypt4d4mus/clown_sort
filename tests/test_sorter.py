from image_namer.sorter import get_sort_folder

SIGNATURE = """Signature

Bank"""

def test_get_sort_folder():
    assert get_sort_folder('fuck crypto.com it sucks') == 'Crypto.com'
    assert get_sort_folder('fuck $cro it sucks') == 'Crypto.com'
    assert get_sort_folder('fuck #cro it sucks') == 'Crypto.com'
    assert get_sort_folder('fuck justinsuntron it sucks') == 'Justin Sun'
    assert get_sort_folder('fuck paoloardoino it sucks') == 'Tether'
    assert get_sort_folder('fuck bitfinex it sucks') == 'Tether'
    assert get_sort_folder('fuck bitfinexed it sucks') is None
    assert get_sort_folder('fuck $SI it sucks') == 'Silvergate'
    assert get_sort_folder('fuck okx it sucks') == 'OKX'
    assert get_sort_folder('fuck okcoin it sucks') == 'OKX'
    assert get_sort_folder('fuck okex it sucks') == 'OKX'
    assert get_sort_folder('fuck tron it sucks') == 'Tron'
    assert get_sort_folder('fuck tronchain it sucks') == 'Tron'
    assert get_sort_folder('fuck tron chain it sucks') == 'Tron'
    assert get_sort_folder('fuck @circle it sucks') == 'Circle'
    assert get_sort_folder('fuck #circle it sucks') == 'Circle'
    assert get_sort_folder('fuck USDC it sucks') == 'Circle'
    assert get_sort_folder('fuck $HUT it sucks') == 'Miners'
    assert get_sort_folder('fuck $CORZ it sucks') == 'Miners'
    assert get_sort_folder('fuck CoreScientific it sucks') == 'Miners'
    assert get_sort_folder('fuck Core Scientific it sucks') == 'Miners'
    assert get_sort_folder('fuck Seba Bank') == 'Banks'
    assert get_sort_folder('fuck $CUBI') == 'Banks'
    assert get_sort_folder(SIGNATURE) == 'SBNY'
