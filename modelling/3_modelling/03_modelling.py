"""
================================================================================
SKRIPSI - KLASIFIKASI KEPADATAN LALU LINTAS
Modelling: Random Forest & SVM dengan GridSearchCV
================================================================================

Skenario 1: Tingkat_Kepadatan = 0  -> Rendah
Skenario 2: Tingkat_Kepadatan = 0 dengan catatan "ramai lancar" -> Sedang

Setup:
- Split 80:20 stratified, random_state=42
- StratifiedKFold k=5 untuk cross-validation
- Scoring: f1_weighted (memperhitungkan class imbalance)
- class_weight='balanced' digunakan sebagai default pada kedua algoritma
- SVM dalam Pipeline dengan StandardScaler (mencegah data leakage)
- RF tidak memerlukan scaling (tree-based, scale-invariant)

Output: model pickle, gridsearch results CSV, confusion matrix PNG,
classification report TXT, feature/permutation importance PNG.

Author: Skripsi Dani Ruliansyah, Universitas Airlangga, 2026
================================================================================
"""

import os, sys, time, json, warnings, pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score
)
from sklearn.inspection import permutation_importance

warnings.filterwarnings('ignore')

# ============ KONFIGURASI ============
RANDOM_STATE = 42
TEST_SIZE = 0.20
CV_FOLDS = 5
# Multi-scoring: GridSearchCV akan mengevaluasi keempat metrik untuk setiap kombinasi.
# refit='f1_weighted' artinya model terbaik dipilih berdasarkan F1-weighted (cocok untuk imbalance).
SCORING = {
    'accuracy': 'accuracy',
    'precision_weighted': 'precision_weighted',
    'recall_weighted': 'recall_weighted',
    'f1_weighted': 'f1_weighted'
}
REFIT_METRIC = 'f1_weighted'
CLASS_ORDER = ['Rendah', 'Sedang', 'Tinggi']

DATA_PATH = '/home/claude/skripsi/02_preprocessing/dataset_preprocessed.csv'
OUT_BASE = '/home/claude/skripsi/03_modelling'

# Plot style
sns.set_style("whitegrid")
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 11,
    'axes.titlesize': 13, 'axes.labelsize': 11,
    'savefig.dpi': 200, 'savefig.bbox': 'tight'
})

# Hyperparameter grid (Opsi B-Slim, revisi dari Bab 3 Tabel 3.11 dan 3.12)
# Justifikasi reduksi grid:
# - RF n_estimators: 100 dan 200 sudah cukup melihat efek jumlah tree
# - RF max_depth: 10 (dibatasi) vs None (unlimited) — kontras untuk efek regularisasi
# - RF min_samples_split, min_samples_leaf: 2 nilai cukup melihat efek regularisasi struktur
# - SVM kernel: 3 jenis utama dipertahankan untuk variasi metode pemisahan
# - SVM C: rentang 0.1 / 1 / 10 mewakili margin lebar / seimbang / strict
# - SVM gamma: 'scale' (default) + 0.1 (manual) cukup mewakili efek pengaruh sampel
PARAM_GRID_RF = {
    'n_estimators': [100, 200],
    'max_depth': [10, None],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2]
}  # Total: 16 kombinasi

PARAM_GRID_SVM = {
    'svm__kernel': ['linear', 'rbf', 'poly'],
    'svm__C': [0.1, 1, 10],
    'svm__gamma': ['scale', 0.1]
}  # Total: 18 kombinasi


# ============ FUNGSI HELPER ============

def load_data():
    """Load dataset preprocessed."""
    df = pd.read_csv(DATA_PATH)
    feature_cols = [c for c in df.columns if c not in ['Label_S1', 'Label_S2']]
    X = df[feature_cols].copy()
    y_s1 = df['Label_S1'].copy()
    y_s2 = df['Label_S2'].copy()
    print(f"Dataset loaded: {df.shape[0]} rows, {len(feature_cols)} features")
    print(f"  Features: {feature_cols}")
    return X, y_s1, y_s2, feature_cols


