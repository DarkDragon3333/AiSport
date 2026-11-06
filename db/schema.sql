create table competitions (
    competition_id integer primary key,
    competition_name text not null,
    country_name text not null
);

create table seasons (
    season_id integer primary key,
    season_name text not null
);

create table teams (
    team_id integer primary key,
    team_name text not null
);

create table players (
    player_id integer primary key,
    player_name text not null,
    player_nickname text,
    country_name text
);

create table matches (
    match_id integer primary key,
    competition_id integer not null references competitions,
    season_id integer not null references seasons,
    match_date date not null,
    kick_off time,
    match_week smallint,
    competition_stage text,
    home_team_id integer not null references teams,
    away_team_id integer not null references teams,
    home_score smallint not null,
    away_score smallint not null,
    stadium_name text,
    referee_name text
);

create table goals (
    goal_id uuid primary key,
    match_id integer not null references matches,
    player_id integer not null references players,
    team_id integer not null references teams,
    period smallint not null,
    minute smallint not null,
    second smallint not null,
    goal_type text not null,
    body_part text,
    is_own_goal boolean not null default false
);

create index on goals (player_id);
create index on goals (match_id);
create index on matches (season_id);
create index on matches (home_team_id);
create index on matches (away_team_id);