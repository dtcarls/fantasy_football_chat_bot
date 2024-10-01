#%%
import os
import anthropic
import gamedaybot.espn.functionality as espn

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

#%%
specific_team_summary_user_prompt = """
You are a witty and opinionated fantasy football analyst. Your task is to analyze the provided league data and create an entertaining summary.

Here is the fantasy football league data:
<league_data>
{{LEAGUE_DATA}}
</league_data>

Analyze this data carefully, paying attention to team rankings, scores, and any notable performances or trends.

Create a summary of the league's current state. Your summary should include:

1. The team's current ranking and record
2. Their performance in the most recent week
3. Any standout players or disappointing performances
4. How they compare to other teams in the league

Present your analysis in a humorous and slightly sarcastic tone. Feel free to use puns, pop culture references, or playful jabs at the team's performance (whether good or bad). Your goal is to inform while entertaining the reader.

Structure your response as follows:

<main_analysis>
[Your main analysis goes here. This should be 3-4 paragraphs long.]
</main_analysis>

<one_liner>
[A witty one-liner that encapsulates the team's current situation or performance]
</one_liner>

Remember, your tone should be engaging and entertaining, but make sure your analysis is based on the actual data provided. Don't make up facts, but feel free to speculate or make jokes based on the information you have.
"""

TEAM_NAME_MAPPING = """
    "Peytons Solo cup" = "POOP"
    "The Commish" = "ODGE"
    "Rick  It Ralph" = "RJL3"
    "Running backs  Dont matter" = "PHIL"
    "A B CeeDee E F G"="gerg"
    "Chudley Cannons"="TMAC"
    "Muth America"="BBW"
    "Team Pinho"="PIN"
    "The Pitts"="PITS"
    "Village Idiot"="Stoo"
    "Mark's Football Team"="GRIE"
    "Jersey Boys"="JERZ"
"""

def end_of_week_summary_for_prompt(league):
    previous_week = league.current_week - 1
    return """
        Team names:
        {team_name_mapping}
        
        Last week's scoreboard:
        {scoreboard}
        
        Optimal Scores:
        {optimal_scores}

        Trophies:
        {trophies}

        Power rankings:
        {power_rankings}

        Current Standings:
        {standings}

        Matchups for next week:
        {matchups}
    """.format(team_name_mapping=TEAM_NAME_MAPPING,
               scoreboard=espn.get_scoreboard_short(league, week=previous_week),
               optimal_scores=espn.optimal_team_scores(league, week=previous_week, full_report=True),
               trophies=espn.get_trophies(league, week=previous_week),
               power_rankings=espn.get_power_rankings(league),
               standings=espn.get_standings(league),
               matchups=espn.get_matchups(league))

def end_of_week_ai_summary(league):
    league_data_text = end_of_week_summary_for_prompt(league)
    prompt_with_data = specific_team_summary_user_prompt.replace("{{LEAGUE_DATA}}", league_data_text)
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_with_data
                    }
                ]
            }
        ]
    )
    content = message.content[0].text
    main_analysis = content.split("<main_analysis>")[1].split("</main_analysis>")[0]
    one_liner = content.split("<one_liner>")[1].split("</one_liner>")[0]
    return main_analysis, one_liner