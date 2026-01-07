import pandas as pd
import numpy as np
import random
from collections import Counter

BAN_LIST = ['rafal', 'grzeslaw', 'lokator', 'staska', 'ewa', 'renata']

df = pd.read_excel("spread.xlsx", header=None)
headers = df.iloc[0]
df = df.iloc[1:]
df.columns = headers
df = df.loc[:, df.columns.notna()]
df = df.dropna(axis=0, how='all')

trafione_col_df = df.get("trafione")
trafione_col_df = trafione_col_df[~df["trafione"].isin(BAN_LIST)]
df = df.drop(columns=["trafione", *BAN_LIST], axis=1)


def calculate_weights(df, trafione_col):
    weights = {}

    # base weight = number of themes the user has
    for name, themes in df.items():
        weights[name] = len(themes.dropna())

    # apply recency penalties
    recent_picks = trafione_col.dropna().tolist()
    b=0.85 # base penalty
    h=1 # half-life

    for i, name in enumerate(reversed(recent_picks), start=1):
        penalty = b ** (i / h)
        weights[name] *= (1 - penalty)
        print(f"osoba {name} z {100*penalty:.2f}% penalty")

    return weights


def select_winner(weights, df):
    names = list(weights.keys())
    w = np.array([weights[n] for n in names], dtype=float)
    w = w / w.sum()

    winner = np.random.choice(names, p=w)
    theme = random.choice(df[winner].dropna().tolist())
    return (theme, winner)


N = 100_000  

weights = calculate_weights(df, trafione_col_df)

results = Counter(select_winner(weights, df) for _ in range(N))

print("\nRESULTS PER THEME")
print("-----------------")
for (theme, person), count in results.most_common():
    print(f"{person:12s} | {theme:30s} -> {count}")



user_counts = Counter(person for (_, person) in results.elements())

print("\nUSER PICK PROBABILITIES")
print("-----------------------")
for user, count in user_counts.most_common():
    pct = 100 * count / N
    print(f"{user:12s} -> {count:5d} picks  ({pct:6.2f}%)")
