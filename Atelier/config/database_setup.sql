-- Matches table
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    match_id BIGINT UNIQUE NOT NULL,
    competition VARCHAR(255),
    joueur1 VARCHAR(255),
    joueur2 VARCHAR(255),
    start_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Ace markets table
CREATE TABLE IF NOT EXISTS ace_markets (
    id SERIAL PRIMARY KEY,
    match_id BIGINT REFERENCES matches(match_id),
    market_type VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(match_id, market_type)
);

-- Odds history table
CREATE TABLE IF NOT EXISTS odds_history (
    id SERIAL PRIMARY KEY,
    ace_market_id INTEGER REFERENCES ace_markets(id),
    selection_name VARCHAR(255) NOT NULL,
    odds DECIMAL(10, 2) NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_matches_match_id ON matches(match_id);
CREATE INDEX IF NOT EXISTS idx_ace_markets_match_id ON ace_markets(match_id);
CREATE INDEX IF NOT EXISTS idx_odds_history_ace_market_id ON odds_history(ace_market_id);
CREATE INDEX IF NOT EXISTS idx_odds_history_recorded_at ON odds_history(recorded_at);