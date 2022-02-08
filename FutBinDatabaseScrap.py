import re
import pandas as pd
import bs4
import cloudscraper

fifa = {'22': 'FIFA22'}     # Store Key

# CSV Headers
cardColumns = ['ID', 'Name', 'Rating', 'Position', 'Revision', 'Nation',
               'Club', 'League', 'Price | PS', 'WeakFoot', 'Skill Moves',
               'Pace', 'Shooting', 'Passing', 'Dribbling', 'Defending',
               'Phyiscality', 'Body Type', 'Weight', 'Height', 'WorkRate',
               'Popularity', 'BaseStats', 'InGameStats']

C = open('FutBin_Players_Stats_FIFA_22_FUT.csv', 'w')
C.write(','.join(cardColumns) + '\n')
C.close()

scraper = cloudscraper.create_scraper(
    browser={'browser': 'firefox', 'platform': 'windows', 'mobile': False})

for key, value in fifa.items():
    id = 0
    ID = 0
    print('Doing ' + value)
    FutBin = scraper.get('https://www.futbin.com/' + key + '/players')
    bs = bs4.BeautifulSoup(FutBin.text, 'html.parser')
    try:
        TotalPages = str(bs.findAll(
            'li', {'class': 'page-item '})[-1].text).strip()
    except IndexError:
        TotalPages = str(bs.findAll(
            'li', {'class': 'page-item'})[-2].text).strip()
    print('Number of pages to be parsed for FIFA '
          + key + ' is ' + TotalPages + ' Pages')
    for page in range(1, int(TotalPages) + 1):
        FutBin = scraper.get('https://www.futbin.com/'
                             + key + '/players?page=' + str(page))
        bs = bs4.BeautifulSoup(FutBin.text, 'html.parser')
        table = bs.find('table', {'id': 'repTb'})
        tbody = table.find('tbody')
        extracted = tbody.findAll('tr', {'class': re.compile('player_tr_\\d')})
        Card = []
        for cardDetails in extracted:
            clubs = cardDetails.find(
                'span', 'players_club_nation').findAll('a')
            # Getting Clubs Information
            club = clubs[0]['data-original-title'].replace(
                'Icons', 'unknown').strip()
            # Getting Nation Information
            nation = clubs[1]['data-original-title'].replace(
                'Icons', 'unknown').strip()
            # Getting League Information
            league = clubs[2]['data-original-title'].strip()
            name = str(cardDetails.text).strip().replace(
                '\n', ' ').split('           ')[0]
            cardDetails = str(cardDetails.text).strip().replace('\n', ' ').replace(
                ' \\ ', '\\').replace(' | ', '|').split('       ')[1]
            # Getting Work Rate W/R
            workRate = re.search('\\w\\\\\\w', cardDetails,
                                 re.IGNORECASE).group(0)
            # Removing workRate From cardDetails
            cardDetails = re.sub('\\w\\\\\\w', '', cardDetails)
            # Getting Height CM|Feet'Inch"
            matchHeight = re.search(
                '\\w+\\|\\d\'\\d+\"', cardDetails, re.IGNORECASE).group(0)
            # Removing matchHeight From cardDetails
            cardDetails = re.sub('\\w+\\|\\d\'\\d+\"', '', cardDetails)
            # Getting Player Preffered Position
            position = re.findall('\\s(\\D*\\s\\D+)',
                                  cardDetails, re.IGNORECASE)[1].split()[0]
            # Removing position From cardDetails
            cardDetails = re.sub(str(position), '', cardDetails)
            # Getting Player Card Revision
            revision = re.findall(
                '\\s(\\D*\\s\\D+)', cardDetails, re.IGNORECASE)[1].split()
            # Some revision Have Differnt Dimention, Joining Those
            revision = (' '.join(revision))     # Now a String
            # Removing revision From cardDetails
            cardDetails = re.sub(revision, '', cardDetails)
            # Getting Body Type
            bodyType = re.search(r'\s{6}(\w.+?)\s{2}', cardDetails).group(1)
            # Removing bodyType From cardDetails
            cardDetails = re.sub(bodyType, '', cardDetails)
            cardDetails = cardDetails.split()
            # Insert Tables At Proper ID
            cardDetails.insert(0, id)
            cardDetails.insert(1, name)
            cardDetails.insert(3, position)
            cardDetails.insert(4, revision)
            cardDetails.insert(5, nation)
            cardDetails.insert(6, club)
            cardDetails.insert(7, league)
            cardDetails.insert(17, bodyType)
            cardDetails.insert(19, matchHeight)
            cardDetails.insert(20, workRate)
            Card.append(cardDetails)
            print(cardDetails)
            id += 1

        df = pd.DataFrame(Card)
        df.to_csv('FutBin_Players_Stats_FIFA_22_FUT.csv', mode='a',
                  header=False, sep=',', encoding='latin1', index=False)
