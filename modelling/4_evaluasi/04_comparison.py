"""
================================================================================
SKRIPSI - KOMPARASI 4 MODEL (RF S1, SVM S1, RF S2, SVM S2)
Visualisasi final untuk Bab 5 (Pembahasan)
================================================================================
"""

import os, pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

# Plot style
sns.set_style("whitegrid")
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 11,
    'axes.titlesize': 13, 'axes.labelsize': 11,
    'savefig.dpi': 200, 'savefig.bbox': 'tight'
})

OUT_BASE = '/home/claude/skripsi/03_modelling'
COMP_DIR = '/home/claude/skripsi/04_comparison'
os.makedirs(COMP_DIR, exist_ok=True)

CLASS_ORDER = ['Rendah', 'Sedang', 'Tinggi']

# Load raw results
with open(os.path.join(OUT_BASE, 'results_raw.pkl'), 'rb') as f:
    results = pickle.load(f)

# ============ PLOT 1: GROUPED BAR CHART METRIK 4 MODEL ============
metrics_data = []
for key, r in results.items():
    metrics_data.append({
        'Model': f"{r['model_name'].upper()} S{r['scenario']}",
        'Accuracy': r['test_accuracy'],
        'Precision': r['test_precision_w'],
        'Recall': r['test_recall_w'],
        'F1 (weighted)': r['test_f1_w'],
        'F1 (macro)': r['test_f1_macro']
    })
mdf = pd.DataFrame(metrics_data)
# Reorder: RF S1, SVM S1, RF S2, SVM S2
ordered = ['RF S1', 'SVM S1', 'RF S2', 'SVM S2']
mdf['Model'] = pd.Categorical(mdf['Model'], categories=ordered, ordered=True)
mdf = mdf.sort_values('Model').reset_index(drop=True)

fig, ax = plt.subplots(figsize=(11, 5.5))
metric_cols = ['Accuracy', 'Precision', 'Recall', 'F1 (weighted)', 'F1 (macro)']
x = np.arange(len(mdf))
width = 0.16
colors_m = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#5F8B5F']

for i, m in enumerate(metric_cols):
    offset = (i - 2) * width
    bars = ax.bar(x + offset, mdf[m], width, label=m, color=colors_m[i],
                   edgecolor='black', linewidth=0.4)
    for bar, v in zip(bars, mdf[m]):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.005,
                f'{v:.3f}', ha='center', va='bottom', fontsize=8.5, rotation=0)

ax.set_xticks(x)
ax.set_xticklabels(mdf['Model'])
ax.set_ylabel('Skor')
ax.set_title('Komparasi Metrik Evaluasi — 4 Model')
ax.legend(loc='lower right', ncol=5, fontsize=10, framealpha=0.95)
ax.set_ylim(0, 0.92)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(os.path.join(COMP_DIR, '01_grouped_bar_4model.png'))
plt.close()
print("✓ 01_grouped_bar_4model.png")

# ============ PLOT 2: CONFUSION MATRIX 4 PANEL ============
fig, axes = plt.subplots(2, 2, figsize=(11.5, 9.5))
titles = {
    'rf_s1': 'RF — Skenario 1',
    'svm_s1': 'SVM — Skenario 1',
    'rf_s2': 'RF — Skenario 2',
    'svm_s2': 'SVM — Skenario 2'
}
positions = {'rf_s1': (0,0), 'svm_s1': (0,1), 'rf_s2': (1,0), 'svm_s2': (1,1)}
for key, ax_pos in positions.items():
    cm = results[key]['cm']
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
    annot = np.array([[f'{cm[i,j]}\n({cm_norm[i,j]:.2f})'
                       for j in range(cm.shape[1])] for i in range(cm.shape[0])])
    ax = axes[ax_pos[0], ax_pos[1]]
    sns.heatmap(cm, annot=annot, fmt='', cmap='Blues',
                xticklabels=CLASS_ORDER, yticklabels=CLASS_ORDER,
                cbar_kws={'shrink': 0.75}, ax=ax,
                linewidths=0.5, linecolor='gray',
                annot_kws={'fontsize': 11})
    ax.set_title(titles[key])
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
plt.suptitle('Confusion Matrix — Komparasi 4 Model (count + normalisasi)',
             fontsize=14, y=1.0)
