import pytest

from clown_sort.filename_extractor import FilenameExtractor
from clown_sort.files.image_file import ImageFile

WUBLOCKCHAIN_TWEET_TEXT = """wu

BLOCKC}*AIN

Wu Blockchain @ @WuBlockchain - 21m see
a16z voted 15 million UNI against the final proposal to deploy Uniswap V3
on BNB Chain proposed by OxPlasma Labs. The proposal uses Wormhole
as a cross-chain bridge. a16z opposes the use of Wormhole and supports
the use of LayerZero. tally.xyz/gov/uniswap/pr...

O 8 tl 7 Q 35 it 6,634 4,"""


REPLY_TWEET_TEXT = """gedaominas @ = @ @gedaominas - 6h

Replying to @tier10k

The same thing happened with their SEPA transfers a couple of years ago.
Just because Binance isn't licensed for money institution activities, they
have to rely on 3rd parties and such parties in this industry have a
tendency to change. Not a big deal if you asked me.

QO 5 td 2 QO 34 ili 14.5K 4

Bitrashi Nakedfoto @Stevi Wunda- 5h
Replying to @gedaominas and @tier10k
Why isn’t Binance licensed for money institution activities?

You don’t think it’s a big deal that they use straw men as fronts for their
business?

I think it reeks of nefarious activity that they keep a layer of separation
between themselves and their customers.

O4 vr 9 4 tht 618 4"""


TIMESTAMPED_TWEET_TEXT = """>
a db @
‘ap’ @tier10k

[DB] SEC Probe Into Kraken at an Advanced Stage
and Could Lead to a Settlement in Coming Days:
Bloomberg

3:55 PM - Feb 8, 2023 - 77.3K Views"""


GABOR_TWEET_TEXT = """fee) Gabor Gurbacs @

@gaborgurbacs

Looking at the facts, Tether (USDT) is the most
trusted stablecoin globally since it continues to be
the #1 stablecoin by market cap and trades 10x the
daily volume of USDC. Sad to see Coinbase behave
like this when an exchange is supposed to remain
impartial.

© Coinbase % @coinbase - Feb 3
Stability = Confidence

Make the switch to the digital dollar, and experience zero fees when you
convert from USDT to USDC.
coinbase.com/blog/switch-to...

6:47 AM - Feb 4, 2023 - 48K Views

20 Retweets 7QuoteTweets 107 Likes

Oo v wv)

o>

Tweet your reply

Replying to @gaborgurbacs

| think this Coinbase media campaign will have the opposite effect. USDC
users will learn about USDT and convert to USDT as they question the
motivations and rationale of this campaign. After-all, if Coinbase and
Coinbase users don’t like USDT why did they list USDT? ;)

fee} Gabor Gurbacs @ @gaborgurbacs - Feb 4

O 5 Td 3 QO 2 tht 2,884 &

Gabor Gurbacs @ @gaborgurbacs - Feb 4 oe
On professionalism: It’s good to see @paoloardoino, @bitcoinlawyer & the
Tether team work and act like professionals. Tether works with both

partners and competitors in a respectful and collaborative manner. Tether
cares about the industry. After all: Rising tides lift all boats."""


TWITTER_CZ = """(te CZ @ Binance @ @cz_binance - Nov 6
7) Binance always encourages collaboration between industry players.
i: Regarding any speculation as to whether this is a move against a
competitor, it is not. Our industry is in it’s nascency and every time a
project publicly fails it hurts every user and every platform. 3/4

3 Tl 493 © 5,626 ath"""


BAD_OCR_TWEET = """af

Martin Farber @ASYB111 - tih
Replying to @cz_binance
Any updates on send cash feature? It is temporarily disabled.

1o) td iv) ily 399 a“"""


REDDIT_POST = """© r/binance - Posted by u/TheLostWander_er 13 hours ago

send cash feature is temporarily disable.

I was trying to withdraw cash since last week and I am seeing this message every time I try the send
cash feature. Am I the only one getting this? What else can I do to send cash?

i) 5 Comments Award Vad Share im Save"""