def plot_confusion_matrix(cm, classes, title, save_path):
    """Confusion matrix dengan count + persentase."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    # Count
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes,
                cbar_kws={'shrink': 0.85}, ax=axes[0],
                linewidths=0.5, linecolor='gray')
    axes[0].set_title(f'{title} — Count')
    axes[0].set_xlabel('Predicted')
    axes[0].set_ylabel('Actual')
    # Normalized (row-wise = recall)
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues',
                xticklabels=classes, yticklabels=classes,
                cbar_kws={'shrink': 0.85}, ax=axes[1], vmin=0, vmax=1,
                linewidths=0.5, linecolor='gray')
    axes[1].set_title(f'{title} — Normalized (per row)')
    axes[1].set_xlabel('Predicted')
    axes[1].set_ylabel('Actual')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_feature_importance_rf(model, feature_names, title, save_path):
    """Feature importance dari Random Forest."""
    imp = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=True)

    fig, ax = plt.subplots(figsize=(9, max(4.5, 0.32*len(feature_names))))
    bars = ax.barh(imp['feature'], imp['importance'], color='#4A6FA5', edgecolor='black', linewidth=0.5)
    for bar, v in zip(bars, imp['importance']):
        ax.text(v + 0.003, bar.get_y() + bar.get_height()/2,
                f'{v:.3f}', va='center', fontsize=9)
    ax.set_xlabel('Importance')
    ax.set_title(title)
    ax.set_xlim(0, imp['importance'].max() * 1.18)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_permutation_importance_svm(model, X_test, y_test, feature_names, title, save_path):
    """Permutation importance untuk SVM (karena SVM non-linear tidak punya native FI)."""
    result = permutation_importance(model, X_test, y_test,
                                     n_repeats=10, random_state=RANDOM_STATE, n_jobs=-1)
    imp = pd.DataFrame({
        'feature': feature_names,
        'importance': result.importances_mean,
        'std': result.importances_std
    }).sort_values('importance', ascending=True)

    fig, ax = plt.subplots(figsize=(9, max(4.5, 0.32*len(feature_names))))
    bars = ax.barh(imp['feature'], imp['importance'], xerr=imp['std'],
                    color='#C73E1D', edgecolor='black', linewidth=0.5,
                    error_kw={'ecolor': 'gray', 'linewidth': 1, 'capsize': 3})
    ax.set_xlabel('Mean decrease in f1_weighted (permutation)')
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def save_classification_report_txt(y_true, y_pred, classes, save_path, header=""):
    """Simpan classification report ke file teks."""
    report = classification_report(y_true, y_pred, labels=classes,
                                    target_names=classes, digits=4, zero_division=0)
    with open(save_path, 'w') as f:
        if header:
            f.write(header + '\n' + '='*70 + '\n\n')
        f.write(report)


def run_gridsearch(X_train, y_train, X_test, y_test, feature_names,
                    model_name, scenario, out_dir):
    """Pipeline utama: GridSearchCV, evaluasi, simpan semua output."""
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"  {model_name.upper()} — SKENARIO {scenario}")
    print(f"{'='*70}")
    print(f"  Train: {len(X_train)} | Test: {len(X_test)}")
    print(f"  Distribusi target (train): {y_train.value_counts().to_dict()}")

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    t0 = time.time()

    # Build estimator + param_grid sesuai algoritma
    if model_name == 'rf':
        estimator = RandomForestClassifier(random_state=RANDOM_STATE,
                                            class_weight='balanced', n_jobs=1)
        param_grid = PARAM_GRID_RF
    elif model_name == 'svm':
        estimator = Pipeline([
            ('scaler', StandardScaler()),
            ('svm', SVC(random_state=RANDOM_STATE, class_weight='balanced',
                        cache_size=500))
        ])
        param_grid = PARAM_GRID_SVM
    else:
        raise ValueError(f"Unknown model: {model_name}")

    # GridSearch
    n_combos = 1
    for v in param_grid.values():
        n_combos *= len(v)
    print(f"  Total kombinasi: {n_combos} × {CV_FOLDS} fold = {n_combos*CV_FOLDS} fits")

    grid = GridSearchCV(estimator=estimator, param_grid=param_grid,
                         cv=cv, scoring=SCORING, refit=REFIT_METRIC,
                         n_jobs=-1, verbose=0)
    grid.fit(X_train, y_train)
    elapsed = time.time() - t0
    print(f"  ✓ GridSearch selesai dalam {elapsed:.1f}s")
    print(f"  Best CV {REFIT_METRIC}: {grid.best_score_:.4f}")
    print(f"  Best params: {grid.best_params_}")

    # === SIMPAN: tabel ringkasan semua kombinasi (DENGAN 4 METRIK) ===
    cv_results = pd.DataFrame(grid.cv_results_)
    # Kolom untuk setiap metrik: mean_test_<metric>, std_test_<metric>
    metric_cols = []
    for m in ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted']:
        metric_cols += [f'mean_test_{m}', f'std_test_{m}']
    metric_cols += [f'rank_test_{REFIT_METRIC}', 'mean_fit_time']
    param_cols = [c for c in cv_results.columns if c.startswith('param_')]
    summary = cv_results[param_cols + metric_cols].copy()
    # Rename agar lebih mudah dibaca di skripsi
    summary = summary.rename(columns={
        'mean_test_accuracy': 'CV_Accuracy',
        'std_test_accuracy': 'CV_Accuracy_std',
        'mean_test_precision_weighted': 'CV_Precision',
        'std_test_precision_weighted': 'CV_Precision_std',
        'mean_test_recall_weighted': 'CV_Recall',
        'std_test_recall_weighted': 'CV_Recall_std',
        'mean_test_f1_weighted': 'CV_F1_weighted',
        'std_test_f1_weighted': 'CV_F1_weighted_std',
        f'rank_test_{REFIT_METRIC}': 'Rank',
        'mean_fit_time': 'Fit_Time_sec'
    })
    summary = summary.sort_values('Rank').reset_index(drop=True)
    # Round untuk readability
    for col in summary.columns:
        if 'CV_' in col or 'Fit_Time' in col:
            summary[col] = summary[col].round(4)
    summary.to_csv(os.path.join(out_dir, '01_gridsearch_all_combinations.csv'), index=False)

    # === Evaluasi pada test set ===
    best_model = grid.best_estimator_
    y_pred = best_model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
    print(f"\n  Test set metrics:")
    print(f"    Accuracy        : {acc:.4f}")
    print(f"    Precision (wt)  : {prec:.4f}")
    print(f"    Recall (wt)     : {rec:.4f}")
    print(f"    F1-score (wt)   : {f1:.4f}")
    print(f"    F1-score (macro): {f1_macro:.4f}")

    # === SIMPAN: best params ===
    with open(os.path.join(out_dir, '02_best_params.txt'), 'w') as f:
        f.write(f"BEST MODEL — {model_name.upper()} | SKENARIO {scenario}\n")
        f.write("="*70 + "\n\n")
        f.write(f"Best CV {REFIT_METRIC}: {grid.best_score_:.4f}\n")
        f.write(f"GridSearch duration: {elapsed:.2f} seconds\n")
        f.write(f"Total combinations evaluated: {n_combos}\n\n")
        f.write("Best parameters:\n")
        for k, v in grid.best_params_.items():
            f.write(f"  {k}: {v}\n")
        f.write(f"\nTest set metrics:\n")
        f.write(f"  Accuracy        : {acc:.4f}\n")
        f.write(f"  Precision (wt)  : {prec:.4f}\n")
        f.write(f"  Recall (wt)     : {rec:.4f}\n")
        f.write(f"  F1-score (wt)   : {f1:.4f}\n")
        f.write(f"  F1-score (macro): {f1_macro:.4f}\n")

    # === SIMPAN: confusion matrix ===
    cm = confusion_matrix(y_test, y_pred, labels=CLASS_ORDER)
    plot_confusion_matrix(cm, CLASS_ORDER,
        f'Confusion Matrix — {model_name.upper()} Skenario {scenario}',
        os.path.join(out_dir, '03_confusion_matrix.png'))

    # === SIMPAN: classification report ===
    save_classification_report_txt(y_test, y_pred, CLASS_ORDER,
        os.path.join(out_dir, '04_classification_report.txt'),
        header=f"CLASSIFICATION REPORT — {model_name.upper()} Skenario {scenario}")

    # === SIMPAN: feature importance ===
    if model_name == 'rf':
        plot_feature_importance_rf(best_model, feature_names,
            f'Feature Importance — RF Skenario {scenario}',
            os.path.join(out_dir, '05_feature_importance.png'))
    elif model_name == 'svm':
        plot_permutation_importance_svm(best_model, X_test, y_test, feature_names,
            f'Permutation Importance — SVM Skenario {scenario}',
            os.path.join(out_dir, '05_permutation_importance.png'))

    # === SIMPAN: model pickle ===
    with open(os.path.join(out_dir, 'model.pkl'), 'wb') as f:
        pickle.dump(best_model, f)

    return {
        'model_name': model_name, 'scenario': scenario,
        'best_cv_score': grid.best_score_, 'best_params': grid.best_params_,
        'test_accuracy': acc, 'test_precision_w': prec,
        'test_recall_w': rec, 'test_f1_w': f1, 'test_f1_macro': f1_macro,
        'cm': cm, 'y_test': y_test.values, 'y_pred': y_pred,
        'n_combinations': n_combos, 'elapsed_sec': elapsed,
        'best_model': best_model
    }


# ============ MAIN ============
if __name__ == '__main__':
    print("="*70)
    print("MODELLING — KLASIFIKASI KEPADATAN LALU LINTAS")
    print("="*70)
    X, y_s1, y_s2, feature_names = load_data()

    results = {}
    for scenario_label, y in [('1', y_s1), ('2', y_s2)]:
        # Split fixed per skenario (sama untuk RF dan SVM)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
        )
        print(f"\n[Skenario {scenario_label}] Split: train={len(X_train)}, test={len(X_test)}")
        print(f"  Distribusi test set: {y_test.value_counts().to_dict()}")

        # RF
        rf_out = os.path.join(OUT_BASE, f'rf_scenario{scenario_label}')
        results[f'rf_s{scenario_label}'] = run_gridsearch(
            X_train, y_train, X_test, y_test, feature_names,
            'rf', scenario_label, rf_out
        )

        # SVM
        svm_out = os.path.join(OUT_BASE, f'svm_scenario{scenario_label}')
        results[f'svm_s{scenario_label}'] = run_gridsearch(
            X_train, y_train, X_test, y_test, feature_names,
            'svm', scenario_label, svm_out
        )

    # Simpan ringkasan agregat
    summary = []
    for key, r in results.items():
        summary.append({
            'Algoritma': r['model_name'].upper(),
            'Skenario': r['scenario'],
            'Best CV F1_weighted': round(r['best_cv_score'], 4),
            'Test Accuracy': round(r['test_accuracy'], 4),
            'Test Precision (w)': round(r['test_precision_w'], 4),
            'Test Recall (w)': round(r['test_recall_w'], 4),
            'Test F1 (w)': round(r['test_f1_w'], 4),
            'Test F1 (macro)': round(r['test_f1_macro'], 4),
            'Durasi (s)': round(r['elapsed_sec'], 1),
            'Best Params': json.dumps(r['best_params'], default=str)
        })
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(os.path.join(OUT_BASE, 'ringkasan_4_model.csv'), index=False)

    # Save raw results untuk visualisasi comparison di step berikut
    with open(os.path.join(OUT_BASE, 'results_raw.pkl'), 'wb') as f:
        pickle.dump(results, f)

    print("\n" + "="*70)
    print("RINGKASAN 4 MODEL")
    print("="*70)
    print(summary_df.to_string(index=False))
    print(f"\n✓ Selesai. Output di: {OUT_BASE}")
