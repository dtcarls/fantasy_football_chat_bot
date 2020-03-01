def get_trophies(league, week=None):
    #Gets trophies for highest score, lowest score, closest score, and biggest win
    matchups = league.box_scores(week=week)
    low_score = 99999
    low_team_name = ''
    high_score = -1
    high_team_name = ''
    closest_score = 99999
    close_winner = ''
    close_loser = ''
    largest_victory = -1
    big_loser_team_name = ''
    big_victor_team_name = ''

    for i in matchups:
        if i.home_score > high_score:
            high_score = i.home_score
            high_team_name = i.home_team.team_name
        if i.home_score < low_score:
            low_score = i.home_score
            low_team_name = i.home_team.team_name
        if i.away_score > high_score:
            high_score = i.away_score
            high_team_name = i.away_team.team_name
        if i.away_score < low_score:
            low_score = i.away_score
            low_team_name = i.away_team.team_name
        if abs(i.away_score - i.home_score) < closest_score:
            closest_score = abs(i.away_score - i.home_score)
            if i.away_score - i.home_score < 0:
                close_winner = i.home_team.team_name
                close_loser = i.away_team.team_name
            else:
                close_winner = i.away_team.team_name
                close_loser = i.home_team.team_name
        if abs(i.away_score - i.home_score) > largest_victory:
            largest_victory = abs(i.away_score - i.home_score)
            if i.away_score - i.home_score < 0:
                big_victor_team_name = i.home_team.team_name
                big_loser_team_name = i.away_team.team_name
            else:
                big_victor_team_name = i.away_team.team_name
                big_loser_team_name = i.home_team.team_name

    low_score_str = ['Low Score: %s with %.2f points' % (low_team_name, low_score)]
    high_score_str = ['High Score: %s with %.2f points' % (high_team_name, high_score)]
    close_score_str = ['Closest Match: %s barely beat %s by a margin of %.2f' % (close_winner, close_loser, closest_score)]
    largest_victory_str = ['Largest Victory: %s beat %s by a margin of %.2f' % (big_victor_team_name, big_loser_team_name, largest_victory)]

    text = ['Trophies of the week:'] + high_score_str+ low_score_str + largest_victory_str + close_score_str
    return '\n'.join(text)
