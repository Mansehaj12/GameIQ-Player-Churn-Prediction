# ============================================================
# GameIQ - Dataset Handling + Exploratory Data Analysis
# ============================================================
# This script:
#   1. Loads the Cookie Cats A/B testing dataset
#   2. Explores the data (head, info, describe)
#   3. Handles missing values
#   4. Creates a 'churn' column
#   5. Performs full EDA with visualizations
# ============================================================

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend (saves to file)
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ────────────────────────────────────────────────────────────
# STEP 2: DATASET HANDLING
# ────────────────────────────────────────────────────────────

# Load the dataset
# The Cookie Cats dataset comes from an A/B test in the mobile game "Cookie Cats".
# The game tested moving a gate (forced wait) from level 30 to level 40.
data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cookie_cats.csv')
df = pd.read_csv(data_path)

print("=" * 60)
print("📊 STEP 2: DATASET EXPLORATION")
print("=" * 60)

# --- 2.1 Show first few rows ---
print("\n🔹 First 5 rows of the dataset:")
print(df.head())

# --- 2.2 Dataset shape ---
print(f"\n🔹 Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")

# --- 2.3 Column info ---
print("\n🔹 Dataset Info:")
print(df.info())

# --- 2.4 Statistical summary ---
print("\n🔹 Statistical Summary:")
print(df.describe())

# --- 2.5 Column Explanations ---
print("\n" + "=" * 60)
print("📖 COLUMN EXPLANATIONS")
print("=" * 60)
print("""
┌──────────────────┬──────────────────────────────────────────────────────┐
│ Column           │ Meaning                                              │
├──────────────────┼──────────────────────────────────────────────────────┤
│ userid           │ Unique player identifier                             │
│ version          │ A/B test group: gate_30 (control) or gate_40 (test)  │
│ sum_gamerounds   │ Total game rounds played in the first 14 days        │
│ retention_1      │ Did the player come back 1 day after install? (T/F)  │
│ retention_7      │ Did the player come back 7 days after install? (T/F) │
└──────────────────┴──────────────────────────────────────────────────────┘
""")

# --- 2.6 Check for missing values ---
print("🔹 Missing Values:")
missing = df.isnull().sum()
print(missing)

if missing.sum() == 0:
    print("✅ No missing values found! Dataset is clean.")
else:
    print("⚠️ Handling missing values...")
    df.dropna(inplace=True)
    print(f"   Rows after cleanup: {df.shape[0]}")

# --- 2.7 Create the CHURN column ---
# WHY CHURN MATTERS:
#   In the gaming business, "churn" means a player has stopped playing.
#   If retention_7 == False → the player didn't return after 7 days → they CHURNED.
#   Predicting churn helps companies:
#     • Identify at-risk players early
#     • Send targeted offers/notifications
#     • Improve game design to keep players engaged
#     • Reduce revenue loss from losing paying customers

df['churn'] = (df['retention_7'] == False).astype(int)
# churn = 1 → player left (bad)
# churn = 0 → player stayed (good)

print("\n🔹 Churn column created!")
print(f"   Churned players:  {df['churn'].sum()} ({df['churn'].mean()*100:.1f}%)")
print(f"   Retained players: {(df['churn'] == 0).sum()} ({(1 - df['churn'].mean())*100:.1f}%)")

print("\n🔹 Updated dataset preview:")
print(df.head(10))


# ────────────────────────────────────────────────────────────
# STEP 3: EXPLORATORY DATA ANALYSIS (EDA)
# ────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("📈 STEP 3: EXPLORATORY DATA ANALYSIS")
print("=" * 60)

# Create output directory for charts
charts_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'charts')
os.makedirs(charts_dir, exist_ok=True)

# Set a clean visual style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12

# --- 3.1 Retention Rates ---
retention_1_rate = df['retention_1'].mean() * 100
retention_7_rate = df['retention_7'].mean() * 100
churn_rate = df['churn'].mean() * 100

