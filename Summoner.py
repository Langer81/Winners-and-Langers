from tkinter import *
'''
write a program that will output the

Using op.gg: 
1. a summoner's top 7 most played champion
2. a summoner's main role
3. a summoner's solo rank
4. 
'''
champ_file = open('champion_list.txt','r')

import requests, bs4
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
class Summoner(object):
    champions = champ_file.read().split() #list of all league champions
    ranks = ['Bronze','Silver','Gold','Platinum','Diamond','Master','Challenger']
    def __init__(self, username):
    
        self.username = username
        self.link = 'http://na.op.gg/summoner/userName=' + username + '#'
        self.response = requests.get(self.link)
        self.response.raise_for_status()
        self.soup = bs4.BeautifulSoup(self.response.text,'lxml')
        self.spectator_tab_link = 'http://na.op.gg/summoner/spectator/userName='+self.username
        self.spectator_response = requests.get(self.spectator_tab_link)
        self.spectator_soup = bs4.BeautifulSoup(self.spectator_response.text,'lxml')
        self.get_rank() # init. self.rank
        self.get_most_played()# init. self.most_played
        self.raw_rank()# init. self.raw_score
        self.in_game()# init. self.is_live
        self.past_games = self.get_past_teammates_and_opponents()
        self.game_urls = self.return_urls()
        if self.is_live == True:
            self.get_current_teammates_and_opponents()# init. self.player_team, self.opposing_team as <class> Team objects
            self.current_champ = self.get_live_champ()
    def __str__(self):
        username = self.username
        rank = self.rank
        most_played = self.most_played
        string = 'Player: ' + username + '\n' + 'Rank: ' + rank + '\n' + 'Most Played Champions: ' + str(most_played) + '\n'
        
        if self.is_live:
            teammates = self.player_team
            opponents = self.opposing_team
            string += 'This player is in game!' + '\n'
            string += 'Teammates: ' + str(teammates) + '\n'
            string += 'Opponents: ' + str(opponents) + '\n'

        else:
            string += 'This player is not in game.'
        return string
    def get_rank(self):
        '''
        return the rank of the summoner
        '''
        rank = self.soup.select('div .tierRank')

        self.rank = rank[0].getText() + ' '
        if self.rank == 'Master ':
            master_points = self.soup.select('div .SideContent div .TierInfo span.LeaguePoints')
            temp = master_points[0].getText()
            for i in range(len(temp)):
                if temp[i].isdigit() == True:
                    self.rank += temp[i]
                if temp[i] == 'L':
                    self.rank += ' ' +temp[i] + 'P'
        if self.rank == 'Challenger ':
            master_points = self.soup.select('div .SideContent div .TierInfo span.LeaguePoints')
            temp = master_points[0].getText()
            for i in range(len(temp)):
                if temp[i].isdigit() == True:
                    self.rank += temp[i]
                if temp[i] == 'L':
                    self.rank += ' ' +temp[i] + 'P'
        return self.rank

    def get_most_played(self):
        '''
        return the seven most played champions of the summoner
        '''
        incomplete_alphabet = 'abcdefghijklmopqrsuvwxyz'
        most_played_unformatted = self.soup.select('div .Content.tabItems a')
        unformatted_temp_2 = []
        unformatted_temp = []
        self.most_played = []

        for i in range(len(most_played_unformatted)):
            unformatted_temp.append(most_played_unformatted[i].getText())
        for i in range(len(unformatted_temp)):
            for letter in incomplete_alphabet:
                if letter in unformatted_temp[i]:
                    unformatted_temp_2.append(unformatted_temp[i])
                    break
        unformatted_temp_2.pop() #gets rid of more seasons
        string = str(unformatted_temp_2)
        i = 0
        j = 0
        while i < len(string):
            while j < len(string):
                if string[i:j] in Summoner.champions:
                    self.most_played.append(string[i:j])
                j+=1
            i+=1
            j=i
        
        return self.most_played

    def get_main_role(self):
        '''
        return the most played role of the summoner
        '''
        temp = []
        role_list = self.soup.select('div .GameAverageStatsBox td ul li div div.Name')
        for i in range(len(role_list)):
            temp.append(role_list[i].getText())
        return temp

    

    '''
    def get_win_rates(self):
        tagged_win_rates = self.soup.select('div .tabItems tr td span')
        win_rates = []
        for i in range(len(tagged_win_rates)):
            win_rates.append(tagged_win_rates[i].getText())
        return win_rates
    '''
    def raw_rank(self):
        '''
        gets a number value for the summoner's rank ex. Bronze 1 = 5
        '''
        separate = self.rank.split()
        raw_score = 0
        rank = separate[0]
        rank_term = 0
        division = int(separate[1])
        for i in range(len(Summoner.ranks)):
            if rank == Summoner.ranks[i]:
                rank_term = Summoner.ranks.index(Summoner.ranks[i])
        raw_score += rank_term*5
        if division == 1:
            raw_score += 5
        elif division == 2:
            raw_score += 4
        elif division == 3:
            raw_score += 3
        elif division == 4:
            raw_score += 2
        elif division == 5:
            raw_score += 1
        self.raw_score = raw_score
        return self.raw_score

    def rank_difference(self, other):
        '''
        each rank represents 1 rank point. The difference is calculated for each player
        '''
        return self.raw_score-other.raw_score
        
    def in_game(self):
        '''
        returns true if summoner is in a live game and false if not
        '''
        self.spectator_tab_link = 'http://na.op.gg/summoner/spectator/userName='+self.username
        response = requests.get(self.spectator_tab_link)
        soup = bs4.BeautifulSoup(response.text,'lxml')
        self.is_live = False
        
        live = soup.select('div .tabItem.Content.SummonerLayoutContent.summonerLayout-spectator')
        live_formatted = []
        for i in range(len(live)):
            live_formatted.append(live[i].getText())
        self.is_live = 'is not in an active game' not in live_formatted[0]
        return self.is_live

    def get_solo_mmr(self):
        pass

    def get_past_teammates_and_opponents(self): # For data collection
        #if the summoner is in a game, then return a list of their teammates and a list of their enemies. 
        total_players = self.soup.select('div .GameItemList div .SummonerName a')
        #print(total_players)
        for i in range(len(total_players)):
            total_players[i] = total_players[i].getText()
        
        teams = []
        i = 0
        j = 5
        while i < len(total_players):
            teams.append(total_players[i:j])
            i+=5
            j+=5
        games = []
        for i in range(0, len(teams), 2):
            games.append([teams[i], teams[i+1]])
            

        #games is a list of lists of lists. The innermost list are 5 player teams, the middle list are lists containing 2, 5 player teams and the last list just contains all the previous lists.

        print('Collected ' + str(len(total_players)/10) +' games from this user')
        return games
        #Example of games: [[['a','b', 'c','d', 'e'],['f','g','h','i','j']]] team > game > overall list

    def get_current_teammates_and_opponents(self):
        response = requests.get(self.spectator_tab_link)
        soup = bs4.BeautifulSoup(response.text,'lxml')
        players_unformatted = soup.select('div .SpectateSummoner td a')
        players_with_space = []
        players = []
        for i in range(len(players_unformatted)):
            players_with_space.append(players_unformatted[i].getText())
        for i in range(len(players_with_space)): #gets rid of spaces from opgg
            if players_with_space[i].isspace() == False:
                players.append(players_with_space[i])
        blue_team = []
        red_team = []
        for i in range(len(players)):
            if i<5:
                blue_team.append(players[i])
            else:
                red_team.append(players[i])
        #now we have 2 lists of players one being the red team, one the blue team
        if self.username in red_team:
            self.player_team = red_team
            self.opposing_team = blue_team
        elif self.username in blue_team:
            self.player_team = blue_team
            self.opposing_team = red_team

        return (self.player_team, self.opposing_team)

    def get_live_champ(self):
        players_and_champs_html = self.spectator_soup.select('div .Content a')[2:]
        player_index = 0
        for element in players_and_champs_html:
            if self.username in element:
                player_index = players_and_champs_html.index(element)

        champ_html = str(players_and_champs_html[player_index-1])
        #print(str(champ_html))
        for champion in Summoner.champions:
            if champion in champ_html:
                return champion

        #print(current_champ)

    def return_urls(self):
        ''' 
        instead of using na.op.gg, this method will isolate all ranked games and use riot's official match history system.
        return should be list of urls of ranked games
        [<url1>, <url2>, etc]
        '''
        browser = webdriver.Firefox()
        browser.get('https://matchhistory.na.leagueoflegends.com/en/#page/landing-page')
        search_box = browser.find_element_by_id('player-search-6-name')
        search_box.send_keys(self.username)
        search_box.send_keys(Keys.ENTER)
        print(browser.current_url)
        browser.forward()
        drop_down_menu = browser.find_element_by_name('mode')
        drop_down_menu.click()
        drop_down_menu.send_keys('r')
        drop_down_menu.click()
        go_button = browser.find_element_by_tag_name('button')
        go_button.click()
        games = browser.find_elements_by_class_name('game-summary')
        #games is a list of webdriver elements
        game_urls = [game.current_url for game in games]
        return game_urls

