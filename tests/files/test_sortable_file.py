from typing import List

from clown_sort.config import Config
from clown_sort.files.image_file import ImageFile
from clown_sort.files.sortable_file import SortableFile

from tests.test_config import *

SIGNATURE = """Signature

Bank"""


def test_sort_file(three_of_swords_file, turn_off_dry_run):
    sortable_file = SortableFile(three_of_swords_file)
    assert(sortable_file.extracted_text() == three_of_swords_file.name)
    sortable_file.sort_file()
    new_file = ImageFile(Config.sorted_screenshots_dir.joinpath('Art', three_of_swords_file.name))
    new_file.file_path.unlink()
    new_file.file_path.parent.rmdir()


def test_get_sort_folder():
    check_folders('fuck Arianna _ Simpson', ['A16Z'])
    check_folders('fuck Arianna1Simpson', ['A16Z'])
    check_folders('fuck #AAXExchange', ['AAX'])
    check_folders('fuck Seba Bank', ['Banks'])
    check_folders('fuck Swipe Wallet ', ['Binance'])
    check_folders('fuck $ADA ', ['Cardano'])
    check_folders('fuck ADA coin', ['Cardano'])
    check_folders('fuck CathieWood coin', ['Cathie Wood'])
    check_folders('fuck ARKK coin', ['Cathie Wood'])
    check_folders('fuck ARK Invest coin', ['Cathie Wood'])
    check_folders('fuck @circle it sucks', ['Circle'])
    check_folders('fuck #circle it sucks', ['Circle'])
    check_folders('fuck USDC it sucks', ['Circle'])
    check_folders('fuck crypto.com it sucks', ['Crypto.com'])
    check_folders('fuck crypto_com it sucks', ['Crypto.com'])
    check_folders('fuck $cro it sucks', ['Crypto.com'])
    check_folders('fuck #cro it sucks', ['Crypto.com'])
    check_folders('fuck $CUBI', ['CUBI'])
    check_folders('fuck EOS ', ['EOS'])
    check_folders('fuck B. Blumer ', ['EOS'])
    check_folders('fuck $FXS ', ['Frax'])
    check_folders('fuck frxUSD ', ['Frax'])
    check_folders('fuck the brock coin', ['Blockchain Capital', 'Friedlander Group', 'Tether'])
    check_folders('fuck the brockpierce coin', ['Blockchain Capital','Friedlander Group', 'Tether'])
    check_folders('fuck justinsuntron it sucks', ['Justin Sun'])
    check_folders('fuck DAI ', ['MakerDAO'])
    check_folders('fuck #DAI ', ['MakerDAO'])
    check_folders('fuck $MCB', ['Metropolitan Commercial Bank'])
    check_folders('fuck $HUT it sucks', ['Miners'])
    check_folders('fuck $CORZ it sucks', ['Miners'])
    check_folders('fuck CoreScientific it sucks', ['Miners'])
    check_folders('fuck Core Scientific it sucks', ['Miners'])
    check_folders('fuck okx it sucks', ['OKX'])
    check_folders('fuck okcoin it sucks', ['OKX'])
    check_folders('fuck okex it sucks', ['OKX'])
    check_folders('fuck $PI Wallet ', ['Pi'])
    check_folders('fuck Gary Gensler coin', ['SEC'])
    check_folders('fuck @SECgov coin', ['SEC'])
    check_folders('fuck the SEC coin', ['SEC'])
    check_folders(SIGNATURE, ['Signature Bank'])
    check_folders('fuck #Signet', ['Signature Bank'])
    check_folders('fuck $SI it sucks', ['Silvergate'])
    check_folders('fuck #SEN ', ['Silvergate'])
    check_folders('fuck paoloardoino it sucks', ['Tether'])
    check_folders('fuck rohn monroe he sucks', ['Tether'])
    check_folders('fuck bitfinex it sucks', ['Tether'])
    check_folders('fuck paolo it sucks', ['Tether'])
    check_folders('fuck Deltec it sucks', ['Tether'])
    check_folders('fuck tron it sucks', ['Tron'])
    check_folders('fuck tronchain it sucks', ['Tron'])
    check_folders('fuck tron chain it sucks', ['Tron'])
    check_folders('fuck @jason dipshit coin', ['VCs'])
    check_folders('fuck founders fund coin', ['VCs'])

    for hoo in ['Rexy Wang', 'Rexy Hoo', '#Hoo', 'Hoo Exchange', 'HooExchange']:
        check_folders(f"fuck {hoo} yo", ['Hoo'])

    # Non-matches
    check_folders("fuck Deltec'ed it sucks", [])
    check_folders('fuck bitfinexed it sucks', [])
    check_folders('fuck DAIS ', [])
    check_folders('fuckEOS ', [])
    check_folders('fuck ADAm ', [])
    check_folders('fuck the SECretary coin', [])


def check_folders(search_string: str, expected_folders: List[str]) -> None:
    folders = [rm.folder for rm in SortableFile.get_sort_folders(search_string)]
    assert folders == expected_folders