REDDIT_REPLIES = """3 Fluffyhobbit - 5 days ago - edited 5 days ago

Option 4. 80% of us send crypto to cold storage and binance doesn't skip a beat
Edit: forgot to put in doesn't*

> 22 tb ) Reply Give Award Share Report Save Follow

2 LeftAct8968 OP - 5 days ago

I love it. That’s my plan! Haha

> adh i) Reply Give Award Share Report Save Follow

BS Fluffyhobbit - 5 days ago

I feel confident binance can handle our $$ moving out all at once since they just had some
billion dollar transfer days & didn't pause transfers @ @

> 6 ib i) Reply Give Award Share Report Save Follow

a ry DisIsGoodForBitcoin - 5 days ago

& MatrixName - 4 days ago

Exactly!
OP believes that little 1B worth of Voyager assets would impact Binance lol

People withdrew over 6B in days on Binance with zero impact.

> adh ) Reply Give Award Share Report Save Follow"""


REDDIT_R_CRYPTOCURRENCY_REPLY = """Si Roberto9410 i} 17.8k - 13 hr. ago
Platinum | QC: CC 831.
Wow the downfall of BUSD is something to see

<p. 1<4 Giveaward Share Report Save Follow

@ FacundoGabrielGuzman © 0-12hr. ago

Platinum | QC: CC 29, BTC 21
It won't be good. It would send bitcoin to the Mariana Trench
<p.0 <> Giveaward Share Report Save Follow

'S) Bunnywabbit13 i} 1.8k - 9 hr. ago

Platinum | QC: CC 170 | ADA 10 | r/AMD 20

Nothing bad will really happen as long as the peg is secured and everyone gets their
money back.

People will just change from BUSD to other stables.

<p. 1<4 Giveaward Share Report Save Follow
"""


REDDIT_DEBIT_COMMENT = """Spmhealy_ADA OP - 21 min. ago

I can't use Debit for anything. Usually I can just buy with Debit or Google Play (both
show my Debit card number)

Can't use Debit to deposit fiat. Don't even see that as an option. I see link bank (which I
picked for instant use) ACH (3-5 day to clear) or Wire Transfer 1-2 days.

Using the first option of "Link Bank", via Routing/Account through Plaid, I can deposit
fiat directly into my account ($20 minimum. Instant use. Of course 7 days till it can be


4} vote <> C) Reply Give Award Share Report Save Follow"""


REDDIT_POST_2 = """c Posted by u/cho0n22 2 days ago
0 Thave the blue card and it's not working
v

My blue card isn't being accepted for online payments, have not tried in person yet.
Is it because I have nothing staked?

Says to check card details.

i) 22 Comments Award lad Share in Save"""


REVEDDIT_THREAD = """[+]_show filters

The account review period does not seem to end !!! my assets are blocked forever. (self.binance)
submitted 2 days, 13 hours ago by F150Rraptor to /r/binance (888.2k)

| by reddit (spam) Q)

Qcomments_ reddit other-discussions subreddit-index message mods _ op-focus 4

 before archival, within 13 seconds

Reveddit Real-Time can notify you when your content is removed.

archive status (?)
comments’ 1 week, 2 days until overwrite

Check if your account has any removed comments.
view my removed comments

@  ‘/reveddit"""