class Game(object):
    def __init__(self, names):
        '''
        Game is a League of Legends game of 10 players.
        names is a list of lists of names
        names = [[langer, kaypop, used bread, raiinichts, longue baguette], [apoxyomenos, swisspikeman, imaqtpie, shiptur, Lil Loaf]]
        '''

        self.team1_names = names[0]
        self.team2_names = names[1]
        self.team1_summoners = [Summoner(player) for player in self.team1_names]
        self.team2_summoners = [Summoner(player) for player in self.team2_names]
        self.team1_raw_ranks = self.get_all_ranks()[0]
        self.team2_raw_ranks = self.get_all_ranks()[1]
        self.team1_champs = self.get_all_champions()[0]
        self.team2_champs = self.get_all_champions()[1]
        self.rank_diff = sum(self.team1_raw_ranks) - sum(self.team2_raw_ranks) #important predictor
        '''
        for summoner in self.team1_summoners:
            if summoner.current
        '''
    def get_all_ranks(self):
        '''
        returns a tuple of the ranks of boths teams
        '''
        team1_ranks = [player.raw_rank() for player in self.team1_summoners]
        team2_ranks = [player.raw_rank() for player in self.team2_summoners]
        return team1_ranks, team2_ranks
    def get_all_champions(self):
        '''
        returns a tuple of the most played champions of boths teams
        list of lists of each players most played champs
        '''
        team1_champs = [player.most_played for player in self.team1_summoners]
        team2_champs = [player.most_played for player in self.team2_summoners]
        return team1_champs, team2_champs