plt.tight_layout()
plt.savefig(os.path.join(COMP_DIR, '02_confusion_matrix_4panel.png'))
plt.close()
print("✓ 02_confusion_matrix_4panel.png")

# ============ PLOT 3: METRIK PER KELAS (untuk best model per algoritma+skenario) ============
from sklearn.metrics import precision_recall_fscore_support

per_class_data = []
for key, r in results.items():
    p, rec, f1, _ = precision_recall_fscore_support(
        r['y_test'], r['y_pred'], labels=CLASS_ORDER, zero_division=0
    )
    for i, c in enumerate(CLASS_ORDER):
        per_class_data.append({
            'Model': f"{r['model_name'].upper()} S{r['scenario']}",
            'Kelas': c, 'Precision': p[i], 'Recall': rec[i], 'F1': f1[i]
        })
pc_df = pd.DataFrame(per_class_data)
pc_df.to_csv(os.path.join(COMP_DIR, 'tabel_metrik_per_kelas.csv'), index=False)

# Visualisasi: 3 panel (precision, recall, f1) per kelas, per model
fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
metric_names = ['Precision', 'Recall', 'F1']
class_colors = {'Rendah': '#2E86AB', 'Sedang': '#F18F01', 'Tinggi': '#C73E1D'}

for i, m in enumerate(metric_names):
    ax = axes[i]
    pivot = pc_df.pivot(index='Model', columns='Kelas', values=m).reindex(ordered)
    pivot = pivot[CLASS_ORDER]
    pivot.plot(kind='bar', ax=ax, color=[class_colors[c] for c in CLASS_ORDER],
               edgecolor='black', linewidth=0.4, width=0.78)
    ax.set_title(f'{m} per Kelas')
    ax.set_ylabel(m)
    ax.set_xlabel('')
    ax.set_ylim(0, 1.05)
    ax.tick_params(axis='x', rotation=0)
    ax.legend(title='Kelas', fontsize=9, loc='lower right')
plt.suptitle('Metrik per Kelas — Komparasi 4 Model', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(COMP_DIR, '03_metrik_per_kelas.png'))
plt.close()
print("✓ 03_metrik_per_kelas.png")

# ============ TABEL RINGKASAN MARKDOWN-FRIENDLY ============
md_summary = []
md_summary.append("RINGKASAN KOMPARASI 4 MODEL\n" + "="*70)
md_summary.append("")
md_summary.append(f"{'Model':<10}{'CV F1_w':<12}{'Test Acc':<12}{'Test Prec':<12}{'Test Rec':<12}{'Test F1_w':<12}{'Test F1_m':<12}")
md_summary.append("-"*82)
for key in ['rf_s1', 'svm_s1', 'rf_s2', 'svm_s2']:
    r = results[key]
    md_summary.append(
        f"{r['model_name'].upper()+' S'+r['scenario']:<10}"
        f"{r['best_cv_score']:<12.4f}"
        f"{r['test_accuracy']:<12.4f}"
        f"{r['test_precision_w']:<12.4f}"
        f"{r['test_recall_w']:<12.4f}"
        f"{r['test_f1_w']:<12.4f}"
        f"{r['test_f1_macro']:<12.4f}"
    )

md_summary.append("")
md_summary.append("BEST PARAMETERS:")
for key in ['rf_s1', 'svm_s1', 'rf_s2', 'svm_s2']:
    r = results[key]
    md_summary.append(f"  {r['model_name'].upper()} S{r['scenario']}: {r['best_params']}")

# Determine overall best
best_key = max(results.keys(), key=lambda k: results[k]['test_f1_w'])
best_r = results[best_key]
md_summary.append("")
md_summary.append(f"=> BEST MODEL OVERALL: {best_r['model_name'].upper()} Skenario {best_r['scenario']}")
md_summary.append(f"   Test F1 (weighted) = {best_r['test_f1_w']:.4f}")
md_summary.append(f"   Test Accuracy = {best_r['test_accuracy']:.4f}")

with open(os.path.join(COMP_DIR, 'RINGKASAN_KOMPARASI.txt'), 'w') as f:
    f.write('\n'.join(md_summary))
print("✓ RINGKASAN_KOMPARASI.txt")

print("\n" + "\n".join(md_summary))
