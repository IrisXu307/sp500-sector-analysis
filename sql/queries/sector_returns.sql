-- Annual average return per sector
SELECT
    sector,
    strftime('%Y', date)            AS year,
    ROUND(AVG(daily_return) * 252, 4) AS annualized_return
FROM sector_returns
GROUP BY sector, year
ORDER BY year, annualized_return DESC;
