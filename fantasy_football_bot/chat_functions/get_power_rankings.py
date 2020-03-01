def get_power_rankings(league, week=None):
    # power rankings requires an integer value, so this grabs the current week for that
    if not week:
        week = league.current_week
    #Gets current week's power rankings
    #Using 2 step dominance, as well as a combination of points scored and margin of victory.
    #It's weighted 80/15/5 respectively
    power_rankings = league.power_rankings(week=week)

    score = ['%s - %s' % (i[0], i[1].team_name) for i in power_rankings
             if i]
    text = ['Power Rankings'] + score
    return '\n'.join(text)