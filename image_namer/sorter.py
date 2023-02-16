"""
Sort images based on the extracted contents.
"""
import shutil
from pathlib import Path
from re import compile, IGNORECASE, MULTILINE
from typing import List, Optional, Union

from rich.panel import Panel
from rich.text import Text

from image_namer.config import DEFAULT_SCREENSHOTS_DIR, Config
from image_namer.util.filesystem_helper import copy_file_creation_time
from image_namer.util.logging import console, copied_file_log_message, log
from image_namer.util.string_helper import comma_join

JUSTIN_SUN = 'Justin Sun'
SORTED_DIR = DEFAULT_SCREENSHOTS_DIR.joinpath('Sorted')
PROCESSED_DIR = DEFAULT_SCREENSHOTS_DIR.joinpath('Processed')
MEMES = 'Memes'

# If these strings are found, move the screenshot to that directory
SORT_SEARCH_STRINGS = [
    [compile('3ac|Three ?Arrows? Capital', IGNORECASE), '3ac'],
    [compile('a16z|andreessen|packym', IGNORECASE), 'A16Z'],
    [compile('aave', IGNORECASE), 'Aave'],
    [compile('aax', IGNORECASE), 'AAX'],
    [compile('Avax|avalanche', IGNORECASE), 'Avalanche'],
    [compile('\\$CUBI|Customers Ban(k|corp)|SEBA[^a-z]|Cross\\s?River', IGNORECASE), 'Banks'],
    [compile('Bankless', IGNORECASE), 'Bankless'],
    [compile('binance|biconomy|bnb|cz|bifinity|binaryx|billance|changpeng|joselito|paysafe|SwipeIO|Swipe\\s?Wallet|keyway|key\\s?vision\\s?dev', IGNORECASE), 'Binance'],
    [compile('Bitstamp', IGNORECASE), 'Bitstamp'],
    [compile('Bitzlato', IGNORECASE), 'Bitzlato'],
    [compile('Blockchain8|tom ?emmer|ritchie ?torres|repritchie', IGNORECASE), 'Blockchain8'],
    [compile('BlockFi', IGNORECASE), 'BlockFi'],
    [compile('cryptomanran|100trillionUSD|nic[_ ]?carter|bitboy|basedkarbon|thecryptolark|adam\\s?back', IGNORECASE), 'Bros'],
    [compile('Cardano|\\$ADA', IGNORECASE), 'Cardano'],
    [compile('celsius|mashinsky|levity\\s?and\\s?love', IGNORECASE), 'Celsius'],
    [compile('[@#]circle|usdc', IGNORECASE), 'Circle'],
    [compile('Coinbase|\\$COIN|brian[_ ]?armstrong', IGNORECASE), 'Coinbase'],
    [compile('crypto[._]?com|CDC|[$#]CRO|\\sCRO\\s', IGNORECASE), 'Crypto.com'],
    [compile('DCG|digital\\s*currency\\s*group|sh?ill?bert|Grayscale|GBTC', IGNORECASE), 'DCG'],
    [compile('El Salvador|Bukele', IGNORECASE), 'El Salvador'],
    [compile('FTX|FTT|SBF|Trabucco|Bankman|Ellison|Nishad|Alameda|Moonstone|friedberg', IGNORECASE), 'FTX'],
    [compile('Gemini|winklev', IGNORECASE), 'Gemini'],
    [compile('Genesis|Michael\\s?Moro', IGNORECASE), 'Genesis'],
    [compile('Hex\\s|[#$]Hex|Pulsechain|Richard\\s?Heart', IGNORECASE), 'Hex'],
    [compile('Hoo\\s?Exchange|#Hoo\\s|Rexy\\s?(Hoo|Wang)', IGNORECASE), 'Hoo'],
    [compile('huobi', IGNORECASE), 'Huobi'],
    [compile('justin\\s*sun|pgala|sunswap', IGNORECASE), JUSTIN_SUN],
    [compile('kinesis|kvt|ABX|KAG', IGNORECASE), 'Kinesis'],
    [compile('kraken|payward', IGNORECASE), 'Kraken'],
    [compile('kucoin', IGNORECASE), 'KuCoin'],
    [compile('lazarus|North\\sKorea', IGNORECASE), 'North Korea'],
    [compile('leroux', IGNORECASE), 'Paul LeRoux'],
    [compile('luna\\s|do kwon|stablekwon', IGNORECASE), 'TerraLuna'],
    [compile('makerdao', IGNORECASE), 'MakerDAO'],
    [compile('\\$MARA|marathon', IGNORECASE), 'Marathon'],
    [compile('marionawfal', IGNORECASE), 'Mario Nawfal'],
    [compile('\\smeme', IGNORECASE), 'Memes'],
    [compile('bitcoin ?min(ing|er)|\\$(CORZ|IRIS|ARGO|HUT|HIVE|CAN|BLOK|BTCM)|Core ?Scientific|Iris\\s?Energy|Blockstream', IGNORECASE), 'Miners'],
    [compile('Saylor|MSTR', IGNORECASE), 'MSTR'],
    [compile('Nexo', IGNORECASE), 'Nexo'],
    [compile('oke?[cx]|star xu', IGNORECASE), 'OKX'],
    [compile('openpayd|CFD\\s?Team', IGNORECASE), 'OpenPayd'],
    [compile('OpenSea', IGNORECASE), 'OpenSea'],
    [compile('paxos', IGNORECASE), 'Paxos'],
    [compile('payrnet|railsr|railsbank', IGNORECASE), 'Payrnet'],
    [compile('\\$PI|PiNetwork', IGNORECASE), 'Pi'],
    [compile('Prime[-\\s]?Trust', IGNORECASE), 'Prime Trust'],
    [compile('PVBC|BankProv', IGNORECASE), 'PVBC'],
    [compile('revolut\\s', IGNORECASE), 'Revolut'],
    [compile('riot', IGNORECASE), 'RIOT'],
    [compile('Safemoon', IGNORECASE), 'Safemoon'],
    [compile('SBNY|Signature[-\\s]*Bank|Signet', IGNORECASE), 'SBNY'],
    [compile('\\$SI|Silvergate|Alan\\s?Lane|Eisele|[\\s#]SEN\\s', IGNORECASE), 'Silvergate'],
    [compile('Solana|Serum', IGNORECASE), 'Solana'],
    [compile('tether|usdt|paolo|friedberg|hoegner|Noble\\s?Bank|Deltec[^\']|bitfinex[^e]', IGNORECASE), 'Tether'],
    [compile('Transactive', IGNORECASE), 'Transactive Systems UAB'],
    [compile('TUSD|TrueUSD', IGNORECASE), 'TrueUSD'],
    [compile('\\stron\\s|tron(block| )?chain|trondao', IGNORECASE), 'Tron'],
    [compile('tusd', IGNORECASE), 'TUSD'],
    [compile('Vauld', IGNORECASE), 'Vauld'],
    [compile('voyager', IGNORECASE), 'Voyager'],
    [compile('wintermute', IGNORECASE), 'wintermute'],
    [compile('wirecard', IGNORECASE), 'Wirecard'],
]


