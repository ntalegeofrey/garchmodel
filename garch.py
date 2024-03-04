import ccxt
import pandas as pd
from arch import arch_model
import numpy as np
import matplotlib.pyplot as plt

# Fetch historical OHLCV data from Binance
exchange = ccxt.binance()
ohlcv = exchange.fetch_ohlcv('ETH/USDT', '4h')
df = pd.DataFrame(
    ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Calculate returns
df['returns'] = df['close'].pct_change()


# Replace infinite values with NaN
df.replace([np.inf, -np.inf], np.nan, inplace=True)

# Remove rows with missing values
df.dropna(inplace=True)

# Fit GARCH(1,1) model
am = arch_model(df['returns'], vol='GARCH', p=1, o=0, q=1, dist='Normal')
res = am.fit(disp='off')

# Simulate buy and sell signals based on predicted volatility
df['signal'] = 0
df.loc[res.conditional_volatility.mean() > res.conditional_volatility,
       'signal'] = 1
df.loc[res.conditional_volatility.mean() < res.conditional_volatility,
       'signal'] = -1

# Plot buy signals
buys = df[df['signal'] == 1]
plt.scatter(buys.index, buys['close'], c='green', marker='^')

# Plot sell signals
sells = df[df['signal'] == -1]
plt.scatter(sells.index, sells['close'], c='red', marker='v')

# Plot close price
plt.plot(df.index, df['close'], label='Price')
plt.legend()
plt.show()
