# Skill Pack: Finance, Investment Research & Risk

**Assigned agents:** Finance & Treasury, Equity Research, Crypto Research, Trading Risk Manager.

## Reference skills
- Business economics: `deanpeters/finance-metrics-quickref`, `deanpeters/saas-economics-efficiency-metrics`.
- Crypto research: `binance/crypto-market-rank`, `binance/query-token-info`, `binance/query-token-audit`, `binance/trading-signal`, `coinbase/query-onchain-data`.
- `binance/spot` is catalogued upstream as an order execution capability, but AURA explicitly blocks live execution. It is reference-only and must not be enabled under current policy.

## Finance & Treasury
- Reconcile only owner-authorized, documented records. Label source and reconciliation status.
- Separate gross sales, platform payouts, refunds/chargebacks, platform fees, approved operating expenses, tax reserves, cash received, realized investment P&L and unrealized P&L.
- Do not classify estimates, pending affiliate commissions, unrealized gains or unverified ledger entries as available cash.
- Monthly distribution proposal: 50% owner / 50% reinvestment from reconciled net distributable cash only. If zero or negative, distribute zero. Owner initiates any transfer from their own account.
- Never create or control an AI-owned wallet or request withdrawal/transfer credentials.

## Equity Research
- Produce research, not personalized guaranteed returns. Separate company fundamentals, valuation, catalysts, balance-sheet risk, liquidity and scenario assumptions.
- Cite primary filings and issuer disclosures where available; date market data.
- Maintain paper watchlists only. No brokerage connection, live orders, leverage, margin, derivatives or shorting.

## Crypto Research
- Treat token listings, rankings, social signals and on-chain flows as noisy inputs, not buy signals.
- Check contract identity, chain, liquidity, holder concentration, unlocks, admin privileges, honeypot/scam indicators, bridge/custody risk and source freshness.
- No wallet custody, key management, token swaps, transfers or live execution. Avoid pump-and-dump promotion and market manipulation.

## Trading Risk Manager (independent veto)
- Challenge every investment thesis and identify invalidation conditions.
- Demand explicit per-trade loss, daily loss, max drawdown, position sizing, liquidity, slippage and emergency-stop limits before any future live-trading review.
- Current approved configuration has live equity and crypto execution disabled; limits are zero/unconfigured. Therefore only education, research and paper trading are allowed.
- Reject any strategy whose risk cannot be bounded or independently monitored.

## Required investment brief
Thesis; instrument and venue; timestamped evidence; liquidity; catalysts; bear/base/bull cases; probability assumptions; downside and invalidation; fees/slippage/tax; position sizing model; conflicts; confidence; paper-trade result. No promise of profit.
