# Example runs (provider: gemini, model: gemini-3.1-flash-lite)

## Which team scored the most total points in 2019?

**zero_shot** (tokens: 815)

```sql
SELECT T.team_name FROM teams T JOIN team_seasons TS ON T.team_id = TS.team_id JOIN offense O ON TS.team_season_id = O.team_season_id WHERE TS.season = 2019 ORDER BY O.total_points DESC LIMIT 1;
```

LSU scored the most total points in 2019.

**single_domain** (tokens: 987)

```sql
SELECT T.team_name FROM teams T JOIN team_seasons TS ON T.team_id = TS.team_id JOIN offense O ON TS.team_season_id = O.team_season_id WHERE TS.season = 2019 ORDER BY O.total_points DESC LIMIT 1;
```

LSU scored the most total points in 2019.

**cross_domain** (tokens: 968)

```sql
SELECT T.team_name FROM teams T JOIN team_seasons TS ON T.team_id = TS.team_id JOIN offense O ON TS.team_season_id = O.team_season_id WHERE TS.season = 2019 ORDER BY O.total_points DESC LIMIT 1;
```

LSU scored the most total points in 2019.

## How many wins did each SEC team have in 2021?

**zero_shot** (tokens: 975)

```sql
SELECT T.team_name, TS.wins FROM team_seasons TS JOIN teams T ON TS.team_id = T.team_id JOIN conferences C ON TS.conference_id = C.conference_id WHERE C.conference_name = 'SEC' AND TS.season = 2021;
```

In 2021, Georgia led the SEC with 14 wins, followed by Alabama with 13, Kentucky and Ole Miss with 10, Arkansas with 9, Texas A&M with 8, Mississippi State, South Carolina, and Tennessee with 7, Auburn, Florida, LSU, and Missouri with 6, and Vanderbilt with 2.

**single_domain** (tokens: 1135)

```sql
SELECT t.team_name, ts.wins FROM team_seasons ts JOIN teams t USING(team_id) JOIN conferences c USING(conference_id) WHERE c.conference_name = 'SEC' AND ts.season = 2021;
```

In 2021, Georgia led the SEC with 14 wins, followed by Alabama with 13, Kentucky and Ole Miss with 10, Arkansas with 9, Texas A&M with 8, Mississippi State, South Carolina, and Tennessee with 7, Auburn, Florida, LSU, and Missouri with 6, and Vanderbilt with 2.

**cross_domain** (tokens: 1128)

```sql
SELECT T.team_name, TS.wins FROM team_seasons TS JOIN teams T ON TS.team_id = T.team_id JOIN conferences C ON TS.conference_id = C.conference_id WHERE C.conference_name = 'SEC' AND TS.season = 2021;
```

In 2021, Georgia led the SEC with 14 wins, followed by Alabama with 13, Kentucky and Ole Miss with 10, Arkansas with 9, Texas A&M with 8, Mississippi State, South Carolina, and Tennessee with 7, Auburn, Florida, LSU, and Missouri with 6, and Vanderbilt with 2.

## Which team had the best turnover margin in 2022?

**zero_shot** (tokens: 818)

```sql
SELECT T.team_name FROM teams T JOIN team_seasons TS ON T.team_id = TS.team_id JOIN game_management GM ON TS.team_season_id = GM.team_season_id WHERE TS.season = 2022 ORDER BY GM.turnover_margin DESC LIMIT 1;
```

Southern California had the best turnover margin in 2022.

**single_domain** (tokens: 999)

```sql
SELECT t.team_name, gm.turnover_margin FROM game_management gm JOIN team_seasons ts USING(team_season_id) JOIN teams t USING(team_id) WHERE ts.season = 2022 ORDER BY gm.turnover_margin DESC LIMIT 1;
```

Southern California had the best turnover margin in 2022 with a margin of 22.

**cross_domain** (tokens: 971)

```sql
SELECT T.team_name FROM teams T JOIN team_seasons TS ON T.team_id = TS.team_id JOIN game_management GM ON TS.team_season_id = GM.team_season_id WHERE TS.season = 2022 ORDER BY GM.turnover_margin DESC LIMIT 1;
```

Southern California had the best turnover margin in 2022.

## What is Ohio St.'s win percentage in each season?

**zero_shot** (tokens: 1184)

```sql
SELECT T2.season, (T2.wins * 1.0 / T2.games) AS win_percentage FROM teams AS T1 JOIN team_seasons AS T2 ON T1.team_id = T2.team_id WHERE T1.team_name = 'Ohio St.';
```

Ohio State's win percentages were approximately 86% in 2013, 93% in 2014, 92% in 2015, 85% in 2016, 86% in 2017, 93% in 2018, 93% in 2019, 100% in 2020, and 85% in 2021, 2022, and 2023.

**single_domain** (tokens: 1346)

```sql
SELECT ts.season, (ts.wins * 1.0 / ts.games) AS win_percentage FROM team_seasons ts JOIN teams t USING(team_id) WHERE t.team_name = 'Ohio St.' ORDER BY ts.season;
```

Ohio State's win percentages were approximately 86% in 2013, 93% in 2014, 92% in 2015, 85% in 2016, 86% in 2017, 93% in 2018, 93% in 2019, 100% in 2020, and 85% in 2021, 2022, and 2023.

**cross_domain** (tokens: 1298)

```sql
SELECT ts.season, (ts.wins * 1.0 / ts.games) FROM team_seasons ts JOIN teams t ON ts.team_id = t.team_id WHERE t.team_name = 'Ohio St.';
```

Ohio State's win percentages from 2013 to 2023 are approximately 0.86, 0.93, 0.92, 0.85, 0.86, 0.93, 0.93, 1.0, 0.85, 0.85, and 0.85, respectively.

