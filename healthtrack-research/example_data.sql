-- Example data for HealthTrack Research
-- Run this after initializing the database

-- Insert example supplements
INSERT INTO supplements (name, dosage, dosage_unit, frequency, user_notes, created_at, updated_at)
VALUES
    ('Vitamin D3', 5000, 'IU', 'daily', 'Taking for bone health and immune support', datetime('now'), datetime('now')),
    ('Omega-3 Fish Oil', 1000, 'mg', 'daily', 'EPA+DHA for cardiovascular health', datetime('now'), datetime('now')),
    ('Vitamin C', 1000, 'mg', 'daily', 'Immune support', datetime('now'), datetime('now')),
    ('Magnesium', 400, 'mg', 'daily', 'Sleep and muscle health', datetime('now'), datetime('now'));

-- Insert example intake logs (last 7 days)
INSERT INTO intake_log (supplement_id, date, taken, energy_level, sleep_quality, mood_level, notes, created_at)
VALUES
    -- Vitamin D3
    (1, date('now', '-6 days'), 1, 7, 8, 7, 'Felt good', datetime('now')),
    (1, date('now', '-5 days'), 1, 8, 7, 8, '', datetime('now')),
    (1, date('now', '-4 days'), 0, 6, 6, 6, 'Forgot to take', datetime('now')),
    (1, date('now', '-3 days'), 1, 7, 8, 7, '', datetime('now')),
    (1, date('now', '-2 days'), 1, 8, 8, 8, 'Great day', datetime('now')),
    (1, date('now', '-1 days'), 1, 7, 7, 7, '', datetime('now')),
    (1, date('now'), 1, 8, 8, 8, '', datetime('now')),

    -- Omega-3
    (2, date('now', '-6 days'), 1, 7, 8, 7, '', datetime('now')),
    (2, date('now', '-5 days'), 1, 8, 7, 8, '', datetime('now')),
    (2, date('now', '-4 days'), 1, 7, 7, 7, '', datetime('now')),
    (2, date('now', '-3 days'), 1, 7, 8, 7, '', datetime('now')),
    (2, date('now', '-2 days'), 1, 8, 8, 8, '', datetime('now')),
    (2, date('now', '-1 days'), 0, 6, 7, 6, 'Missed', datetime('now')),
    (2, date('now'), 1, 8, 8, 8, '', datetime('now'));

-- Note: Research cache will be populated automatically via PubMed API
-- Interactions will be added through the interaction checking feature
