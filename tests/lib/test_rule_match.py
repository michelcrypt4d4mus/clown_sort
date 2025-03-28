from typing import List

from clown_sort.lib.rule_match import RuleMatch

from tests.test_config import *

SIGNATURE = """Signature

Bank"""


def test_get_rule_matches():
    check_folders('fuck Arianna _ Simpson', ['A16Z'])
    check_folders('fuck Arianna1Simpson', ['A16Z'])
    check_folders('fuck #AAXExchange', ['AAX'])
    check_folders('fuck Seba Bank', ['Banks'])
    check_folders('fuck Swipe Wallet ', ['Binance'])
    check_folders('fuck the brock coin', ['Blockchain Capital', 'Friedlander Group', 'Tether'])
    check_folders('fuck the brockpierce coin', ['Blockchain Capital', 'Brock Pierce', 'Friedlander Group', 'Tether'])
    check_folders('fuck Ted Cruz ', ['Blockchain8'])
    check_folders('fuck $ADA ', ['Cardano'])
    check_folders('fuck ADA coin', ['Cardano'])
    check_folders('fuck InvestBybit coin', ['Binance', 'Bybit'])
    check_folders('fuck Bybit coin', ['Bybit'])
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
    check_folders('fuck Cronos chain it sucks', ['Crypto.com'])
    check_folders('fuck $CUBI', ['CUBI'])
    check_folders('fuck Block.One ', ['EOS'])
    check_folders('fuck BlockOne ', ['EOS'])
    check_folders('fuck BrendanBlumer', ['EOS'])
    check_folders('fuck B. Blumer ', ['EOS'])
    check_folders('fuck EOS ', ['EOS'])
    check_folders('fuck Wagestream ', ['Fintech'])
    check_folders('fuck C2f0 ', ['Fintech'])
    check_folders('fuck Grasshopper ', ['Fintech'])
    check_folders('fuck Chimebank ', ['Fintech'])
    check_folders('fuck $FXS ', ['Frax'])
    check_folders('fuck frxUSD ', ['Frax'])
    check_folders('fuck @happydelio', ['Haru Invest'])
    check_folders('fuck Haru', ['Haru Invest'])
    check_folders('fuck justinsuntron it sucks', ['Justin Sun'])
    check_folders('fuck DAI ', ['MakerDAO'])
    check_folders('fuck #DAI ', ['MakerDAO'])
    check_folders('fuck Matthew  Roszak he sucks', ['Matthew Roszak'])
    check_folders('fuck MatthewRoszak he sucks', ['Matthew Roszak'])
    check_folders('fuck $MCB', ['Metropolitan Commercial Bank'])
    check_folders('fuck $HUT it sucks', ['Miners'])
    check_folders('fuck HUT8 it sucks', ['Miners'])
    check_folders('fuck $CORZ it sucks', ['Miners'])
    check_folders('fuck CoreScientific it sucks', ['Miners'])
    check_folders('fuck Core Scientific it sucks', ['Miners'])
    check_folders('fuck Michael Saylor he sucks', ['MSTR'])
    check_folders('fuck MichaelSaylor he sucks', ['MSTR'])
    check_folders('fuck okx it sucks', ['OKX'])
    check_folders('fuck okcoin it sucks', ['OKX'])
    check_folders('fuck okex it sucks', ['OKX'])
    check_folders('fuck $PI Wallet ', ['Pi'])
    check_folders("CFTC’s Division of Clearing and Risk Issues.pdf", ['SEC'])
    check_folders('fuck Gary Gensler coin', ['SEC'])
    check_folders('fuck @SECgov coin', ['SEC'])
    check_folders('fuck the SEC coin', ['SEC'])
    check_folders(SIGNATURE, ['Signature Bank'])
    check_folders('fuck #Signet', ['Signature Bank'])
    check_folders('fuck $SI it sucks', ['Silvergate'])
    check_folders('fuck #SEN ', ['Silvergate'])
    check_folders('fuck XLM ', ['Stellar'])
    check_folders('fuck SynapseFi ', ['Synapse'])
    check_folders('fuck Telegram ', ['Telegram'])
    check_folders('fuck Pavel Durov ', ['Telegram'])
    check_folders('fuck PavelDurov ', ['Telegram'])
    check_folders('fuck #Ton', ['Telegram'])
    check_folders('fuck Toncoin', ['Telegram'])
    check_folders('fuck paoloardoino it sucks', ['Tether'])
    check_folders('fuck rohn monroe he sucks', ['Tether'])
    check_folders('fuck bitfinex it sucks', ['Tether'])
    check_folders('fuck Digfinex it sucks', ['Tether'])
    check_folders('fuck iFinex it sucks', ['Tether'])
    check_folders('fuck paolo it sucks', ['Tether'])
    check_folders('fuck Deltec it sucks', ['Tether'])
    check_folders('fuck tron it sucks', ['Tron'])
    check_folders('fuck tronchain it sucks', ['Tron'])
    check_folders('fuck tron chain it sucks', ['Tron'])
    check_folders('cs I TGBP_implementat (ethereum: Q@xaa912f203dcc1f5b6f862c0e0da3254cfc08a1d9) I I FUNCTIONS - allowance(owner: address, spender: address) -_ _uint25', ['TrueUSD'])
    check_folders('fuck @jason dipshit coin', ['VCs'])
    check_folders('fuck founders fund coin', ['VCs'])
    check_folders('fuck 0xe85c4D91DC0D9dB0a59300e18acFA2A498419E83 coin', ['Wallet Addresses Ethereum'])
    check_folders('fuck TXQmDK38s5YHjJDF7xuGpJtGTH9WeDVpk5 coin', ['Wallet Addresses Tron'])

    for hoo in ['Rexy Wang', 'Rexy Hoo', '#Hoo', 'Hoo Exchange', 'HooExchange']:
        check_folders(f"fuck {hoo} yo", ['Hoo'])


def test_non_rule_matches():
    check_folders("fuck Deltec'ed it sucks", [])
    check_folders('fuck bitfinexed it sucks', [])
    check_folders('fuck DAIS ', [])
    check_folders('fuckEOS ', [])
    check_folders('fuck ADAm ', [])
    check_folders('fuck the SECretary coin', [])


def check_folders(search_string: str, expected_folders: List[str]) -> None:
    folders = [rm.folder for rm in RuleMatch.get_rule_matches(search_string)]
    assert folders == expected_folders