print(f"\n🔹 Day 1 Retention Rate: {retention_1_rate:.2f}%")
print(f"   → {retention_1_rate:.0f}% of players returned the day after installing.")
print(f"\n🔹 Day 7 Retention Rate: {retention_7_rate:.2f}%")
print(f"   → Only {retention_7_rate:.0f}% of players were still active after a week.")
print(f"\n🔹 Overall Churn Rate:   {churn_rate:.2f}%")
print(f"   → {churn_rate:.0f}% of players stopped playing within 7 days.")

# --- 3.2 A/B Testing Comparison ---
print("\n" + "-" * 50)
print("🔬 A/B TEST: gate_30 vs gate_40")
print("-" * 50)

ab_retention = df.groupby('version').agg(
    day1_retention=('retention_1', 'mean'),
    day7_retention=('retention_7', 'mean'),
    churn_rate=('churn', 'mean'),
    avg_rounds=('sum_gamerounds', 'mean'),
    player_count=('userid', 'count')
).round(4)

print(ab_retention)

gate30 = df[df['version'] == 'gate_30']
gate40 = df[df['version'] == 'gate_40']

print(f"\n   📌 gate_30 (control) - Gate at level 30:")
print(f"      Day 1 Retention: {gate30['retention_1'].mean()*100:.2f}%")
print(f"      Day 7 Retention: {gate30['retention_7'].mean()*100:.2f}%")
print(f"      Churn Rate:      {gate30['churn'].mean()*100:.2f}%")

print(f"\n   📌 gate_40 (test) - Gate at level 40:")
print(f"      Day 1 Retention: {gate40['retention_1'].mean()*100:.2f}%")
print(f"      Day 7 Retention: {gate40['retention_7'].mean()*100:.2f}%")
print(f"      Churn Rate:      {gate40['churn'].mean()*100:.2f}%")

# --- 3.3 Engagement Analysis ---
print("\n" + "-" * 50)
print("🎮 ENGAGEMENT ANALYSIS (sum_gamerounds)")
print("-" * 50)

churned = df[df['churn'] == 1]['sum_gamerounds']
retained = df[df['churn'] == 0]['sum_gamerounds']

print(f"\n   Churned players   → Avg rounds: {churned.mean():.1f}, Median: {churned.median():.0f}")
print(f"   Retained players  → Avg rounds: {retained.mean():.1f}, Median: {retained.median():.0f}")

# --- 3.4 VISUALIZATIONS ---
print("\n" + "-" * 50)
print("📊 Generating visualizations...")
print("-" * 50)

# ── Chart 1: Retention Rates by A/B Group ──
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Day 1 Retention
versions = ['gate_30', 'gate_40']
day1_vals = [gate30['retention_1'].mean() * 100, gate40['retention_1'].mean() * 100]
day7_vals = [gate30['retention_7'].mean() * 100, gate40['retention_7'].mean() * 100]

colors = ['#4C72B0', '#DD8452']

