# Sort images based on the extracted contents

from re import compile, IGNORECASE
from typing import List, Optional

JUSTIN_SUN = 'Justin Sun'

# If these strings are found, move the screenshot to that directory
SORT_SEARCH_STRINGS = [
    [compile('3ac|Three ?Arrows? Capital', IGNORECASE), '3ac'],
    [compile('a16z|andreessen|packym', IGNORECASE), 'A16Z'],
    [compile('aave', IGNORECASE), 'Aave'],
    [compile('aax', IGNORECASE), 'AAX'],
    [compile('Avax|avalanche', IGNORECASE), 'Avalanche'],
    [compile('\\$CUBI|Customers Ban(k|corp)|SEBA[^a-z]|Cross\\s?River', IGNORECASE), 'Banks'],
    [compile('binance|bnb|cz|bifinity|binaryx|billance|paysafe', IGNORECASE), 'Binance'],
    [compile('Blockchain8|tom ?emmer|ritchie ?torres|repritchie', IGNORECASE), 'Blockchain8'],
    [compile('BlockFi', IGNORECASE), 'BlockFi'],
    [compile('Cardano|\\$ADA', IGNORECASE), 'Cardano'],
    [compile('celsius|mashinsky', IGNORECASE), 'Celsius'],
    [compile('[@#]circle|usdc', IGNORECASE), 'Circle'],
    [compile('Coinbase|\\$COIN|brian[_ ]?armstrong', IGNORECASE), 'Coinbase'],
    [compile('crypto\\.?com|CDC|[$#]CRO|\\sCRO\\s', IGNORECASE), 'Crypto.com'],
    [compile('cryptomanran', IGNORECASE), 'CryptoManRan'],
    [compile('DCG|digital\\s*currency\\s*group|sh?ill?bert|Grayscale|GBTC', IGNORECASE), 'DCG'],
    [compile('El Salvador|Bukele', IGNORECASE), 'El Salvador'],
    [compile('FTX|SBF|Trabucco|Bankman|Ellison|Nishad|Alameda|Moonstone|friedberg', IGNORECASE), 'FTX'],
    [compile('Gemini|winklev', IGNORECASE), 'Gemini'],
    [compile('Genesis', IGNORECASE), 'Genesis'],
    [compile('huobi', IGNORECASE), 'Huobi'],
    [compile('justin\\s*sun|pgala', IGNORECASE), JUSTIN_SUN],
    [compile('kinesis|kvt', IGNORECASE), 'Kinesis'],
    [compile('kraken|payward', IGNORECASE), 'Kraken'],
    [compile('kucoin', IGNORECASE), 'KuCoin'],
    [compile('leroux', IGNORECASE), 'Paul LeRoux'],
    [compile('luna\\s|do kwon|stablekwon', IGNORECASE), 'TerraLuna'],
    [compile('makerdao', IGNORECASE), 'MakerDAO'],
    [compile('\\$MARA|marathon', IGNORECASE), 'Marathon'],
    [compile('marionawfal', IGNORECASE), 'Mario Nawfal'],
    [compile('bitcoin ?min(ing|er)|\\$(CORZ|IRIS|ARGO|HUT|HIVE|CAN|BLOK|BTCM)|Core ?Scientific|Iris\\s?Energy|Blockstream', IGNORECASE), 'Miners'],
    [compile('Nexo', IGNORECASE), 'Nexo'],
    [compile('oke?[cx]|star xu', IGNORECASE), 'OKX'],
    [compile('openpayd', IGNORECASE), 'OpenPayd'],
    [compile('\\$PI|PiNetwork', IGNORECASE), 'Pi'],
    [compile('\\$PVBC|BankProv', IGNORECASE), 'PVBC'],
    [compile('riot', IGNORECASE), 'RIOT'],
    [compile('SBNY|Signature\\s*Bank', IGNORECASE), 'SBNY'],
    [compile('\\$SI|Silvergate', IGNORECASE), 'Silvergate'],
    [compile('Solana|Serum', IGNORECASE), 'Solana'],
    [compile('tether|usdt|paolo|friedberg|bitfinex[^e]', IGNORECASE), 'Tether'],
    [compile('\\stron\\s|tron(block| )?chain|trondao', IGNORECASE), 'Tron'],
    [compile('tusd', IGNORECASE), 'TUSD'],
    [compile('Vauld', IGNORECASE), 'Vauld'],
    [compile('voyager', IGNORECASE), 'Voyager'],
    [compile('wirecard', IGNORECASE), 'Wirecard'],
]


def get_sort_folder(search_string: str) -> Optional[str]:
    return next((sss[1] for sss in SORT_SEARCH_STRINGS if sss[0].search(search_string)), None)


def get_sort_folders(search_string: Optional[str]) -> List[str]:
    """Find any folders that could be relevant."""
    if search_string is None:
        return []

    folders = [sss[1] for sss in SORT_SEARCH_STRINGS if sss[0].search(search_string)]

    if folders == ['Huobi', JUSTIN_SUN]:
        return [JUSTIN_SUN]
    else:
        return folders
