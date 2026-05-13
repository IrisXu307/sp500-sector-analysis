-- Rolling 30-day average return per sector using window functions
SELECT
    date,
    sector,
    daily_return,
    AVG(daily_return) OVER (
        PARTITION BY sector
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_30d_avg,
    LAG(daily_return, 1) OVER (PARTITION BY sector ORDER BY date) AS prev_day_return,
    RANK() OVER (PARTITION BY date ORDER BY daily_return DESC)    AS daily_rank
FROM sector_returns
ORDER BY date, sector;
