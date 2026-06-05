
import matplotlib
matplotlib.use("TkAgg")   # change to "Agg" on headless servers
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator
from collections import Counter, defaultdict
import numpy as np
import urllib.request, json, sys, time

FLASK_URL    = "http://127.0.0.1:5000/all_cached"
REFRESH_SECS = 30   # auto-refresh interval when running in live mode

# ── Fetch data from Flask ─────────────────────────────────────────────────────
def fetch_data(retries=5) -> dict:
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(FLASK_URL, timeout=4) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if attempt < retries - 1:
                print(f"  Waiting for Flask… ({attempt+1}/{retries}) — {e}")
                time.sleep(2)
            else:
                print(f"\n❌  Cannot reach {FLASK_URL}")
                print("   Make sure app.py is running first.\n")
                sys.exit(1)


# ── Compute analytics ─────────────────────────────────────────────────────────
def compute(db: dict):
    cat_counts   = Counter()
    med_counts   = {}
    se_freq      = Counter()
    prec_counts  = []
    cat_med_tot  = defaultdict(int)

    for name, info in db.items():
        cat  = info.get("cat", "other")
        meds = info.get("meds", [])
        prec = info.get("prec", [])

        cat_counts[cat]  += 1
        med_counts[name]  = len(meds)
        prec_counts.append(len(prec))
        cat_med_tot[cat] += len(meds)

        for med in meds:
            if len(med) >= 3:
                se = med[2].split("(")[0].strip()
                se_freq[se] += 1

    return cat_counts, med_counts, se_freq, prec_counts, cat_med_tot


