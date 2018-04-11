CREATE TABLE IF NOT EXISTS flags (
    flag TEXT PRIMARY KEY,
    sploit TEXT,
    team TEXT,
    time INTEGER,
    status TEXT,
    checksystem_response TEXT
);

CREATE INDEX IF NOT EXISTS flags_sploit ON flags(sploit);
CREATE INDEX IF NOT EXISTS flags_team ON flags(team);
CREATE INDEX IF NOT EXISTS flags_status_time ON flags(status, time);
CREATE INDEX IF NOT EXISTS flags_time ON flags(time);