## Which conference averaged the most passing yards per team in 2023?

**zero_shot** (tokens: 851)

```sql
SELECT T3.conference_name FROM offense AS T1 JOIN team_seasons AS T2 ON T1.team_season_id = T2.team_season_id JOIN conferences AS T3 ON T2.conference_id = T3.conference_id WHERE T2.season = 2023 GROUP BY T3.conference_name ORDER BY AVG(T1.pass_yards) DESC LIMIT 1;
```

The Pac-12 conference averaged the most passing yards per team in 2023.

**single_domain** (tokens: 1030)

```sql
SELECT c.conference_name, AVG(o.pass_yards) AS avg_pass_yards FROM offense o JOIN team_seasons ts USING(team_season_id) JOIN conferences c USING(conference_id) WHERE ts.season = 2023 GROUP BY c.conference_name ORDER BY avg_pass_yards DESC LIMIT 1;
```

The Pac-12 conference averaged the most passing yards per team in 2023 with 3530.5 yards.

**cross_domain** (tokens: 990)

```sql
SELECT c.conference_name FROM conferences c JOIN team_seasons ts ON c.conference_id = ts.conference_id JOIN offense o ON ts.team_season_id = o.team_season_id WHERE ts.season = 2023 GROUP BY c.conference_id ORDER BY AVG(o.pass_yards) DESC LIMIT 1;
```

The Pac-12 conference averaged the most passing yards per team in 2023.

## Which team gave up the fewest points per game in 2018, and how many?

**zero_shot** (tokens: 893)

```sql
SELECT T.team_name, CAST(D.points_allowed AS REAL) / TS.games AS points_per_game_allowed FROM teams T JOIN team_seasons TS ON T.team_id = TS.team_id JOIN defense D ON TS.team_season_id = D.team_season_id WHERE TS.season = 2018 ORDER BY points_per_game_allowed ASC LIMIT 1;
```

Clemson gave up the fewest points per game in 2018 with an average of 13.13 points.

**single_domain** (tokens: 1050)

```sql
SELECT t.team_name, CAST(d.points_allowed AS REAL) / ts.games AS points_allowed_per_game FROM defense d JOIN team_seasons ts USING(team_season_id) JOIN teams t USING(team_id) WHERE ts.season = 2018 ORDER BY points_allowed_per_game ASC LIMIT 1;
```

Clemson gave up the fewest points per game in 2018 with an average of 13.13.

**cross_domain** (tokens: 1039)

```sql
SELECT T.team_name, CAST(D.points_allowed AS REAL) / TS.games AS points_per_game FROM teams T JOIN team_seasons TS ON T.team_id = TS.team_id JOIN defense D ON TS.team_season_id = D.team_season_id WHERE TS.season = 2018 ORDER BY points_per_game ASC LIMIT 1;
```

Clemson gave up the fewest points per game in 2018 with an average of 13.13.

## Which teams had a losing record but a positive turnover margin in 2020?

**zero_shot** (tokens: 924)

```sql
SELECT T.team_name FROM teams T JOIN team_seasons TS ON T.team_id = TS.team_id JOIN game_management GM ON TS.team_season_id = GM.team_season_id WHERE TS.season = 2020 AND TS.losses > TS.wins AND GM.turnover_margin > 0;
```

The teams that had a losing record but a positive turnover margin in 2020 were Arkansas, Baylor, Charlotte, Colorado St., Illinois, Kentucky, New Mexico, Purdue, Rice, Rutgers, Syracuse, Virginia Tech, and Wyoming.

**single_domain** (tokens: 1082)

```sql
SELECT t.team_name FROM team_seasons ts JOIN teams t USING(team_id) JOIN game_management gm USING(team_season_id) WHERE ts.season = 2020 AND ts.losses > ts.wins AND gm.turnover_margin > 0;
```

The teams that had a losing record but a positive turnover margin in 2020 were Arkansas, Baylor, Charlotte, Colorado St., Illinois, Kentucky, New Mexico, Purdue, Rice, Rutgers, Syracuse, Virginia Tech, and Wyoming.

**cross_domain** (tokens: 1077)

```sql
SELECT T.team_name FROM teams T JOIN team_seasons TS ON T.team_id = TS.team_id JOIN game_management GM ON TS.team_season_id = GM.team_season_id WHERE TS.season = 2020 AND TS.losses > TS.wins AND GM.turnover_margin > 0;
```

The teams that had a losing record but a positive turnover margin in 2020 were Arkansas, Baylor, Charlotte, Colorado St., Illinois, Kentucky, New Mexico, Purdue, Rice, Rutgers, Syracuse, Virginia Tech, and Wyoming.

## Who was the best team ever?

**zero_shot** (tokens: 799)

```sql
SELECT T.team_name, TS.season FROM teams T JOIN team_seasons TS ON T.team_id = TS.team_id ORDER BY (TS.wins * 1.0 / TS.games) DESC, TS.wins DESC LIMIT 1;
```

The best team ever was Clemson in the 2018 season.

**single_domain** (tokens: 965)

```sql
SELECT t.team_name, ts.season FROM team_seasons ts JOIN teams t USING(team_id) ORDER BY (ts.wins * 1.0 / ts.games) DESC, ts.wins DESC LIMIT 1;
```

The best team ever was Clemson in the 2018 season.

**cross_domain** (tokens: 952)

```sql
SELECT T.team_name, TS.season FROM teams T JOIN team_seasons TS ON T.team_id = TS.team_id ORDER BY (TS.wins * 1.0 / TS.games) DESC, TS.wins DESC LIMIT 1;
```

The best team ever was Clemson in the 2018 season.
