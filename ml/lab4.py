import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LassoCV
from sklearn.linear_model import RidgeCV
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures

df = pd.read_csv("AirQualityUCI.csv", sep=";", decimal=",", encoding="latin1")
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
df = df.replace(-200, np.nan)
numeric_cols = ["CO(GT)", "PT08.S1(CO)", "NMHC(GT)", "C6H6(GT)", "PT08.S2(NMHC)",
                "NOx(GT)", "PT08.S3(NOx)", "NO2(GT)", "PT08.S4(NO2)",
                "PT08.S5(O3)", "T", "RH", "AH"]
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

df.dropna(subset=["CO(GT)", "C6H6(GT)", "T", "RH", "NO2(GT)"], inplace=True)

y = df["CO(GT)"].values
rng = 42
X_full = df[numeric_cols].copy()

X_train_full, X_test_full, y_train, y_test = train_test_split(
    X_full, y, test_size=0.2, random_state=rng
)


def report_metrics(model, X_tr, X_te, y_tr, y_te, name="model"):
    y_pred = model.predict(X_te)
    r2 = r2_score(y_te, y_pred)
    mse = mean_squared_error(y_te, y_pred)
    print(f"{name}: R2 = {r2:.10f}, MSE = {mse:.10f}")
    return r2, mse


# 1
print("\nЗадание 1: Простая линейная регрессия (CO ~ C6H6)")
X = df[["C6H6(GT)"]].values
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=rng)
lm_simple = LinearRegression().fit(X_tr, y_tr)
r2_s, mse_s = report_metrics(lm_simple, X_tr, X_te, y_tr, y_te, name="Linear CO ~ C6H6")

# 2
print("\nЗадание 2: Множественная линейная регрессия (CO ~ C6H6, T, RH, NO2)")
features_2 = ["C6H6(GT)", "T", "RH", "NO2(GT)"]
X = df[features_2].values
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=rng)
lm_multi = LinearRegression().fit(X_tr, y_tr)
r2_m, mse_m = report_metrics(lm_multi, X_tr, X_te, y_tr, y_te, name="Linear multifeat")

# 3
print("\nЗадание 3: Линейная регрессия со стандартизацией")
pipe_std = Pipeline([("scaler", StandardScaler()), ("lr", LinearRegression())])
pipe_std.fit(X_tr, y_tr)
r2_std, mse_std = report_metrics(pipe_std, X_tr, X_te, y_tr, y_te, name="Std + Linear")

# 4
print("\nЗадание 4: Линейная регрессия с L1-регуляризацией (Lasso)")
X = X_full.values
mask = ~np.isnan(X).any(axis=1)
X_all = X[mask]
y_all = y[mask]

X_tr_all, X_te_all, y_tr_all, y_te_all = train_test_split(X_all, y_all, test_size=0.2, random_state=rng)

lassocv = Pipeline([
    ("scaler", StandardScaler()),
    ("lasso_cv", LassoCV(cv=5, random_state=rng, n_alphas=50, max_iter=5000))
])
lassocv.fit(X_tr_all, y_tr_all)
best_alpha_lasso = lassocv.named_steps["lasso_cv"].alpha_
lasso_model = lassocv.named_steps["lasso_cv"]
r2_lasso, mse_lasso = report_metrics(lassocv, X_tr_all, X_te_all, y_tr_all, y_te_all,
                                     name=f"LassoCV (alpha={best_alpha_lasso:.5f})")
nnz = np.sum(lasso_model.coef_ != 0)
print(
    f"Lasso: оптимальный альфа = {best_alpha_lasso:.6g}, количество ненулевых коэффициентов = {nnz}/{len(lasso_model.coef_)}")

# 5
print("\nЗадание 5: Линейная регрессия с L2-регуляризацией (Ridge)")

ridge_alphas = np.logspace(-4, 4, 50)
ridgecv = Pipeline([
    ("scaler", StandardScaler()),
    ("ridge_cv", RidgeCV(alphas=ridge_alphas, cv=5, scoring="neg_mean_squared_error"))
])
ridgecv.fit(X_tr_all, y_tr_all)
best_alpha_ridge = ridgecv.named_steps["ridge_cv"].alpha_
ridge_model = ridgecv.named_steps["ridge_cv"]
r2_ridge, mse_ridge = report_metrics(ridgecv, X_tr_all, X_te_all, y_tr_all, y_te_all,
                                     name=f"RidgeCV (alpha={best_alpha_ridge:.5f})")
print(f"Оптимальный alpha: {ridge_model.alpha_:.6f}")

# 6
print("\nЗадание 6: Кросс-валидация (K=5)")
X = df[features_2].values
y_local = y
kf = KFold(n_splits=5, shuffle=True, random_state=rng)
lm = LinearRegression()
scoring = {"r2": "r2", "mse": "neg_mean_squared_error"}
cv_res = cross_validate(lm, X, y_local, cv=kf, scoring=scoring, return_train_score=False)
r2_cv_mean = np.mean(cv_res["test_r2"])
r2_cv_std = np.std(cv_res["test_r2"])
mse_cv_mean = -np.mean(cv_res["test_mse"])
mse_cv_std = np.std(-cv_res["test_mse"])
print(
    f"CV (K=5) Linear multifeat: R2 mean={r2_cv_mean:.10f} ± {r2_cv_std:.10f}, MSE mean={mse_cv_mean:.10f} ± {mse_cv_std:.10f}")

# 7
print("\nЗадание 7: Оптимальные параметры регуляризации")
print(f"LassoCV optimal alpha = {best_alpha_lasso:.6g}")
print(f"RidgeCV optimal alpha = {best_alpha_ridge:.6g}")

# 8
print("\nЗадание 8: Полиномиальная регрессия")
poly_results = []
for deg in (2, 3):
    poly = Pipeline([
        ("poly", PolynomialFeatures(degree=deg, include_bias=False)),
        ("scaler", StandardScaler()),
        ("lr", LinearRegression())
    ])
    X = df[features_2].values
    X_tr_p, X_te_p, y_tr_p, y_te_p = train_test_split(X, y, test_size=0.2, random_state=rng)
    poly.fit(X_tr_p, y_tr_p)
    r2_p, mse_p = report_metrics(poly, X_tr_p, X_te_p, y_tr_p, y_te_p, name=f"Полиномиальная степень = {deg}")
    poly_results.append((r2_p, mse_p))

# 9
print("\nЗадание 9: Сравнение всех моделей")
results = {
    "model": ["Простая", "Множественная", "Std+Linear", "LassoCV", "RidgeCV", "Poly deg2", "Poly deg3"],
    "r2": [r2_s, r2_m, r2_std, r2_lasso, r2_ridge, poly_results[0][0], poly_results[1][0]],
    "mse": [mse_s, mse_m, mse_std, mse_lasso, mse_ridge, poly_results[0][1], poly_results[1][1]]
}
res_df = pd.DataFrame(results)
print("\nСводная таблица результатов:\n", res_df)

coef_multi = lm_multi.coef_
print("\nКоэффициенты множественной линейной регрессии:")
for feat, c in zip(features_2, coef_multi):
    print(f" {feat}: {c:.10f}")

print("\nНенулевые коэффициенты Lasso:")
for feat, c in zip(X_full.columns, lasso_model.coef_):
    if abs(c) > 1e-8:
        print(f" {feat}: {c:.10f}")
print("\nКоэффициенты Ridge:")
for feat, c in zip(X_full.columns, ridge_model.coef_):
    print(f" {feat}: {c:.10f}")