# ── Build dashboard ───────────────────────────────────────────────────────────
def build_dashboard(db: dict):
    if not db:
        print("⚠️  No diseases cached yet — search some diseases in MedBot first, then re-run graphs.py")
        sys.exit(0)

    cat_counts, med_counts, se_freq, prec_counts, cat_med_tot = compute(db)

    # ── Theme ─────────────────────────────────────────────────────────────────
    BG, CARD    = "#080c14", "#0f1623"
    ACCENT      = "#00e5c3"
    ACCENT2     = "#ff5f7e"
    ACCENT3     = "#ffc857"
    TEXT        = "#e8f0f8"
    MUTED       = "#5a7090"
    PALETTE     = ["#00e5c3","#ff5f7e","#ffc857","#a78bfa","#38bdf8",
                   "#fb923c","#4ade80","#f472b6","#facc15","#22d3ee",
                   "#818cf8","#34d399","#e879f9","#f87171","#60a5fa"]

    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": CARD,
        "axes.edgecolor": MUTED, "axes.labelcolor": TEXT,
        "xtick.color": MUTED, "ytick.color": MUTED, "text.color": TEXT,
        "grid.color": "#1e2a3a", "grid.linestyle": "--", "grid.alpha": 0.6,
        "font.family": "DejaVu Sans", "font.size": 10,
    })

    fig = plt.figure(figsize=(19, 13), facecolor=BG)
    fig.suptitle("MedBot Global — Live Analytics Dashboard",
                 fontsize=21, fontweight="bold", color=TEXT, y=0.98)

    gs = gridspec.GridSpec(2, 3, figure=fig,
                           hspace=0.50, wspace=0.38,
                           top=0.93, bottom=0.07, left=0.06, right=0.97)

    # ── Panel 1 · Category donut ──────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    labels = [c.capitalize() for c in cat_counts]
    sizes  = list(cat_counts.values())
    colors = PALETTE[:len(labels)]
    wedges, _, autotexts = ax1.pie(
        sizes, colors=colors, autopct="%1.0f%%", pctdistance=0.78,
        startangle=140, wedgeprops={"width": 0.52, "edgecolor": BG, "linewidth": 2},
    )
    for at in autotexts:
        at.set_fontsize(7.5); at.set_color(BG); at.set_fontweight("bold")
    ax1.legend(
        handles=[mpatches.Patch(color=c, label=l) for c, l in zip(colors, labels)],
        loc="lower center", bbox_to_anchor=(0.5, -0.42),
        ncol=2, fontsize=7.5, frameon=False, labelcolor=TEXT,
    )
    ax1.text(0, 0, f"{sum(sizes)}\nDiseases", ha="center", va="center",
             fontsize=12, fontweight="bold", color=TEXT)
    ax1.set_title("Disease Categories", color=TEXT, fontweight="bold", pad=12, fontsize=13)

    # ── Panel 2 · Medications per disease ────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    top15 = sorted(med_counts.items(), key=lambda x: x[1], reverse=True)[:15]
    names  = [n.title()[:24] for n, _ in top15]
    counts = [c for _, c in top15]
    bcolors = [PALETTE[i % len(PALETTE)] for i in range(len(names))]
    bars = ax2.barh(names, counts, color=bcolors, height=0.65, edgecolor=BG, linewidth=0.7)
    ax2.invert_yaxis()
    ax2.set_xlabel("No. of Medications", color=MUTED, fontsize=9)
    ax2.set_title("Medications per Disease (Top 15)", color=TEXT, fontweight="bold", pad=10, fontsize=13)
    ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax2.grid(axis="x"); ax2.tick_params(labelsize=8)
    for bar, cnt in zip(bars, counts):
        ax2.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                 str(cnt), va="center", ha="left", fontsize=8, color=TEXT)

    # ── Panel 3 · Top side-effects lollipop ──────────────────────────────────
    ax3 = fig.add_subplot(gs[0, 2])
    top_se    = se_freq.most_common(14)
    se_labels = [s for s, _ in top_se][::-1]
    se_vals   = [v for _, v in top_se][::-1]
    y_pos = np.arange(len(se_labels))
    ax3.hlines(y_pos, 0, se_vals, color=MUTED, linewidth=1.5, alpha=0.5)
    ax3.scatter(se_vals, y_pos, s=64, color=ACCENT2, zorder=5)
    ax3.set_yticks(y_pos); ax3.set_yticklabels(se_labels, fontsize=8)
    ax3.set_xlabel("Frequency across DB", color=MUTED, fontsize=9)
    ax3.set_title("Most Frequent Side Effects", color=TEXT, fontweight="bold", pad=10, fontsize=13)
    ax3.grid(axis="x"); ax3.tick_params(axis="y", length=0)

    # ── Panel 4 · Avg meds per category ──────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 0])
    cats    = list(cat_counts.keys())
    avg     = [cat_med_tot[c] / cat_counts[c] for c in cats]
    pairs   = sorted(zip(cats, avg), key=lambda x: x[1], reverse=True)
    sc, sa  = zip(*pairs) if pairs else ([], [])
    ax4.bar([c.capitalize()[:11] for c in sc], sa,
            color=[PALETTE[i % len(PALETTE)] for i in range(len(sc))],
            edgecolor=BG, linewidth=0.7)
    ax4.set_ylabel("Avg Medications", color=MUTED, fontsize=9)
    ax4.set_title("Avg Meds per Category", color=TEXT, fontweight="bold", pad=10, fontsize=13)
    ax4.tick_params(axis="x", rotation=38, labelsize=8)
    ax4.grid(axis="y")

    # ── Panel 5 · Precaution violin ───────────────────────────────────────────
    ax5 = fig.add_subplot(gs[1, 1])
    cat_prec = defaultdict(list)
    for name, info in db.items():
        cat_prec[info.get("cat","other")].append(len(info.get("prec", [])))
    c_keys  = sorted(cat_prec.keys())
    c_data  = [cat_prec[k] for k in c_keys]
    c_labels= [k.capitalize()[:10] for k in c_keys]

    if len(c_keys) >= 2:
        parts = ax5.violinplot(c_data, showmedians=True, showextrema=False)
        for i, pc in enumerate(parts["bodies"]):
            pc.set_facecolor(PALETTE[i % len(PALETTE)]); pc.set_alpha(0.72); pc.set_edgecolor(BG)
        parts["cmedians"].set_color(TEXT); parts["cmedians"].set_linewidth(1.5)
        ax5.set_xticks(range(1, len(c_labels)+1))
        ax5.set_xticklabels(c_labels, rotation=38, fontsize=8)
    else:
        ax5.text(0.5, 0.5, "Search more diseases\nto see distribution",
                 ha="center", va="center", color=MUTED, fontsize=11, transform=ax5.transAxes)

    ax5.set_ylabel("Precautions per Disease", color=MUTED, fontsize=9)
    ax5.set_title("Precaution Count by Category", color=TEXT, fontweight="bold", pad=10, fontsize=13)
    ax5.grid(axis="y")

    # ── Panel 6 · KPI summary tiles ───────────────────────────────────────────
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.set_xlim(0, 1); ax6.set_ylim(0, 1); ax6.axis("off")
    ax6.set_title("Session Summary", color=TEXT, fontweight="bold", pad=10, fontsize=13)

    total_d   = len(db)
    total_m   = sum(med_counts.values())
    unique_se = len(se_freq)
    total_p   = sum(prec_counts)
    n_cats    = len(cat_counts)
    avg_m     = total_m / total_d if total_d else 0

    kpis = [
        ("🦠", "Diseases Searched", str(total_d),          ACCENT),
        ("💊", "Total Medications",  str(total_m),          ACCENT3),
        ("⚠️",  "Side-effect Types",  str(unique_se),        ACCENT2),
        ("📋", "Total Precautions",  str(total_p),          "#a78bfa"),
        ("🏥", "Categories",         str(n_cats),           "#38bdf8"),
        ("📊", "Avg Meds/Disease",   f"{avg_m:.1f}",        "#4ade80"),
    ]

    for idx, (icon, label, val, col) in enumerate(kpis):
        row = idx // 2
        cx  = (idx % 2) * 0.5
        yb  = 0.88 - row * 0.30
        rect = mpatches.FancyBboxPatch(
            (cx + 0.03, yb - 0.20), 0.43, 0.24,
            boxstyle="round,pad=0.02", linewidth=1.2,
            edgecolor=col, facecolor="#0f1623", transform=ax6.transAxes,
        )
        ax6.add_patch(rect)
        ax6.text(cx + 0.25, yb + 0.01, val,
                 ha="center", va="center", fontsize=19, fontweight="bold",
                 color=col, transform=ax6.transAxes)
        ax6.text(cx + 0.25, yb - 0.12, label,
                 ha="center", va="center", fontsize=8, color=MUTED,
                 transform=ax6.transAxes)

    plt.savefig("medbot_dashboard.png", dpi=150, bbox_inches="tight", facecolor=BG)
    print("✅  Dashboard saved → medbot_dashboard.png")
    plt.show()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    live_mode = "--live" in sys.argv   # python graphs.py --live  → auto-refresh

    if live_mode:
        print("📊  Live mode — refreshing every", REFRESH_SECS, "seconds. Ctrl+C to stop.")
        try:
            while True:
                db = fetch_data()
                print(f"  Loaded {len(db)} diseases from session cache.")
                build_dashboard(db)
                time.sleep(REFRESH_SECS)
        except KeyboardInterrupt:
            print("\n👋  Stopped.")
    else:
        print("📊  Fetching live data from MedBot session…")
        db = fetch_data()
        print(f"  ✓  {len(db)} disease(s) found in session cache.")
        build_dashboard(db)