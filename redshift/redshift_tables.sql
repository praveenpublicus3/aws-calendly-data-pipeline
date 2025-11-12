CREATE TABLE IF NOT EXISTS landing (
    event VARCHAR(100),
    invitee_email VARCHAR(255),
    invitee_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS spend (
    event_type VARCHAR(100),
    total_spend DECIMAL(10,2)
);
