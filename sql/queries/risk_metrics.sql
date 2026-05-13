-- Annualized volatility (std dev) per sector
SELECT
    sector,
    ROUND(STDEV(daily_return) * SQRT(252), 4) AS annualized_volatility,
    ROUND(AVG(daily_return) * 252, 4)         AS annualized_return,
    COUNT(*)                                   AS trading_days
FROM sector_returns
GROUP BY sector
ORDER BY annualized_volatility;
