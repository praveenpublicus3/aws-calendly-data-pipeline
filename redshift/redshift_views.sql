CREATE OR REPLACE VIEW vw_daily_calls AS
SELECT
    CURRENT_DATE AS booking_date,
    event AS source,
    COUNT(invitee_email) AS total_bookings
FROM landing
WHERE invitee_email IS NOT NULL
GROUP BY event, CURRENT_DATE;

CREATE OR REPLACE VIEW vw_cost_per_booking AS
SELECT
    l.event AS event_type,
    COUNT(l.invitee_email) AS total_invitees,
    COALESCE(s.total_spend, 0) AS total_spend,
    CASE WHEN COUNT(l.invitee_email)=0 THEN 0
         ELSE COALESCE(s.total_spend, 0) / COUNT(l.invitee_email)
    END AS cost_per_booking
FROM landing l
LEFT JOIN spend s ON l.event = s.event_type
GROUP BY l.event, s.total_spend;