DUNE_ANALYTICS = """Query results Alameda (Tagged and Rumored) Ethereum Wallets All Time In and Out a) @crypto_oracle

symbol inbound_usd inbound_txn_count inbound_avg_usd_per_txn outbound_usd outbound_txn_count outbound_avg_usd_per_txn gross_usd_volume
UST ic} ic} ic} 39,043 ,282,243,898,941,440 32 1,220,102,570,121,841,920 39,043 ,282,243,898,941,440
UST 18,144,219,611,167,979,520 39 465 , 236,400, 286,358,464 66,919 , 371 99 675 ,953 18,144,219,611, 234,897,920
USDC 10,457 ,122,051 1,406 7 , 437,498 53,826,674, 384 4,282 12,570,452 64,283 ,796,435
USDC 27 ,609 ,877,275 2,085 13,242,147 ic} ic} ic} 27 ,609 ,877,275
USDT 6 ,412,994,982 2,442 2,626,124 18,405 ,687,731 3,372 5,458,389 24,818 ,682,712
BUSD 5,194,152,635 830 6,258,015 14,142 ,335,576 1,770 7,990,020 19, 336,488,211
FIT 1,701, 881,033 425 4,004,426 11,554,699,961 386 29,934,456 13, 256,580,994
USDC ic} ic} ic} 9, 758,805,985 695 14,041,447 9, 758,805,985
USDT 3, 068,693,355 1,015 3,023,343 4 , 886,514,268 170 28 , 744,202 7,955,207 ,623
BUSD 2,012,057 , 564 806 2,496,349 3,650,959, 785 193 18,916 ,890 5,663 ,017,349
USDC 2,460, 329,194 113 21,772,825 2,460, 284,995 110 22,366,227 4,920 ,614,190
USDT 1,069,466 ,002 949 1,126,940 3,694,837 , 430 1,452 2,544,654 4,764,303 ,432
USDC 4,753,143 ,010 347 13,697 ,818 ic} ic} ic} 4,753,143 ,010
USDC 1,893,508 ,015 673 2, 813 , 533 2,684,621,215 150 17,897,475 4,578 ,129,229
FIT 4 ,554,280,415 9 506,031,157 ic} ic} ic} 4 ,554,280,415
WBTC 1,457,376 ,216 218 6,685,212 2,958,107 ,671 513 5,766,292 4,415 ,483 , 887
FIT ic} ic} ic} 4,308 ,989,371 2 2,154,494, 685 4,308 ,989,371
USDC 4, 254,331,253 63 67 , 529,068 ic} ic} ic} 4, 254,331,253
USDC 2,091,907 , 850 89 23,504,583 2,100,717 ,678 94 22,348 ,060 4,192 ,625,528
USDC 4,187 ,877,876 132 31,726,348 ic} ic} ic} 4,187 ,877,876
FIT 4 ,174,679,205 8 521,834,901 ic} ic} ic} 4,174,679,205
TUSD 689,890,645 178 3,875,790 3, 069,951,471 1,347 2,279,103 3,759,842 ,117
HUSD 483 , 794,983 120 4,031,625 2,944,786 ,359 759 3,879,824 3,428 581,343
USDT ic} ic} ic} 3 , 337,578,009 626 5,331,594 3 , 337,578,009

m Miner; Tornado Cash Recipient WBTC 3, 299,132,787 85 38,813,327 [c) [c) [o) 3, 299,132,787"""


PARANOID_STYLE = """It was Welch who promised to cut communists and "comsymps" (sympathizers) from
the fabric of American society. It was Welch who called then-President Dwight D.
Eisenhower "a dedicated, conscious agent of the communist conspiracy." It was
Welch who inspired those "Impeach Earl Warren" and "Get the U.S. Out of the
United Nations" billboards that dominated the highways of America in the 1960s as
the Burma Shave signs had in the 1930s and 40s.

Although Belmont was the society's headquarters, Southern California was its sort of
unofficial capital. With a regional command post in San Marino, Birchism spread
through the region, its intense, almost exclusively white, upper-middle class
Americans carrying the society's conservative banner.
"""


@pytest.fixture(scope='session')
def ocr_image(do_kwon_tweet):
    """Requires the private varibale _extracted_text to be set manually."""
    image_file = ImageFile(do_kwon_tweet)
    image_file.text_extraction_attempted = True
    return image_file


