from social_arsenal.config import Config
from social_arsenal.files.image_file import ImageFile
from social_arsenal.files.sortable_file import SortableFile

from tests.test_config import *

SIGNATURE = """Signature

Bank"""


def test_sort_file(three_of_swords_file, test_config):
    Config.dry_run = False
    Config.leave_in_place = True
    sortable_file = SortableFile(three_of_swords_file)
    assert(sortable_file.extracted_text() == three_of_swords_file.name)
    sortable_file.sort_file()
    Config.dry_run = True
    new_file = ImageFile(Config.sorted_screenshots_dir.joinpath('Art', three_of_swords_file.name))
    new_file.file_path.unlink()
    new_file.file_path.parent.rmdir()


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
    assert SortableFile.get_sort_folders('fuck $PI Wallet ') == ['Pi']
    assert SortableFile.get_sort_folders('fuck Arianna _ Simpson') == ['A16Z']
    assert SortableFile.get_sort_folders('fuck Arianna1Simpson') == ['A16Z']
    assert SortableFile.get_sort_folders('fuck DAI ') == ['MakerDAO']
    assert SortableFile.get_sort_folders('fuck #DAI ') == ['MakerDAO']
    assert SortableFile.get_sort_folders('fuck EOS ') == ['EOS']
    assert SortableFile.get_sort_folders('fuck B. Blumer ') == ['EOS']
    assert SortableFile.get_sort_folders('fuck $ADA ') == ['Cardano']
    assert SortableFile.get_sort_folders('fuck ADA coin') == ['Cardano']
    assert SortableFile.get_sort_folders('fuck CathieWood coin') == ['Cathie Wood']
    assert SortableFile.get_sort_folders('fuck ARKK coin') == ['Cathie Wood']
    assert SortableFile.get_sort_folders('fuck ARK Invest coin') == ['Cathie Wood']

    for hoo in ['Rexy Wang', 'Rexy Hoo', '#Hoo', 'Hoo Exchange', 'HooExchange']:
        assert SortableFile.get_sort_folders(f"fuck {hoo} yo") == ['Hoo']

    # Non-matches
    assert SortableFile.get_sort_folders("fuck Deltec'ed it sucks") == []
    assert SortableFile.get_sort_folders('fuck bitfinexed it sucks') == []
    assert SortableFile.get_sort_folders('fuck DAIS ') == []
    assert SortableFile.get_sort_folders('fuckEOS ') == []
    assert SortableFile.get_sort_folders('fuck ADAm ') == []