'''
class Team(object):
    def __init__(self,team):
    
        #takes a list of five players and creates a Team object from them.
        
        self.team = [] # list of 5 summoners
        for name in team:
            self.team.append(Summoner(name))

        self.get_total_rank()
    def get_total_rank(self):
        self.team_total = 0
        for summoner in self.team:
            self.team_total+=summoner.raw_score
        return self.team_total
    def get_total_rank_difference(self, other):
        return self.team_total - other.team_total
class Application(Frame):
    def __init__(self, master):
        super(Application, self).__init__(master)
        self.grid()
        self.create_widgets()
    def create_widgets(self):
        self.text = Text(self,width)


class DataCollection(object):
    def __init__(self, summoner, ):
'''
def test_function():
    username = input('Enter a League of Legends Player')
    summoner = Summoner(username)
    summoner_past_games = summoner.get_past_teammates_and_opponents()
    test_game = Game(summoner_past_games[0])
    print('Team 1: ' + str(test_game.team1_names))
    print('Team 1 ranks: ' + str(test_game.team1_raw_ranks))
    print('Team 1 champs: ' + str(test_game.team1_champs))
    print()
    print('---------------------------------')
    print()
    print('Team 2: ' + str(test_game.team2_names))
    print('Team 2 ranks:' + str(test_game.team2_raw_ranks))
    print('Team 2 champs: ' + str(test_game.team2_champs))
def main():
    username = input('Enter a League of Legends Player')
    summoner = Summoner(username)
    print(summoner.game_urls)
    #while True:
    
    '''
    cont = input('Press any key to display the next game')
    while cont:
        current = next(summoner_past_games)
        current_game = Game(current)
        print(current_game.rank_diff)
        cont = input('Press any key to display the next game')

    while True:
        try:
            current = next(summoner_past_games)
            current_game = Game(current)

        except StopIteration:
    '''
    


if __name__ == '__main__':
    main()