def test_tweet_filenames(ocr_image):
    ocr_image._extracted_text = WUBLOCKCHAIN_TWEET_TEXT
    assert FilenameExtractor(ocr_image).filename() == 'Tweet by @WuBlockchain - "a16z voted 15 million UNI against the final proposal to deploy Uniswap V3 on BNB Chain proposed by OxPlasma Labs. The proposal uses Wormhole as a cross_chain bridge. a16z o" do_kwon_debate_the_poor.jpeg'
    ocr_image._extracted_text = REPLY_TWEET_TEXT
    assert FilenameExtractor(ocr_image).filename() == 'Tweet by @gedaominas replying to @tier10k - "The same thing happened with their SEPA transfers a couple of years ago. Just because Binance isn\'t licensed for money institution activities_ they have" do_kwon_debate_the_poor.jpeg'
    ocr_image._extracted_text = TIMESTAMPED_TWEET_TEXT
    assert FilenameExtractor(ocr_image).filename() == 'Tweet by @tier10k - "_DB_ SEC Probe Into Kraken at an Advanced Stage and Could Lead to a Settlement in Coming Days: Bloomberg 3:55 PM _ Feb 8_ 2023 _ 77.3K Views" do_kwon_debate_the_poor.jpeg'
    ocr_image._extracted_text = GABOR_TWEET_TEXT
    assert FilenameExtractor(ocr_image).filename() == 'Tweet by @gaborgurbacs - "I think this Coinbase media campaign will have the opposite effect. USDC users will learn about USDT and convert to USDT as they question the motivations and rationale of" do_kwon_debate_the_poor.jpeg'
    ocr_image._extracted_text = BAD_OCR_TWEET
    assert FilenameExtractor(ocr_image).filename() == 'Tweet by @ASYB111 replying to @cz_binance - "Any updates on send cash feature? It is temporarily disabled. 1o) td iv) ily 399 a_" do_kwon_debate_the_poor.jpeg'
    ocr_image._extracted_text = TWITTER_CZ
    assert FilenameExtractor(ocr_image).filename() == 'Tweet by @cz_binance - "7) Binance always encourages collaboration between industry players. i: Regarding any speculation as to whether this is a move against a competitor_ it is not. Our industry i" do_kwon_debate_the_poor.jpeg'


def test_reddit_filenames(ocr_image):
    ocr_image._extracted_text = REDDIT_POST
    assert FilenameExtractor(ocr_image).filename() == 'Reddit post by TheLostWander_er in binance - "send cash feature is temporarily disable. I was trying to withdraw cash since last week and I am seeing this message every time I try the send cash fe" do_kwon_debate_the_poor.jpeg'
    ocr_image._extracted_text = REDDIT_REPLIES
    assert FilenameExtractor(ocr_image).filename() == 'Reddit post by Fluffyhobbit - "Option 4. 80_ of us send crypto to cold storage and binance doesn\'t skip a beat Edit: forgot to put in doesn\'t_ _ 22 tb )" do_kwon_debate_the_poor.jpeg'
    ocr_image._extracted_text = REDDIT_R_CRYPTOCURRENCY_REPLY
    assert FilenameExtractor(ocr_image).filename() == 'Reddit post by Roberto9410 - "Wow the downfall of BUSD is something to see _p. 1_4" do_kwon_debate_the_poor.jpeg'
    ocr_image._extracted_text = REDDIT_DEBIT_COMMENT
    assert FilenameExtractor(ocr_image).filename() == 'Reddit post by Spmhealy_ADA - "show my Debit card number) Can\'t use Debit to deposit fiat. Don\'t even see that as an option. I see link bank (which I picked for instant use) ACH (3_5 day to clear)" do_kwon_debate_the_poor.jpeg'
    ocr_image._extracted_text = REDDIT_POST_2
    assert FilenameExtractor(ocr_image).filename() == 'Reddit post by cho0n22 - "0 Thave the blue card and it\'s not working v My blue card isn\'t being accepted for online payments_ have not tried in person yet. Is it because I have nothing staked? Say" do_kwon_debate_the_poor.jpeg'


def test_reveddit_filenames(ocr_image):
    ocr_image._extracted_text = REVEDDIT_THREAD
    assert FilenameExtractor(ocr_image).filename() == 'Reveddit r_binance do_kwon_debate_the_poor.jpeg'


def test_dune_analytics_filename(ocr_image):
    ocr_image._extracted_text = DUNE_ANALYTICS
    assert FilenameExtractor(ocr_image).filename() == 'Dune Analytics "Alameda (Tagged and Rumored) Ethereum Wallets All Time In and Out a)" do_kwon_debate_the_poor.jpeg'


def test_everything_else_filename(ocr_image):
    ocr_image._extracted_text = PARANOID_STYLE
    assert FilenameExtractor(ocr_image).filename() == 'do_kwon_debate_the_poor - "It was Welch who promised to cut communists and "comsymps" (sympathizers) from the fabric of American society. It was Welch who called then_President Dwight D. Eisenhower".jpeg'
