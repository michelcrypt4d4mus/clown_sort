from image_namer.files.sortable_file import SortableFile

SIGNATURE = """Signature

Bank"""


def test_get_sort_folder():
    assert SortableFile.get_sort_folders('fuck crypto.com it sucks') == ['Crypto.com']
    assert SortableFile.get_sort_folders('fuck crypto_com it sucks') == ['Crypto.com']
    assert SortableFile.get_sort_folders('fuck $cro it sucks') == ['Crypto.com']
    assert SortableFile.get_sort_folders('fuck #cro it sucks') == ['Crypto.com']
    assert SortableFile.get_sort_folders('fuck justinsuntron it sucks') == ['Justin Sun']
    assert SortableFile.get_sort_folders('fuck paoloardoino it sucks') == ['Tether']
    assert SortableFile.get_sort_folders('fuck bitfinex it sucks') == ['Tether']
    assert SortableFile.get_sort_folders('fuck paolo it sucks') == ['Tether']
    assert SortableFile.get_sort_folders('fuck Deltec it sucks') == ['Tether']
    assert SortableFile.get_sort_folders('fuck $SI it sucks') == ['Silvergate']
    assert SortableFile.get_sort_folders('fuck okx it sucks') == ['OKX']
    assert SortableFile.get_sort_folders('fuck okcoin it sucks') == ['OKX']
    assert SortableFile.get_sort_folders('fuck okex it sucks') == ['OKX']
    assert SortableFile.get_sort_folders('fuck tron it sucks') == ['Tron']
    assert SortableFile.get_sort_folders('fuck tronchain it sucks') == ['Tron']
    assert SortableFile.get_sort_folders('fuck tron chain it sucks') == ['Tron']
    assert SortableFile.get_sort_folders('fuck @circle it sucks') == ['Circle']
    assert SortableFile.get_sort_folders('fuck #circle it sucks') == ['Circle']
    assert SortableFile.get_sort_folders('fuck USDC it sucks') == ['Circle']
    assert SortableFile.get_sort_folders('fuck $HUT it sucks') == ['Miners']
    assert SortableFile.get_sort_folders('fuck $CORZ it sucks') == ['Miners']
    assert SortableFile.get_sort_folders('fuck CoreScientific it sucks') == ['Miners']
    assert SortableFile.get_sort_folders('fuck Core Scientific it sucks') == ['Miners']
    assert SortableFile.get_sort_folders('fuck Seba Bank') == ['Banks']
    assert SortableFile.get_sort_folders('fuck $CUBI') == ['Banks']
    assert SortableFile.get_sort_folders(SIGNATURE) == ['SBNY']
    assert SortableFile.get_sort_folders('fuck #SEN ') == ['Silvergate']
    assert SortableFile.get_sort_folders('fuck Swipe Wallet ') == ['Binance']

    for hoo in ['Rexy Wang', 'Rexy Hoo', '#Hoo', 'Hoo Exchange', 'HooExchange']:
        assert SortableFile.get_sort_folders(f"fuck {hoo} yo") == ['Hoo']

    # Non-matches
    assert SortableFile.get_sort_folders("fuck Deltec'ed it sucks") == []
    assert SortableFile.get_sort_folders('fuck bitfinexed it sucks') == []
