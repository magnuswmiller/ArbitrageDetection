import numpy as np
from scipy.optimize import linprog

# Example input data
# Modify these lists to reflect the actual data you extracted
strikes = [1000, 2000, 3000, 4000, 5000, 6000]  # Strike prices
call_bids = [3420.5, 2420.3, 1439.8, 482.9, 1.5, 0]  # Bid prices for calls
call_asks = [3432.6, 2432.4, 1430.4, 483.3, 1.65, 0.1]  # Ask prices for calls
put_bids = [0.15, 0.95, 7.2, 52.5, 564.9, 1562.4]  # Bid prices for puts
put_asks = [0.15, 1.1, 7.4, 52.9, 577, 1574.5]  # Ask prices for puts
spot_bid = 4440.1699  # Spot bid price for underlying asset
spot_ask = 4442.7798  # Spot ask price for underlying asset

# Number of variables: 2 for each option (long and short) + 2 for the underlying asset (long and short)
num_options = len(strikes) * 2  # 2 options (call, put) per strike
total_positions = num_options * 2 + 2  # Long and short for each option + long and short for underlying

# Objective function: Minimize cost of setting up arbitrage
c = np.zeros(total_positions)
c[0] = spot_ask  # Long position on underlying asset
c[1] = -spot_bid  # Short position on underlying asset

# Add ask prices for long positions and bid prices for short positions for calls and puts
for i in range(len(strikes)):
    c[2 + i] = call_asks[i]  # Long call
    c[2 + len(strikes) + i] = -call_bids[i]  # Short call
    c[2 + 2*len(strikes) + i] = put_asks[i]  # Long put
    c[2 + 3*len(strikes) + i] = -put_bids[i]  # Short put

# Constraints
# Each row corresponds to a possible price of the underlying at expiry
A = np.zeros((len(strikes) + 1, total_positions))
b = np.zeros(len(strikes) + 1)

# Payoff matrix for different strike prices at expiry
for i, strike in enumerate(strikes):
    # Underlying asset payoff
    A[i, 0] = 1  # Long underlying
    A[i, 1] = -1  # Short underlying

    # Call and put payoffs at each strike price
    for j, s in enumerate(strikes):
        A[i, 2 + j] = max(0, s - strike)  # Long call
        A[i, 2 + len(strikes) + j] = -max(0, s - strike)  # Short call
        A[i, 2 + 2*len(strikes) + j] = max(0, strike - s)  # Long put
        A[i, 2 + 3*len(strikes) + j] = -max(0, strike - s)  # Short put

# Constraint at "infinity" - assume very high price
A[-1, 0] = 1  # Long underlying asset payoff approaches infinity
A[-1, 1] = -1  # Short underlying asset payoff approaches negative infinity

# All calls are in-the-money at infinity
A[-1, 2:2+len(strikes)] = 1  # Long calls
A[-1, 2+len(strikes):2+2*len(strikes)] = -1  # Short calls

# All puts are out-of-the-money at infinity
A[-1, 2+2*len(strikes):2+3*len(strikes)] = 0  # Long puts
A[-1, 2+3*len(strikes):] = 0  # Short puts

print("A: ", A)
print("b: ", b)
print("c: ", c)

# Solve linear program
result = linprog(c, A_ub=-A, b_ub=-b, method="highs")

# Output results
if result.success:
    print("No arbitrage opportunity detected.")
else:
    print("Arbitrage opportunity detected!")
    print("Suggested trades (positive = buy, negative = sell):")
    print(result.x)
    print("Expected profit:", result.fun)

