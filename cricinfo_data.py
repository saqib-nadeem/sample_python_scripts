import os
import pytz
import decimal
import logging
import calendar
import requests
from __future__ import division

from lxml import html

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand

from impact_app.models import *


os.environ['TZ'] = 'UTC'

logger = logging.getLogger('impact_app_management')

SR_BOOST_CONSTANT = 3
ER_BOOST_CONSTANT = 3


class Command(BaseCommand):

    def getRequest(self, url, params):
        resp = requests.get(url, params=params)
        return resp

    def writeToFile(self, file_name, content):
        f = open(file_name, 'w+')
        f.write(content)
        f.close()

    def getPageContent(self, url, file_name):
        ''' Read From file '''
        if (os.path.isfile(file_name)):
            tree = html.fromstring(open(file_name).read())
        else:
            ''' Read From URL '''
            page = self.getRequest(url, None)
            tree = html.fromstring(page.content)
            self.writeToFile(file_name, page.content)
        return tree

    def populateOverNumber(self, ball, over_info):
        over_text = ball.cssselect('.commentary-overs')[0].text
        over_info['over_str'] = over_text
        # over_info['over'] = int(over_text.split('.')[0]) + 1
        # over_info['ball'] = int(over_text.split('.')[1])

    def findPlayerFromList(self, player_name, player_list):
        for player in player_list:
            if player_name in player[0]:
                return player

    def populateStriker(self, players_text, over_info, players):
        over_info['batsman'] = self.findPlayerFromList(str(players_text.strip().split(' ')[2]), players)
        over_info['non_striker'] = ''  # TODO: find nonstriker if needed

    def populateRuns(self, runs_text, over_info):
        over_info['runs'] = {}
        runs = 0
        if any(word in runs_text for word in ['run', 'runs', 'leg', 'byes', 'wide']):
            runs = runs_text[0]
            if 'n' in runs:
                runs = 0
            runs = int(runs)
        over_info['runs']['total'] = runs
        over_info['runs']['batsman'] = runs

    def populateBatsman(self, over_info):
        over_info['batsman'] = {
            'runs': over_info['runs'],
            'dotball': 0 if over_info['runs'] > 1 else 1,
            'six': 1 if 'six' in over_info else 0,
            'four': 1 if 'four' in over_info else 0,
            'ball_count': 1,
            'key': over_info['striker']  # TODO: replace with full name
        }

        if over_info['batsman']['six'] == 1:
            del over_info['six']

        if over_info['batsman']['four'] == 1:
            del over_info['four']

    def populateBowler(self, players_text, over_info, players):
        over_info['bowler'] = self.findPlayerFromList(str(players_text.strip().split(' ')[0]), players)

    def populateTeam(self, players_text, over_info):
        over_info['team'] = {
            'runs': over_info['runs'],
            'wicket': 1 if 'wicket' in over_info else 0,
            'ball_count': 1,
            'extras': over_info['extras']
        }

        if over_info['team']['wicket'] == 1:
            del over_info['wicket']

    def populateExtras(self, runs_text, over_info):
        # TODO: Find all types of no ball string
        if any(word in runs_text for word in ['leg', 'byes', 'wide']):
            runs = int(runs_text[0])
            if 'leg' in runs_text:
                over_info['extras'] = {'legbyes': runs}
            if 'byes' in runs_text:
                over_info['extras'] = {'byes': runs}
            if 'wide' in runs_text:
                over_info['extras'] = {'wide': runs}
            over_info['runs']['extras'] = runs
            over_info['runs']['batsman'] = 0
        else:
            over_info['runs']['extras'] = 0

    def populateBoundryInfo(self, boundry_text, over_info):
        if 'SIX' in boundry_text:
            over_info['runs']['total'] = 6
            over_info['runs']['batsman'] = 6
            # over_info['six'] = True
        elif 'FOUR' in boundry_text:
            over_info['runs']['total'] = 4
            over_info['runs']['batsman'] = 4
            # over_info['four'] = True

    def populateWicketInfo(self, wicket_text, over_info):
        if 'OUT' in wicket_text:
            over_info['wicket'] = True  # TODO: find player_out and out kind

    def populateComment(self, players_text, runs_text, boundry_or_wicket_text,
                         over_info):
        over_info["comment"] = '{}'.format(players_text)
        if runs_text:
            over_info["comment"] = '{}, {}'.format(players_text, runs_text)
        if boundry_or_wicket_text:
            over_info["comment"] += ', {}'.format(boundry_or_wicket_text).strip()

    def populateTotalRuns(self, total_runs, over_info):
        over_info['total_runs'] = total_runs + over_info['runs']

    def populateCity(self, match_information, info):
        info['city'] = match_information[1].split(' ')[-1]

    def populateCompetition(self, match_information, info):
        info['competition'] = match_information[0].strip()

    def populateDate(self, match_information, info):
        # TODO: Convert date to year-month-day format
        abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
        date = match_information[2:]
        month = abbr_to_num[date[0].strip().split(" ")[0]]
        day = date[0].strip().split(" ")[1]
        year = date[1].strip()
        date = '{}-{}-{}'.format(year, month, day)
        info['dates'] = [datetime.datetime.strptime('{}-{}-{}'.format(year, month, day), "%Y-%m-%d").date()]

    def populateMatchType(self, match_information , info):
        match_number = match_information[1].strip().split(' ')[0][:-2]
        info['match_number'] = 'Match {}'.format(match_number)
        info['T20_number'] = match_number
        info['match_type'] = 'T20'

    def populateOvers(self, info):
        info['overs'] = 20

    def extractNumber(self, string):
        return int(''.join(ele for ele in str(string) if ele.isdigit()))

    def extractWinnerName(self, string):
        return string.split('won')[0].strip()

    def extractWinBy(self, string):
        if 'runs' in string:
            return 'runs'
        elif 'wickets' in string:
            return 'wickets'

    def populateOutcome(self, innings_requirement, info):
        outcome = innings_requirement[0].text
        number = self.extractNumber(outcome)
        winner_name = self.extractWinnerName(outcome)
        win_by = self.extractWinBy(outcome)

        info['outcome'] = {'by': {win_by: number}, 'winner': winner_name}

    def populateTeams(self, team_names, info):
        info['teams'] = [team_names[0].text, team_names[1].text]

    def populateToss(self, match_details, info):
        # TODO:Find decision(field/bat)
        info['toss'] = match_details[0].cssselect('.normal')[0].text

    def populatePlayerOfMatch(self, match_details, info):
        # TODO: need to clean
        info['player_of_match'] = [match_details[1].cssselect('.normal')[1].text.split('(')[0].strip()]

    def populateUmpires(self, match_details, info):
        umpires = match_details[2].cssselect('.playerName')
        info['umpires'] = [umpires[0].text, umpires[1].text]

    def populateVenue(self, venue_information, info):
        venue = venue_information.cssselect('.space-top-bottom-5')[1].cssselect('.headLink')[0].text
        info['venue'] = venue.split(",")[0]

    def getPlayerFullName(self, text):
        return " ".join(text.split(' ')[-2:])

    def populatePlayers(self, first_innings_player, more_match_stats, info):
        players = {}
        list_player = [(self.getPlayerFullName(player.get('title')), player.text) for element in first_innings_player for player
               in element.cssselect('.playerName')] + [
                  (self.getPlayerFullName(player.get('title')), player.text) for element in more_match_stats for player in
                  element.cssselect('.playerName')]

        for element in first_innings_player:
            for index, player in enumerate(element.cssselect('.playerName')):
                player_name = (self.getPlayerFullName(player.get('title')), player.text)
                dismissal_info = element.cssselect('.dismissal-info')[index].text.strip()
                fielders = dismissal_info.split('(')[1].replace(')', '') if '(' in dismissal_info else dismissal_info
                players[player_name[1]] = {
                    'name': player_name[1],
                    'fielders': fielders.split('/') if '/' in fielders else [fielders]
                }

        info['players'] = list_player
        info['players_wicket_info'] = players

    def getMatchInfo(self, url):
        # TODO: Romove content reading from file
        tree = self.getPageContent(url, 'match_info.txt')
        info = {}
        match_information = tree.xpath('//div[@class="match-information-strip"]')
        match_information = match_information[0].text.split(',')
        self.populateCity(match_information, info)
        self.populateCompetition(match_information, info)
        self.populateDate(match_information, info)
        self.populateMatchType(match_information, info)
        self.populateOvers(info)

        innings_requirement = tree.xpath('//div[@class="innings-requirement"]')
        self.populateOutcome(innings_requirement, info)

        team_names = tree.xpath('//div[@class="team-1-name"]')[0].cssselect('.teamLink')
        self.populateTeams(team_names, info)

        match_details = tree.xpath('//div[@class="match-information"]')[0].cssselect('.space-top-bottom-10')
        self.populateToss(match_details, info)
        self.populateUmpires(match_details, info)

        venue_information = tree.xpath('//div[@class="row brief-summary"]')[0].cssselect('.match-information')[0]
        self.populateVenue(venue_information, info)

        first_innings_player = tree.xpath('//table[@class="batting-table innings"]')
        more_match_stats = tree.xpath('//div[@class="more-match-stats"]')
        self.populatePlayers(first_innings_player, more_match_stats, info)
        self.populateWicketKeeper(first_innings_player, info)
        self.populatePlayerOfMatch(match_details, info)

        return info

    def checkUnicde(self, str):
        if isinstance(str, unicode):
           return True
        return False

    def populateWicketKeeper(self, innings_player, info):

        first_inning_player = innings_player[0]
        second_inning_player = innings_player[1]

        for element in first_inning_player:
            for e in element.cssselect('.batsman-name'):
                if self.checkUnicde(e.text_content()):
                    info['Team_1_Historical_WK'] = \
                        self.findPlayerFromList(str(e.text_content().encode('ascii', 'ignore')).split(" ")[-1], info['players'])

        for element in second_inning_player:
            for e in element.cssselect('.batsman-name'):
                if self.checkUnicde(e.text_content()):
                    info['Team_2_Historical_WK'] = \
                        self.findPlayerFromList(str(e.text_content().encode('ascii', 'ignore')).split(" ")[-1],
                                                info['players'])

    def populateWicket(self, wicket_text, inning, players, players_wicket_info):

        out_kinds = {
            'c': 'caught',
            'run': 'run out',
            'lbw': 'leg before wicket',
            'b': 'bowled',
            'st': 'stump'
        }
        out_kind = out_kinds.get(wicket_text[2])
        inning['wicket'] = {
            'kind': out_kind,
            'player_out': self.findPlayerFromList(str(wicket_text[1]), players)
        }
        if out_kind == 'caught':
            inning['wicket']['fielders'] = [self.findPlayerFromList(wicket_text[3].encode('ascii', 'ignore').decode('ascii'), players)]

        elif out_kind == 'run out':
            fielders = players_wicket_info[' '.join(wicket_text[:2])]['fielders']
            inning['wicket']['fielders'] = [self.findPlayerFromList(str(fielder.encode('ascii', 'ignore').decode('ascii')), players) for fielder in fielders]

    def getInningsInfo(self, url, innings_number, match_info):
        full_url = '{}?innings={};view=commentary'.format(url, innings_number)
        # TODO: Romove reading content from file
        tree = self.getPageContent(full_url, 'innings_info_{}.txt'.format(innings_number))
        team = tree.xpath('//*[@id="sub_{}"]'.format(innings_number))[0].text.split(" ")[0]
        balls = tree.xpath('//div[@class="commentary-event"]')
        players = match_info['players']

        inning = {}
        for ball in balls:
            over_info = {}

            if ball.cssselect('.commentary-text p b') and not ball.cssselect('.commentary-overs'):
                wicket_text = ball.cssselect('.commentary-text p b')[0].text.replace("  ", " ").split(" ")
                self.populateWicket(wicket_text, inning[over_str], players, match_info['players_wicket_info'])
                continue

            self.populateOverNumber(ball, over_info)
            comment = ball.cssselect('.commentary-text p')[0].text
            sub_comment = comment.split(',')
            players_text = sub_comment[0]

            runs_text = sub_comment[1].strip()
            self.populateStriker(players_text, over_info, players)
            self.populateRuns(runs_text, over_info)
            self.populateExtras(runs_text, over_info)
            boundry_or_wicket_text = None

            if ball.cssselect('.commsImportant'):
                boundry_or_wicket_text = ball.cssselect('.commsImportant')[0].text
                self.populateBoundryInfo(boundry_or_wicket_text, over_info)
                # self.populateWicketInfo(boundry_or_wicket_text, over_info)

            self.populateBowler(players_text, over_info, players)
            over_str = over_info['over_str']
            del over_info['over_str']
            inning[over_str] = over_info

        return inning, team

    def processMatch(self, url):
        # TODO: Instead of hardcode URL, take as an argument either from CLI or file
        # url = 'http://www.espncricinfo.com/india-v-england-2016-17/engine/match/1034829.html'
        url = url
        match = {}
        match['info'] = self.getMatchInfo(url)

        inning_1, team_1 = self.getInningsInfo(url, 1, match['info'])
        inning_2, team_2 = self.getInningsInfo(url, 2, match['info'])

        innings = {
            '1st_innings': {
                'team': team_1,
                'deliveries': inning_1,
                'team_1_Historical_WK': match['info']['Team_1_Historical_WK']
            },
            '2nd_innings': {
                'team': team_2,
                'deliveries': inning_2,
                'team_2_Historical_WK': match['info']['Team_2_Historical_WK']
            }
        }
        match['innings'] = innings

        # TODO: need to move this code to better place
        toss_winner = match['info']['toss']
        match['info']['toss'] = {
            'winner': toss_winner,
            'decision': 'bat' if toss_winner == team_1 else 'field'
        }

        return match

    def populateMatchMetadataTable(self, tournamentMetadata, matchInfo, teams, matchType):

        """
        Helper method to populate Match metadata for historical data.
        :param tournament:
        :param matchInfo: HistoricalData matchInfo object.
        :param teams: list of teams playing a match.
        :return:
        """
        # TODO: This has historical data specific fields. May need to change it to make more usable
        matchMetadata = MatchMetadata()
        matchMetadata.tournament = tournamentMetadata
        matchMetadata.team_1 = teams[0]
        matchMetadata.team_2 = teams[1]
        if 'by' not in matchInfo['outcome']:
            pass
        else:
            if 'runs' in matchInfo['outcome']['by']:
                outcome = matchInfo['outcome']['by']['runs']
            elif 'wickets' in matchInfo['outcome']['by']:
                outcome = matchInfo['outcome']['by']['wickets']

            matchMetadata.result_diff = outcome
        matchMetadata.outcome = outcome
        matchMetadata.status = COMPLETED
        if 'winner' in matchInfo['outcome']:
            matchMetadata.winner = teams[0] if teams[0].name == str(matchInfo['outcome']['winner']).strip() else teams[1]

        dates = [
        matchMetadata.when = dates
        matchMetadata.start_date = dates[0]

        matchMetadata.overs_per_side = matchInfo['overs']
        matchMetadata.toss_decision = matchInfo['toss']['decision']
        matchMetadata.toss_winner = teams[0] if teams[0].name == str(matchInfo['toss']['winner']).strip() else \
            teams[1]

        matchMetadata.venue = {'venue': matchInfo['venue'],
                               'city': matchInfo['city'] if 'city' in matchInfo else None}
        if 'player_of_match' in matchInfo:
            player_of_the_match = str(matchInfo['player_of_match'][0]).strip()
            matchMetadata.player_of_the_match, created = PlayerMetadata.objects.get_or_create(
                name=player_of_the_match,
                historical_name=player_of_the_match)

        matchMetadata.match_number = matchInfo['T20_number']
        matchMetadata.match_title = matchInfo['match_number']
        matchMetadata.match_type = matchType
        matchMetadata.save()
        return matchMetadata

    def updateWicketKeepingPoints(self, wicket, matchMetadata, wkImpactDict, stumpingPoints, catchPoints):
        """
        Update wicket keeping points and wicketkeeping dictionary
        :param wicket:
        :param matchMetadata:
        :param wkImpactDict:
        :param stumpingPoints:
        :param catchPoints:
        :return:
        """
        wkImpact, created = WicketKeepingImpact.objects.get_or_create(player=wicket.fielder_1, match=matchMetadata)
        wkImpact.total_stumping_points += stumpingPoints
        wkImpact.total_catch_points += catchPoints
        wkImpact.num_dismissals += 1
        if 3 <= wkImpact.num_dismissals < 5:
            wkImpact.special_wk_points = 15
        if wkImpact.num_dismissals >= 5:
            wkImpact.special_wk_points = 30
        wkImpact.total_wicket_keeping_impact = wkImpact.total_stumping_points + wkImpact.special_wk_points + \
                                               wkImpact.total_catch_points
        wkImpact.save()
        wkImpactDict[wkImpact.player.name] = wkImpact

    def createFieldingImpact(self, wicket, matchMetadata, fieldingImpactDict, wkImpactDict, manualWkNameList):
        """
        Create or update fielding and wicketKeepingImpact of a player.
        :param fieldingImpactDict:
        :param wicketJson:
        :param fielder:
        :param fielderName:
        :param matchMetadata:
        :return:
        """
        # TODO: This has historical data specific fields. May need to change it to make more usable

        if wicket.mode == 'stumped':
            stumpingPoints = 15
            catchPoints = 0
            self.updateWicketKeepingPoints(wicket, matchMetadata, wkImpactDict, stumpingPoints, catchPoints)
            return

        if wicket.fielder_1 is not None:
            fieldingImpact, created = FieldingImpact.objects.get_or_create(player=wicket.fielder_1, match=matchMetadata)
            if wicket.mode == 'run out':
                if wicket.fielder_2 is None:
                    fieldingImpact.direct_hit_points += 10
                    fieldingImpact.num_dismissals += 1
                else:
                    fieldingImpact.non_direct_hit_points += 5
                    fieldingImpact2, created = FieldingImpact.objects.get_or_create(player=wicket.fielder_2,
                                                                                    match=matchMetadata)
                    fieldingImpact2.non_direct_hit_points += 5
                    fieldingImpact2.total_fielding_impact += 5
                    fieldingImpact2.save()
                    fieldingImpactDict[fieldingImpact2.player.name] = fieldingImpact2
            elif wicket.mode == 'caught':
                if wicket.fielder_1.name in manualWkNameList:
                    stumpingPoints = 0
                    catchPoints = 15
                    self.updateWicketKeepingPoints(wicket, matchMetadata, wkImpactDict, stumpingPoints, catchPoints)
                else:
                    fieldingImpact.total_catch_points += 10
                    fieldingImpact.num_dismissals += 1
            if 3 <= fieldingImpact.num_dismissals < 5:
                fieldingImpact.special_fielding_points = 10
            if fieldingImpact.num_dismissals >= 5:
                fieldingImpact.special_fielding_points = 20
            fieldingImpact.total_fielding_impact = fieldingImpact.direct_hit_points + \
                                                   fieldingImpact.non_direct_hit_points + \
                                                   fieldingImpact.total_catch_points + \
                                                   fieldingImpact.special_fielding_points
            fieldingImpact.save()
            fieldingImpactDict[fieldingImpact.player.name] = fieldingImpact

    def getCorrectOver(self, oversForBowler):
        """
        Return correct over decimal for the given over.
        :param oversForBowler:
        :return:
        """
        overDigits = oversForBowler.as_tuple().digits
        ballDigit = overDigits[-1]
        if ballDigit == 6:
            # To increase to next over.
            oversForBowler += decimal.Decimal('0.4')
        return oversForBowler

    def createPlayerScorecard(self, playerScoreCardDict, playerName, player, team, scoreCard, batsmanScore,
                              bowlingScore):
        """
        Creates or updates the player scorecard for the given parameters.
        :param playerScoreCard:
        :param playerScoreCardDict:
        :param playerName:
        :param player:
        :param team:
        :param playerScoreCard1:
        :return:
        """
        playerScoreCard = PlayerScoreCard()
        if playerName in playerScoreCardDict:
            playerScoreCard = playerScoreCardDict[playerName]
        if batsmanScore is None:
            batsmanScore = playerScoreCard.batting_score
        if bowlingScore is None:
            bowlingScore = playerScoreCard.bowling_score
        playerScoreCard.batting_score = batsmanScore
        playerScoreCard.team = team
        playerScoreCard.player = player
        playerScoreCard.score_card_metadata = scoreCard
        playerScoreCard.bowling_score = bowlingScore
        playerScoreCard.save()
        playerScoreCardDict[playerName] = playerScoreCard

    def updateBattingImpact(self, battingImpactDict, battingScoreDict, totalData):
        """
        Update batting impact for each player on each ball particularly SR boost and total points.
        :param battingImpactDict:
        :param battingScoreDict:
        :param totalMatchRuns:
        :param totalMatchBalls:
        :return:
        """
        totalMatchRuns = totalData[0]
        totalMatchBalls = totalData[1]
        if totalMatchBalls == 0:
            currentMatchStrikeRate = 0.0
        else:
            currentMatchStrikeRate = (totalMatchRuns / totalMatchBalls * 1.0)
        for batsmanName, battingImpact in battingImpactDict.iteritems():
            # TODO: Maybe want to change later so that battingScoreDict always has player when it reaches this point.
            if batsmanName not in battingScoreDict:
                continue
            currentStrikeRate = battingScoreDict[batsmanName].strike_rate
            numBalls = battingScoreDict[batsmanName].balls
            srBoost = ((float(currentStrikeRate) / 100.0) - currentMatchStrikeRate) * SR_BOOST_CONSTANT * numBalls
            battingImpact.strike_rate_boost = srBoost
            battingImpact.total_batting_impact = battingImpact.total_landmark_points + battingImpact.total_base_points \
                                                 + battingImpact.special_batting_points \
                                                 + int(
                battingImpact.partnership_points) + battingImpact.early_bird_points \
                                                 + battingImpact.hattrick_boost_points + battingImpact.strike_rate_boost \
                                                 + battingImpact.knockout_punch_points + battingImpact.super_over_points
            battingImpact.save()
            battingImpactDict[batsmanName] = battingImpact

    def updateBowlingImpact(self, bowlingImpactDict, bowlingScoreDict, totalData):
        """
        Updates bowling impact for each player on each ball particularly ER boost and total points.
        :param bowlingImpactDict:
        :param bowlingScoreDict:
        :param totalMatchRuns:
        :param totalMatchBalls:
        :return:
        """
        totalMatchRuns = totalData[0]
        totalMatchBalls = totalData[1]
        if totalMatchBalls == 0:
            currentMatchEconomyRate = 0.0
        else:
            currentMatchEconomyRate = (totalMatchRuns / totalMatchBalls * 1.0)
        for bowlerName, bowlingImpact in bowlingImpactDict.iteritems():
            currentEconomyRate = bowlingScoreDict[bowlerName].economy_rate
            numBalls = bowlingScoreDict[bowlerName].num_balls
            erBoost = (currentMatchEconomyRate - (currentEconomyRate / 6.0)) * ER_BOOST_CONSTANT * numBalls
            bowlingImpact.economy_rate_boost = erBoost
            bowlingImpact.total_bowling_impact = bowlingImpact.total_landmark_points + bowlingImpact.total_base_points \
                                                 + bowlingImpact.special_bowling_points + bowlingImpact.dot_balls_boost \
                                                 + bowlingImpact.maiden_boost + bowlingImpact.early_bird_points \
                                                 + bowlingImpact.hattrick_boost_points + bowlingImpact.pen_extra_points \
                                                 + bowlingImpact.economy_rate_boost \
                                                 + bowlingImpact.knockout_punch_points + bowlingImpact.super_over_points
            bowlingImpact.save()
            bowlingImpactDict[bowlerName] = bowlingImpact

    def updateKnockOutPoints(self, battingImpactDict, bowlingImpactDict, totalInningsBalls, deliveries,
                             battingScoreCard):
        """
        Update knock out punch points and hence total points for batsmen and bowler based on the window.
        :param battingImpactDict:
        :return:
        """
        # TODO: This has historical data specific fields. May need to change it to make more usable
        # 25 percent of the balls for the innings
        numKnockOutPunchBalls = totalInningsBalls / 4
        logger.info("Num knock out balls for the innings: " + str(numKnockOutPunchBalls))
        oversBowledTuple = battingScoreCard.total_overs.as_tuple().digits
        knockOutWindowStart = totalInningsBalls - numKnockOutPunchBalls

        # Calculating over to start from.
        overToStart = int(knockOutWindowStart / 6)
        ballToStart = int((knockOutWindowStart % 6) + 1)

        # TODO: Change to make it more flexible for 50 overs.
        if overToStart >= 15:
            return
        logger.info("ball to start: " + str(ballToStart))
        # Special case in case its end of the over. Then start from next.
        deliveryKey = str(overToStart) + '.' + str(ballToStart)
        decimalDeliveryKey = decimal.Decimal(deliveryKey)
        # for ball in deliveries: # previous code
        for ball, nestedItem in deliveries.iteritems():
            currentBall = decimal.Decimal(ball)
            if currentBall < decimalDeliveryKey:
                continue
            over = int(currentBall)

            # TODO: Change to make it more flexible for 50 overs.
            if numKnockOutPunchBalls <= 0 or over >= 15:
                break

            # deliveryInfo = ball.values()[0] # previous code
            deliveryInfo = ball

            # Update batting impact.
            batsmanName = nestedItem['batsman']
            print "batsmanNamebatsmanName: ", batsmanName[0]
            print "battingImpactDictbattingImpactDict: ", battingImpactDict
            battingImpact = battingImpactDict[batsmanName[0]]
            battingPointsToBeAdded = 0
            totalRunsInBall = nestedItem['runs']['total']
            if totalRunsInBall == 0:
                battingPointsToBeAdded -= 1
            batsmanRuns = nestedItem['runs']['batsman']
            if batsmanRuns >= 4:
                battingPointsToBeAdded += batsmanRuns
            battingImpact.knockout_punch_points += battingPointsToBeAdded
            battingImpact.total_batting_impact += battingPointsToBeAdded
            battingImpact.save()
            battingImpactDict[batsmanName[0]] = battingImpact

            # Update bowling impact
            bowlerName = nestedItem['bowler']
            bowlingImpact = bowlingImpactDict[bowlerName[0]]
            bowlingPointsToBeAdded = 0
            if totalRunsInBall == 0:
                bowlingPointsToBeAdded += 1
            if 'wicket' in deliveryInfo and nestedItem['wicket']['kind'] != 'run out':
                bowlingPointsToBeAdded += 10
            bowlingImpact.knockout_punch_points += bowlingPointsToBeAdded
            bowlingImpact.total_bowling_impact += bowlingPointsToBeAdded
            bowlingImpact.save()
            bowlingImpactDict[bowlerName[0]] = bowlingImpact

            numKnockOutPunchBalls -= 1

    def batsmanHattrick(self, lastThreeBalls):
        """
        returns hattrick points to be added to the batsman score.
        :param lastTwoBalls:
        :param points:
        :return:
        """
        if len(lastThreeBalls) < 3:
            return 0
        points = 6
        for ball in lastThreeBalls:
            if ball < 4:
                return 0
            if ball < points:
                points = ball
        return points

    def bowlerHattrick(self, lastThreeBalls):
        """
        returns hattrick points to be added to the bowler score.
        :param lastTwoBalls:
        :param points:
        :return:
        """
        if len(lastThreeBalls) < 3:
            return 0
        points = 10
        for ball in lastThreeBalls:
            if not ball:
                return 0
        return points

    def getCorrectPlayerObject(self, playerName, substitutes):
        """
        Remove sub from the player for substitute
        :param playerName:
        :return:
        """
        if 'sub' in playerName:
            playerName = playerName[:-6]
            # TODO: need to update the player meta data name and historical name
            player, created = PlayerMetadata.objects.get_or_create(name=playerName, historical_name=playerName)
            substitutes.add(player)
        else:
            # TODO: need to update the player meta data name and historical name
            player, created = PlayerMetadata.objects.get_or_create(name=playerName, historical_name=playerName)
        return player

    def processSingleInning(self, tournamentMetadata, matchMetadata, inning, teamBatting, teamBowling,
                            playerScoreCardDict, totalData, manualWkNameList, substitutes):

        """
        Processes single inning of a match.
        :param tournamentMetadata:
        :param matchMetadata:
        :param inning:
        :return:
        """
        # TODO: This has historical data specific fields. May need to change it to make more usable

        decimal.getcontext().prec = 1
        # Create ScoreCard
        battingScoreCard, created = ScoreCardMetadata.objects.get_or_create(team=teamBatting, match_metadata=matchMetadata)
        bowlingScoreCard, created = ScoreCardMetadata.objects.get_or_create(team=teamBowling, match_metadata=matchMetadata)
        totalMatchRuns = totalData[0]
        totalMatchBalls = totalData[1]
        # Set defaults
        deliveries = inning['deliveries']
        totalInningsBalls = 0
        decimal.getcontext().prec = 1
        currentBall = decimal.Decimal('0.1')
        extraRuns = 0
        total = 0
        wickets = 0
        batsmen = set()
        bowlers = set()
        batsmenDict = dict()
        bowlersDict = dict()
        battingImpactDict = dict()
        bowlingImpactDict = dict()
        fieldingImpactDict = dict()
        playerImpactDict = dict()
        wkImpactDict = dict()
        battingPosition = 1
        bowlingPosition = 1
        isEarlyBird = True
        isKnockOutPeriod = False
        maidenCounter = 0
        maidenDict = dict()
        for i in xrange(0, 20):
            maidenDict[i] = 0

        for ball, nestedItem in inning['deliveries'].iteritems():

            extraObjs = []
            bowlerWicketFlag = False
            deliveryInfo = ball
            # deliveryInfo = ball.values()[0]
            runs = nestedItem['runs']

            # currentBall = decimal.Decimal(str(ball.keys()[0])) # previous code
            currentBall = decimal.Decimal(ball)
            currentOver = int(currentBall)
            runsForBatsmanCurrentBall = runs['batsman']
            totalRunsCurrentBall = runs['total']
            totalMatchRuns += totalRunsCurrentBall
            batsmanName = nestedItem['batsman']
            logger.info("ball %s", str(ball))
            logger.info("batsmanName %s", str(batsmanName))

            # Create batsman score
            batsmanScore = BattingScore()
            if batsmanName[0] in batsmenDict:
                batsmanScore = batsmenDict[batsmanName[0]]
                batsmanScore.balls += 1
                batsmanScore.runs += runsForBatsmanCurrentBall
            else:
                batsmanScore = BattingScore()
                batsmanScore.balls = 1
                batsmanScore.status = BattingScore.NOT_OUT
                batsmanScore.position = battingPosition
                battingPosition += 1
                batsmanScore.runs = runsForBatsmanCurrentBall
                batsmanScore.strike_rate = 0.0
                batsmanScore.save()
                batsmenDict[batsmanName[0]] = batsmanScore

            batsman, created = PlayerMetadata.objects.get_or_create(name=batsmanName[0], historical_name=batsmanName[1])
            batsmen.add(batsman)

            # Create bowler score.
            bowlerName = nestedItem['bowler']
            logger.info("bowlerName %s", bowlerName)
            bowler, created = PlayerMetadata.objects.get_or_create(name=bowlerName[0], historical_name=bowlerName[1])
            bowlers.add(bowler)
            bowlingScore = BowlingScore()
            if bowlerName[0] in bowlersDict:
                bowlingScore = bowlersDict[bowlerName[0]]
            else:
                bowlingScore.dot_balls = 0
                bowlingScore.extras = 0
                bowlingScore.num_wickets = 0
                bowlingScore.runs = 0
                bowlingScore.overs = decimal.Decimal('0.0')
                bowlingScore.num_balls = 0
                bowlingScore.position = bowlingPosition
                bowlingPosition += 1
                bowlingScore.save()
                bowlersDict[bowlerName[0]] = bowlingScore

            # Check for dot ball.
            if totalRunsCurrentBall == 0:
                bowlingScore.dot_balls += 1
                maidenDict[currentOver] += 1
            else:
                maidenDict[currentOver] = 0
            bowlingScore.runs += runs['batsman']

            # Special work for extras.
            extraInDelivery = runs['extras']
            countBallBowled = 1
            if extraInDelivery > 0:
                totalMatchRuns -= extraInDelivery
                extraFromDeliveryObj = nestedItem['extras']
                for key, val in extraFromDeliveryObj.iteritems():
                    extra = Extras()
                    if key == 'wides':
                        batsmanScore.balls -= 1
                        bowlingScore.extras += val
                        countBallBowled = 0
                    if key == 'noballs':
                        bowlingScore.extras += val
                        countBallBowled = 0
                    if "byes" not in key:
                        bowlingScore.runs += val
                    else:
                        bowlingScore.dot_balls += 1
                        maidenDict[currentOver] += 1
                    extra.type = key
                    extra.value = val
                    extraObjs.append(extra)

            bowlingScore.num_balls += countBallBowled
            decimal.getcontext().prec = 2
            oversForBowler = bowlingScore.overs
            if countBallBowled > 0:
                totalMatchBalls += 1
                totalInningsBalls += 1
                oversForBowler += decimal.Decimal('0.1')
                oversForBowler = self.getCorrectOver(oversForBowler)
            bowlingScore.overs = oversForBowler
            if bowlingScore.num_balls > 0:
                bowlingScore.economy_rate = (bowlingScore.runs / (bowlingScore.num_balls * 1.0)) * (6.0)
            extraRuns += extraInDelivery
            total += runs['total']

            # Store wicket and fielding impact.
            if 'wicket' in nestedItem:
                # Set wicket object here
                wicketObj = Wicket()
                wicketJson = nestedItem['wicket']
                batsmanOut = str(wicketJson['player_out']).strip()
                # TODO: need to update the player meta data name and historical name
                wicketObj.batsman, created = PlayerMetadata.objects.get_or_create(name=batsmanOut, historical_name=batsmanOut)
                wicketObj.mode = wicketJson['kind']
                if wicketJson['kind'] == 'run out':
                    wicketObj.bowler = None
                else:
                    wicketObj.bowler = bowler
                    bowlerWicketFlag = True

                # fielder data not coming in the dict

                if 'fielders' in wicketJson:
                    fielders = wicketJson['fielders']
                    fielderObjs = []
                    fielder_1 = str(fielders[0]).strip()
                    wicketObj.fielder_1 = self.getCorrectPlayerObject(fielder_1, substitutes)
                    fielderObjs.append(wicketObj.fielder_1)
                    if len(fielders) > 1:
                        fielder_2 = str(fielders[1]).strip()
                        wicketObj.fielder_2 = self.getCorrectPlayerObject(fielder_2, substitutes)
                        fielderObjs.append(wicketObj.fielder_2)

                wicketObj.save()
                self.createFieldingImpact(wicketObj, matchMetadata, fieldingImpactDict, wkImpactDict, manualWkNameList)
                if wicketJson['kind'] == 'run out':
                    if batsmanOut in batsmenDict:
                        outScore = batsmenDict[batsmanOut]
                    else:
                        outScore = BattingScore()
                        outScore.balls = 0
                        outScore.position = battingPosition
                        battingPosition += 1
                        outScore.runs = 0
                        outScore.strike_rate = 0.0
                    outScore.wicket = wicketObj
                    outScore.status = BattingScore.OUT
                    if batsmanOut != batsmanName:
                        outScore.save()
                else:
                    batsmanScore.wicket = wicketObj
                    batsmanScore.status = BattingScore.OUT
                    bowlingScore.num_wickets += 1
                    bowlingScore.wickets.add(wicketObj)

                wickets += 1

            if batsmanScore.balls > 0:
                batsmanScore.strike_rate = decimal.Decimal((batsmanScore.runs / (batsmanScore.balls * 1.0)) * 100)
            else:
                batsmanScore.strike_rate = decimal.Decimal('0.0')

            partnerName = str(nestedItem['non_striker']).strip()
            # TODO: need to update the player meta data name and historical name for non striker
            # logger.info("partnerName %s", str(partnerName[0]))
            # partner, created = PlayerMetadata.objects.get_or_create(name=partnerName, historical_name=partnerName)
            # batsmen.add(partner)

            # Save information.
            # TODO: Change when calculating bowling impact.
            batsmanScore.save()
            bowlingScore.save()
            battingScoreCard.total_runs = total
            currentTotalOvers = self.getCorrectOver(decimal.Decimal(currentBall))
            battingScoreCard.total_overs = currentTotalOvers
            battingScoreCard.total_extras = extraRuns
            battingScoreCard.total_wickets = wickets
            battingScoreCard.save()
            bowlingScoreCard.save()

            for extra in extraObjs:
                extraVal = extra.value
                extra, created = Extras.objects.get_or_create(score_card=battingScoreCard, type=extra.type)
                extra.value += extraVal
                extra.save()
            self.createPlayerScorecard(playerScoreCardDict, batsmanName[0], batsman, teamBatting, battingScoreCard, batsmanScore,
                                       None)
            self.createPlayerScorecard(playerScoreCardDict, bowlerName[0], bowler, teamBowling, bowlingScoreCard, None,
                                       bowlingScore)

            # Setting early bird and knock out period.
            oversBowledTuple = battingScoreCard.total_overs.as_tuple().digits
            if len(oversBowledTuple) > 1:
                overNum = int(battingScoreCard.total_overs)
                if isEarlyBird and (overNum >= 5):
                    isEarlyBird = False
                logger.debug("Over num: " + str(overNum))
                logger.debug("Overs " + str(battingScoreCard.total_overs))
                if not isKnockOutPeriod and overNum >= 15:
                    logger.debug("Setting knock out period to true ")
                    isKnockOutPeriod = True

            # Populate batting Impact
            tempLastBalls = []

            batsmanImpact, created = BattingImpact.objects.get_or_create(player=batsman, match=matchMetadata)

            if created:
                batsmanImpact.last_three_balls = tempLastBalls

            currentNumRunsBatsman = batsmanScore.runs
            batsmanImpact.total_base_points = currentNumRunsBatsman
            landMarkPoints = 0
            if currentNumRunsBatsman >= 30:
                landMarkPoints = 10
            if currentNumRunsBatsman >= 75:
                landMarkPoints = 20
            if currentNumRunsBatsman >= 100:
                landMarkPoints = 40
            if currentNumRunsBatsman >= 150:
                landMarkPoints = 60
            batsmanImpact.total_landmark_points = landMarkPoints
            if currentNumRunsBatsman > 150:
                batsmanImpact.special_batting_points += runsForBatsmanCurrentBall
            if isEarlyBird and runsForBatsmanCurrentBall >= 4:
                # Number of 4s into 4 and number of 6s into 6
                batsmanImpact.early_bird_points += runsForBatsmanCurrentBall

            if isKnockOutPeriod:
                if runsForBatsmanCurrentBall >= 4:
                    logger.info("Adding knock out points: " + str(runsForBatsmanCurrentBall))
                    batsmanImpact.knockout_punch_points += runsForBatsmanCurrentBall
                if totalRunsCurrentBall == 0:
                    logger.info("Negative knock out points: ")
                    batsmanImpact.knockout_punch_points -= 1

            # batsmanHattrickPoints = 6
            lastThreeBalls = batsmanImpact.last_three_balls
            if lastThreeBalls is None:
                lastThreeBalls = []
            if len(lastThreeBalls) == 3:
                lastThreeBalls.pop(0)
            lastThreeBalls.append(runsForBatsmanCurrentBall)
            batsmanHattrickPoints = self.batsmanHattrick(lastThreeBalls)
            if batsmanHattrickPoints > 0:
                lastThreeBalls = []
            batsmanImpact.hattrick_boost_points += batsmanHattrickPoints
            batsmanImpact.last_three_balls = lastThreeBalls

            # partnerImpact, created = BattingImpact.objects.get_or_create(player=partner, match=matchMetadata)
            #
            # partnerImpact.partnership_points += runsForBatsmanCurrentBall / 2
            # battingImpactDict[partnerName] = partnerImpact
            # battingImpactDict[batsmanName] = batsmanImpact

            totalData = (totalMatchRuns, totalMatchBalls)
            # Update total batting points and strike rate boost.
            self.updateBattingImpact(battingImpactDict, batsmenDict, totalData)

            tempLastWickets = []

            bowlingImpact, created = BowlingImpact.objects.get_or_create(player=bowler, match=matchMetadata)

            if created:
                bowlingImpact.last_three_balls = tempLastWickets
            numWicketsBowler = bowlingScore.num_wickets
            bowlingImpact.total_base_points = numWicketsBowler * 25

            bowlingLandmarkPoints = 0
            if numWicketsBowler >= 3:
                bowlingLandmarkPoints = 10
            if numWicketsBowler >= 5:
                bowlingLandmarkPoints = 30
            bowlingImpact.total_landmark_points = bowlingLandmarkPoints
            if numWicketsBowler > 5:
                bowlingImpact.special_bowling_points = (numWicketsBowler - 5) * 25
            bowlingImpact.dot_balls_boost = bowlingScore.dot_balls
            if maidenDict[currentOver] == 6:
                bowlingImpact.maiden_boost += 10
            bowlingImpact.pen_extra_points = (bowlingScore.extras * (-1))

            if isEarlyBird and numWicketsBowler > 0:
                bowlingImpact.early_bird_points = numWicketsBowler * 10

            if isKnockOutPeriod:
                if bowlerWicketFlag:
                    bowlingImpact.knockout_punch_points += 10
                if totalRunsCurrentBall == 0:
                    bowlingImpact.knockout_punch_points += 1

            lastThreeBallsBowler = bowlingImpact.last_three_balls
            if lastThreeBallsBowler is None:
                lastThreeBallsBowler = []
            if len(lastThreeBallsBowler) == 3:
                lastThreeBallsBowler.pop(0)
            lastThreeBallsBowler.append(bowlerWicketFlag)
            bowlerHattrickPoints = self.bowlerHattrick(lastThreeBallsBowler)
            if bowlerHattrickPoints > 0:
                lastThreeBallsBowler = []
            bowlingImpact.hattrick_boost_points += bowlerHattrickPoints
            bowlingImpact.last_three_balls = lastThreeBallsBowler

            bowlingImpactDict[bowlerName[0]] = bowlingImpact

            # Update total bowling points and economy rate boost.
            for bowlerName, bowlingImpact in bowlingImpactDict.iteritems():
                print '{}-{}'.format(bowlerName, bowlingImpact)

            self.updateBowlingImpact(bowlingImpactDict, bowlersDict, totalData)

            # TODO: For each player in player score card dictionary update strike rate , knock out and total points.
            self.updatePlayerImpactCards(battingImpactDict, bowlingImpactDict, fieldingImpactDict, wkImpactDict,
                                         teamBatting, teamBowling, tournamentMetadata, playerImpactDict)
        # TODO: Update knowck out kpunch points for the window and hence total points.

        # self.updateKnockOutPoints(battingImpactDict, bowlingImpactDict, totalInningsBalls, deliveries, battingScoreCard)
        self.updatePlayerImpactCards(battingImpactDict, bowlingImpactDict, fieldingImpactDict, wkImpactDict, teamBatting
                                     , teamBowling, tournamentMetadata, playerImpactDict)
        return totalData, batsmen, bowlers


    def updatePlayerImpactCards(self, battingImpactDict, bowlingImpactDict, fieldingImpactDict, wkImpactDict,
                                teamBatting, teamBowling, tournamentMetadata, playerImpactDict):


        """
        Helper method to update all the player impact cards.
        :param playerImpactDict:
        :param totalMatchRuns:
        :param totalMatchBalls:
        :return:
        """
        for playerName, battingImpact in battingImpactDict.iteritems():
            if playerName in playerImpactDict:
                playerImpactCard = playerImpactDict[playerName]
            else:
                playerImpactCard, created = PlayerImpactCard.objects.get_or_create(player=battingImpact.player,
                                                                                   match=battingImpact.match,
                                                                                   team=teamBatting,
                                                                                   tournament=tournamentMetadata)
            playerImpactCard.batting_impact_key = battingImpact
            playerImpactCard.batting_impact = battingImpact.total_batting_impact
            playerImpactCard.total_impact = playerImpactCard.batting_impact + playerImpactCard.bowling_impact + \
                                            playerImpactCard.fielding_impact + playerImpactCard.wk_impact
            playerImpactCard.save()
            playerImpactDict[playerName] = playerImpactCard

        for playerName, bowlingImpact in bowlingImpactDict.iteritems():
            if playerName in playerImpactDict:
                playerImpactCard = playerImpactDict[playerName]
            else:
                playerImpactCard, created = PlayerImpactCard.objects.get_or_create(player=bowlingImpact.player,
                                                                                   match=bowlingImpact.match,
                                                                                   team=teamBowling,
                                                                                   tournament=tournamentMetadata)
            playerImpactCard.bowling_impact_key = bowlingImpact
            playerImpactCard.bowling_impact = bowlingImpact.total_bowling_impact
            playerImpactCard.total_impact = playerImpactCard.batting_impact + playerImpactCard.bowling_impact + \
                                            playerImpactCard.fielding_impact + playerImpactCard.wk_impact
            playerImpactCard.save()
            playerImpactDict[playerName] = playerImpactCard

        for playerName, fieldingImpact in fieldingImpactDict.iteritems():
            if playerName in playerImpactDict:
                playerImpactCard = playerImpactDict[playerName]
            else:
                playerImpactCard, created = PlayerImpactCard.objects.get_or_create(player=fieldingImpact.player,
                                                                                   match=fieldingImpact.match,
                                                                                   team=teamBowling,
                                                                                   tournament=tournamentMetadata)
            playerImpactCard.fielding_impact_key = fieldingImpact
            playerImpactCard.fielding_impact = fieldingImpact.total_fielding_impact
            playerImpactCard.total_impact = playerImpactCard.batting_impact + playerImpactCard.bowling_impact + \
                                            playerImpactCard.fielding_impact + playerImpactCard.wk_impact
            playerImpactCard.save()
            playerImpactDict[playerName] = playerImpactCard

        for playerName, wkImpact in wkImpactDict.iteritems():
            if playerName in playerImpactDict:
                playerImpactCard = playerImpactDict[playerName]
            else:
                playerImpactCard, created = PlayerImpactCard.objects.get_or_create(player=wkImpact.player,
                                                                                   match=wkImpact.match,
                                                                                   team=teamBowling,
                                                                                   tournament=tournamentMetadata)
            playerImpactCard.wk_impact_key = wkImpact
            playerImpactCard.wk_impact = wkImpact.total_wicket_keeping_impact
            playerImpactCard.total_impact = playerImpactCard.batting_impact + playerImpactCard.bowling_impact + \
                                            playerImpactCard.fielding_impact + playerImpactCard.wk_impact
            playerImpactCard.save()
            playerImpactDict[playerName] = playerImpactCard

    def calculateAvgFielderImpact(self, currentNumMatches, currentAvgImpact, matchImpact, isSubstitute):
        """
        Calculates average impact from the current match.
        :return:
        """
        currentTotalImpact = currentAvgImpact * currentNumMatches
        currentTotalImpact += matchImpact
        if not isSubstitute:
            currentNumMatches += 1
        if isSubstitute and currentNumMatches == 0:
            currentAvgImpact = currentTotalImpact
        else:
            currentAvgImpact = currentTotalImpact / currentNumMatches
        return currentAvgImpact

    def calculateAvgImpact(self, currentNumMatches, currentAvgImpact, matchImpact):
        """
        Calculates average impact from the current match.
        :return:
        """
        currentTotalImpact = currentAvgImpact * currentNumMatches
        currentTotalImpact += matchImpact
        currentAvgImpact = currentTotalImpact / (currentNumMatches + 1)
        return currentAvgImpact

    def updateHistoricalImpact(self, impactCards, substitutes, matchType):
        """
        Updates or creates historical impact of the players.
        :param impactCards:
        :return:
        """
        for impactCard in impactCards:
            historicalImpact, created = HistoricalPlayerImpact.objects.get_or_create(player=impactCard.player,
                                                                                     match_type=matchType)
            isSubstitute = False
            if impactCard.player in substitutes:
                isSubstitute = True
            currentNumMatches = historicalImpact.num_matches
            historicalImpact.avg_total_impact = self.calculateAvgImpact(currentNumMatches,
                                                                        historicalImpact.avg_total_impact,
                                                                        impactCard.total_impact)
            historicalImpact.avg_batting_impact = self.calculateAvgImpact(currentNumMatches,
                                                                          historicalImpact.avg_batting_impact,
                                                                          impactCard.batting_impact)
            historicalImpact.avg_bowling_impact = self.calculateAvgImpact(currentNumMatches,
                                                                          historicalImpact.avg_bowling_impact,
                                                                          impactCard.bowling_impact)
            historicalImpact.avg_fielding_impact = self.calculateAvgFielderImpact(currentNumMatches,
                                                                                  historicalImpact.avg_fielding_impact,
                                                                                  impactCard.fielding_impact,
                                                                                  isSubstitute)
            historicalImpact.avg_wk_impact = self.calculateAvgImpact(currentNumMatches, historicalImpact.avg_wk_impact,
                                                                     impactCard.wk_impact)
            historicalImpact.num_hots += 1 if impactCard.hot_impact else 0
            historicalImpact.num_nots += 1 if impactCard.not_impact else 0
            if not isSubstitute:
                historicalImpact.num_matches += 1
            historicalImpact.save()

    def add_to_team(self, team, batsmen, bowlers):
        """
        Add players to a team
        :param team:
        :param batsmen:
        :param bowlers:
        :return:
        """
        batsmen = set(batsmen)
        for player in batsmen:
            team.current_players.add(player)
        bowlers = set(bowlers)
        for player in bowlers:
            team.current_players.add(player)

    def updateTournamentImpact(self, impactCards, tournament, substitutes, matchType):
        """
        Updates or creates tournament impact of the players.
        :param impactCards:
        :return:
        """
        for impactCard in impactCards:
            tournamentImpact, created = TournamentPlayerImpact.objects.get_or_create(player=impactCard.player,
                                                                                     tournament=tournament,
                                                                                     match_type=matchType)
            tournamentImpact.total_impact += impactCard.total_impact
            tournamentImpact.total_batting_impact += impactCard.batting_impact
            tournamentImpact.total_bowling_impact += impactCard.bowling_impact
            tournamentImpact.total_fielding_impact += impactCard.fielding_impact
            tournamentImpact.total_wk_impact += impactCard.wk_impact
            if impactCard.player not in substitutes:
                tournamentImpact.num_matches += 1
            tournamentImpact.save()

    def setHotAndNotFields(self, impactCards):
        """
        Sets hot and not fields for the impact cards.
        :param impactCards:
        :return:
        """
        # To get top 5 and last 3
        hotThreshold = impactCards[4].total_impact
        notThreshold = impactCards[len(impactCards) - 3].total_impact
        for impactCard in impactCards:
            if impactCard.total_impact >= hotThreshold:
                impactCard.hot_impact = True
                impactCard.save()
                continue
            if impactCard.total_impact <= notThreshold:
                impactCard.not_impact = True
                impactCard.save()
                continue

    def processInnings(self, tournamentMetadata, matchMetadata, innings, teams, matchType):
        """
        Method to process all the innings. This will internally populate impact and scorecard tables.
        Also dynamically update team/player tables for the time being.
        :param tournamentMetadata: Tournament model object for defining reference(s)
        :param matchMetadata: Match model object for defining reference(s)
        :param innings: innings list from yaml files.
        :param teams: Teams object for teams playing the match.
        :return:
        """

        firstInning = innings['1st_innings']
        secondInning = innings['2nd_innings']

        team1stInning = teams[0] if teams[0].name == str(firstInning['team']).strip() else teams[1]
        team2ndInning = teams[0] if teams[0].name == str(secondInning['team']).strip() else teams[1]
        batsmen_1 = set()
        batsmen_2 = set()
        bowlers_1 = set()
        bowlers_2 = set()
        substitutes = set()
        substitutessecond = set()
        manualWkNameList = []
        manualWkNameList.append(firstInning['team_1_Historical_WK'])
        manualWkNameList.append(secondInning['team_2_Historical_WK'])
        playerScoreCardDict = dict()
        totalMatchRuns = 0
        totalMatchBalls = 0
        totalData = (totalMatchRuns, totalMatchBalls)

        totalData, batsmen_1, bowlers_2 = self.processSingleInning(tournamentMetadata, matchMetadata, firstInning,
                                                                   team1stInning,
                                                                   team2ndInning, playerScoreCardDict, totalData,
                                                                   manualWkNameList, substitutes)
        logger.info("Total data " + str(totalData))
        if secondInning is not None:
            totalData, batsmen_2, bowlers_1 = self.processSingleInning(tournamentMetadata, matchMetadata, secondInning,
                                                                       team2ndInning, team1stInning, playerScoreCardDict
                                                                       , totalData, manualWkNameList, substitutes)

        #Process super over for the teams.
        #For each delivery.
        #Update super over score

        impactCards = PlayerImpactCard.objects.filter(match=matchMetadata).order_by('-total_impact')
        self.setHotAndNotFields(impactCards)
        self.updateHistoricalImpact(impactCards, substitutes, matchType)
        self.updateTournamentImpact(impactCards, tournamentMetadata, substitutes, matchType)

        self.add_to_team(team1stInning, batsmen_1, bowlers_1)
        self.add_to_team(team2ndInning, batsmen_2, bowlers_2)

    def processFile(self, matchType, url):
        """
        Processes a yaml file and populates relevant tables.
        :param fileName:
        :return:
        """

        matchData = self.processMatch(url)
        utc = pytz.utc
        try:
            testTeam_1 = Team.objects.get(name=matchData['info']['teams'][0])
            testTeam_2 = Team.objects.get(name=matchData['info']['teams'][1])
            matchExist = MatchMetadata.objects.get(team_1=testTeam_1, team_2=testTeam_2,
                                                   start_date=matchData['info']['dates'][0], )
        except ObjectDoesNotExist:
            matchExist = None

        if matchExist is None:
            logger.info("Match doesn't exist")
            matchInfo = matchData['info']

            year = matchInfo['dates'][0].year
            tournamentName = str(matchData['info']['competition']).strip()
            competition = None

            tournamentName += (" " + str(year))
            teams = matchInfo['teams']
            teamsObj = []
            tournamentMetadata = TournamentMetadata()
            tournamentMetadata, created = TournamentMetadata.objects.get_or_create(name=tournamentName,
                                                                                   defaults={'status': COMPLETED})

            currentMatchDate = matchInfo['dates'][0]
            tournamentMetadata.save()
            teamIter = 0
            for team in teams:
                teamObj = Team()
                teamObj.name = str(teams[teamIter]).strip()
                teamObj.screen_name = "".join([i[0].upper() for i in str(teams[teamIter]).strip().split(" ")])
                teamObj, created = Team.objects.get_or_create(name=teamObj.name, screen_name=teamObj.screen_name)
                teamObj.team_type = teamObj.INTERNATIONAL if competition is None else teamObj.CLUB
                teamObj.current_tournament = tournamentMetadata
                teamObj.next_tournament = tournamentMetadata
                teamsObj.append(teamObj)
                teamIter += 1

            matchMetadata = self.populateMatchMetadataTable(tournamentMetadata, matchInfo, teamsObj, matchType)
            self.processInnings(tournamentMetadata, matchMetadata, matchData['innings'], teamsObj, matchType)
        else:
            logger.info(
                "Match between " + matchData['info']['teams'][0] + " and " + matchData['info']['teams'][
                    1] + " on " + str(
                    matchData['info']['dates'][0]) + " already exist")

    def add_arguments(self, parser):
        parser.add_argument('--url', nargs='?', help='url')

        parser.add_argument('--match_type', nargs='?', help='Type of matches to be processed',
                            default=T20I)

    def handle(self, *args, **options):
        matchType = options['match_type']
        url = options['url']
        self.processFile(matchType=matchType, url=url)