def get_sort_folders(search_string: Optional[str]) -> List[str]:
    """Find any folders that could be relevant."""
    if search_string is None:
        return []

    folders = [sss[1] for sss in SORT_SEARCH_STRINGS if sss[0].search(search_string)]

    if folders == ['Huobi', JUSTIN_SUN]:
        return [JUSTIN_SUN]
    else:
        return folders


def sort_file_by_ocr(image_file: 'ImageFile', dry_run: bool = True) -> None:
    """Sort the file to destination_dir subdir."""
    console.print(image_file)
    sort_folders = get_sort_folders(image_file.ocr_text())

    if len(sort_folders) == 0:
        console.print('No sort folders! ', style='magenta dim')
        image_file.set_image_description_exif_as_ocr_text(dry_run=dry_run)
    else:
        console.print(Text('FOLDERS: ', style='magenta') + comma_join(sort_folders))
        possible_old_file = SORTED_DIR.joinpath(image_file.basename)

        if possible_old_file.is_file():
            console.print(Text(f"WARNING: Deleting unsorted file '{possible_old_file}'...", style='red'))
            possible_old_file.unlink()

        for sort_folder in sort_folders:
            image_file.set_image_description_exif_as_ocr_text(sort_folder, dry_run=dry_run)

    _move_to_processed_dir(image_file.file_path, dry_run=dry_run)


def get_sort_destination(basename: str, subdir: Optional[Union[Path, str]] = None) -> Path:
    """Get the destination folder. """
    if subdir is None:
        destination_dir = Config.sorted_screenshots_dir
    else:
        destination_dir = Config.sorted_screenshots_dir.joinpath(subdir)

        if not destination_dir.is_dir():
            log.warning(f"Creating subdirectory '{destination_dir}'...")
            destination_dir.mkdir()

    return destination_dir.joinpath(basename)


def sort_file_by_filename(file_path: Path, dry_run: bool = True) -> None:
    console.line(1)
    console.print(Panel(file_path.name, expand=False, style='cyan'))
    sort_folders = get_sort_folders(str(file_path))

    if len(sort_folders) == 0:
        console.print('No sort folders! Not copying...', style='dim')
        return
    else:
        destination_paths = [get_sort_destination(file_path.name, subdir) for subdir in sort_folders]

    for destination_path in destination_paths:
        if dry_run:
            console.print(f"Dry run, not copying to '{destination_path}'...")
        else:
            shutil.copy(file_path, destination_path)
            copy_file_creation_time(file_path, destination_path)

        console.print(copied_file_log_message(file_path.name, destination_path))

    _move_to_processed_dir(file_path, dry_run=dry_run)


def _move_to_processed_dir(file_path: Path, dry_run: bool = True) -> None:
    processed_file_path = Config.processed_screenshots_dir.joinpath(file_path.name)

    if dry_run:
        console.print(
            f"Not moving file to {Config.sorted_screenshots_dir} because it's a dry run...",
            style='dim'
        )
    elif file_path == processed_file_path:
        console.print("Not moving file because it's the same location...", style='dim')
    else:
        console.print(f"Moving '{file_path}' to '{processed_file_path}'", style='dim')
        shutil.move(file_path, processed_file_path)
