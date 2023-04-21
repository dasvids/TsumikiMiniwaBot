import re
from database.mongo import rates_db

def my_regex_search(row):
    return re.search(r'(`♡\d{1,5}\xa0{0,4}`)\s·\s\*\*(`\xa0{0,4}[0-9a-z]{1,7}`)\*\*\s·\s(`[★☆]{4}`)\s·\s'
                     r'(`#\d{1,5}\xa0{0,5}`)\s·\s(`◈\d`)\s·\s'
                     r'~?~?((\s?[\w#()/&\'*!.,%~;?:-]+)+)\s·\s\*\*((\s?[\w#()/&!\'.,*;?~%:-]+)+)\*\*~?~?',
                     row)
    
def get_info(rs):
    price = get_price(rs)
    return {
        rs.group(2): {
            "wl": rs.group(1),
            "print": rs.group(4),
            "ed": rs.group(5),
            "series": rs.group(6),
            "character": rs.group(8),
            "price": price,
            "is_accepted": True if float(price[1:len(price) - 1]) >= 3 else False
        }
    }
    
def remove_apos(row):
    return row[2:len(row) - 1]


def get_price(rs):
    card_print = int(remove_apos(rs.group(4)))
    wl = int(remove_apos(rs.group(1)))
    ed = int(remove_apos(rs.group(5)))

    prate = ""
    # very hot if else things for define print
    if card_print > 1000:
        prate = 'hp'
    elif card_print in range(500, 1000):
        prate = 'hmp'
    elif card_print in range(100, 500):
        prate = 'lmp'
    elif card_print in range(50, 100):
        prate = 'hlp'
    elif card_print in range(10, 50):
        prate = 'llp'
    elif card_print in range(1, 10):
        prate = 'sp'

    try:
        # trying to get price of card
        card_price = wl / rates_db.find_one({'edition': f'{ed}'})[prate]
    except KeyError:
        # in case if rate wasnt found count price as 0
        card_price = 0
    except ZeroDivisionError:
        # imagine write 0 to rate
        card_price = 0

    # round for good view
    return f"""`{round(card_price, 2)}`"""

def myfunc(mlist):
    MatchesList = [my_regex_search(x) for x in mlist]
    ed = {}
    for edition in rates_db.find({},{'_id': 0}):
        subed = {}
        for t in edition.keys():
            subed.update({t : edition[t]})
            
        ed.update({
            int(edition['edition']): subed})

    cardsinfo = []

    for match in MatchesList:
        card_print = int(remove_apos(match.group(4)))
        wl = int(remove_apos(match.group(1)))
        edition = int(remove_apos(match.group(5)))
        print_type = get_print_type(card_print)
        price = wl / \
            ed[edition][print_type] if ed[edition][print_type] != 0 else 0
        # prices.append(price)
        cardsinfo.append({
            match.group(2): {
                "wl": match.group(1),
                "print": match.group(4),
                "ed": match.group(5),
                "series": match.group(6),
                "character": match.group(8),
                "price": f"""`{round(price, 2)}`""",
                "is_accepted": True if price >= 3 else False
            }
        })

    return cardsinfo

def get_print_type(card_print):
    if card_print > 1000:
        prate = 'hp'
    elif card_print in range(500, 1000):
        prate = 'hmp'
    elif card_print in range(100, 500):
        prate = 'lmp'
    elif card_print in range(50, 100):
        prate = 'hlp'
    elif card_print in range(10, 50):
        prate = 'llp'
    elif card_print in range(1, 10):
        prate = 'sp'
    return prate