axes[0].bar(versions, day1_vals, color=colors, edgecolor='white', linewidth=1.5)
axes[0].set_title('Day 1 Retention by Version', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Retention Rate (%)')
axes[0].set_ylim(0, 100)
for i, v in enumerate(day1_vals):
    axes[0].text(i, v + 1.5, f'{v:.2f}%', ha='center', fontweight='bold', fontsize=12)

axes[1].bar(versions, day7_vals, color=colors, edgecolor='white', linewidth=1.5)
axes[1].set_title('Day 7 Retention by Version', fontsize=14, fontweight='bold')
axes[1].set_ylabel('Retention Rate (%)')
axes[1].set_ylim(0, 100)
for i, v in enumerate(day7_vals):
    axes[1].text(i, v + 1.5, f'{v:.2f}%', ha='center', fontweight='bold', fontsize=12)

plt.suptitle('🔬 A/B Test: Retention Comparison', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(charts_dir, 'retention_by_version.png'), dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: retention_by_version.png")

# ── Chart 2: Churn Distribution (Pie Chart) ──
fig, ax = plt.subplots(figsize=(8, 8))
churn_counts = df['churn'].value_counts()
labels = ['Retained (Stayed)', 'Churned (Left)']
colors_pie = ['#2ecc71', '#e74c3c']
explode = (0, 0.05)

ax.pie(churn_counts, labels=labels, colors=colors_pie, autopct='%1.1f%%',
       startangle=90, explode=explode, shadow=True, textprops={'fontsize': 14})
ax.set_title('Overall Player Churn Distribution', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(charts_dir, 'churn_distribution.png'), dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: churn_distribution.png")

# ── Chart 3: Engagement vs Churn (Histogram) ──
fig, ax = plt.subplots(figsize=(12, 6))

# Cap at 500 rounds for better visualization (most data is below this)
max_rounds = 500
df_capped = df[df['sum_gamerounds'] <= max_rounds]

ax.hist(df_capped[df_capped['churn'] == 0]['sum_gamerounds'],
        bins=50, alpha=0.6, label='Retained', color='#2ecc71', edgecolor='white')
ax.hist(df_capped[df_capped['churn'] == 1]['sum_gamerounds'],
        bins=50, alpha=0.6, label='Churned', color='#e74c3c', edgecolor='white')

ax.set_title('Engagement Distribution: Churned vs Retained Players', fontsize=14, fontweight='bold')
ax.set_xlabel('Total Game Rounds (first 14 days)')
ax.set_ylabel('Number of Players')
ax.legend(fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(charts_dir, 'engagement_vs_churn.png'), dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: engagement_vs_churn.png")

# ── Chart 4: Churn Rate by Engagement Buckets ──
fig, ax = plt.subplots(figsize=(12, 6))

bins = [0, 1, 10, 50, 100, 250, 500, float('inf')]
labels_bucket = ['0', '1-10', '11-50', '51-100', '101-250', '251-500', '500+']
df['engagement_bucket'] = pd.cut(df['sum_gamerounds'], bins=bins, labels=labels_bucket, right=True)

bucket_churn = df.groupby('engagement_bucket', observed=False)['churn'].mean() * 100

bars = ax.bar(bucket_churn.index, bucket_churn.values, color='#e74c3c', edgecolor='white', linewidth=1.5)
ax.set_title('Churn Rate by Engagement Level', fontsize=14, fontweight='bold')
ax.set_xlabel('Game Rounds Played (Buckets)')
ax.set_ylabel('Churn Rate (%)')

for bar, val in zip(bars, bucket_churn.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{val:.1f}%', ha='center', fontweight='bold', fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(charts_dir, 'churn_by_engagement.png'), dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: churn_by_engagement.png")

# Clean up temporary column
df.drop('engagement_bucket', axis=1, inplace=True)

# ────────────────────────────────────────────────────────────
# PRODUCT ANALYST INSIGHTS
# ────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("💡 PRODUCT ANALYST INSIGHTS")
print("=" * 60)

print("""
🔍 KEY FINDINGS:

1. 📉 HIGH CHURN RATE
   → ~{:.0f}% of players leave within 7 days. This is common in mobile
     games but still represents a massive revenue opportunity.

2. 🚪 GATE PLACEMENT MATTERS
   → gate_30 shows slightly better Day 7 retention than gate_40.
   → Moving the gate further delays the "frustration point" but may
     not improve engagement. The earlier gate may actually help by
     creating a healthy play/rest rhythm.

3. 🎮 ENGAGEMENT IS THE #1 PREDICTOR
   → Players who play very few rounds (0-10) churn at extremely high
     rates. Engagement in the first few days is critical.
   → The "aha moment" likely happens after ~50+ rounds.

4. 📊 DAY 1 RETENTION PREDICTS DAY 7
   → If a player doesn't return on Day 1, they almost certainly won't
     return on Day 7. The first session experience is crucial.

5. 🎯 ACTIONABLE INSIGHT
   → Focus on the FIRST SESSION. If you can get a player past 10 rounds
     on day 1, their chance of long-term retention increases dramatically.
""".format(churn_rate))

print("=" * 60)
print("✅ STEP 2 & 3 COMPLETE!")
print(f"   Charts saved to: {os.path.abspath(charts_dir)}")
print("=" * 60)
