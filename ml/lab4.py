import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LassoCV, RidgeCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler, PolynomialFeatures

df = pd.read_csv("AirQualityUCI.csv", sep=";", decimal=",")
df = df.drop(columns=["Unnamed: 15", "Unnamed: 16"])
df.dropna(subset=["CO(GT)", "C6H6(GT)", "T", "RH", "NO2(GT)"], inplace=True)
df = df.apply(pd.to_numeric, errors="coerce")

y = df["CO(GT)"]

features = ["C6H6(GT)", "T", "RH", "NO2(GT)"]
X = df[features]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 1
model_simple = LinearRegression()
model_simple.fit(X_train[["C6H6(GT)"]], y_train)

y_pred_simple = model_simple.predict(X_test[["C6H6(GT)"]])

print("1. Базовая линейная регрессия с одним признаком:")
print(f"R²: {r2_score(y_test, y_pred_simple):.5f}")
print(f"MSE: {mean_squared_error(y_test, y_pred_simple):.5f}")

# 2
lr_multi = LinearRegression()
lr_multi.fit(X_train, y_train)

y_pred_multi = lr_multi.predict(X_test)

print("Множественная линейная регрессия:")
print("R²:", r2_score(y_test, y_pred_multi))
print("MSE:", mean_squared_error(y_test, y_pred_multi))

# 3
lr_multi = LinearRegression()
lr_multi.fit(X_train, y_train)

y_pred_multi = lr_multi.predict(X_test)

print("Множественная линейная регрессия:")
print("R²:", r2_score(y_test, y_pred_multi))
print("MSE:", mean_squared_error(y_test, y_pred_multi))

# 4
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

lr_scaled = LinearRegression()
lr_scaled.fit(X_train_scaled, y_train)

y_pred_scaled = lr_scaled.predict(X_test_scaled)

print("Линейная регрессия после стандартизации:")
print("R²:", r2_score(y_test, y_pred_scaled))
print("MSE:", mean_squared_error(y_test, y_pred_scaled))

# 5
lasso = LassoCV(cv=5, random_state=42)
lasso.fit(X_train_scaled, y_train)

y_pred_lasso = lasso.predict(X_test_scaled)

print("Lasso регрессия:")
print("R²:", r2_score(y_test, y_pred_lasso))
print("MSE:", mean_squared_error(y_test, y_pred_lasso))
print("Оптимальное alpha:", lasso.alpha_)
print("Количество ненулевых коэффициентов:", np.sum(lasso.coef_ != 0))

# 6
ridge = RidgeCV(cv=5)
ridge.fit(X_train_scaled, y_train)

y_pred_ridge = ridge.predict(X_test_scaled)

print("Ridge регрессия:")
print("R²:", r2_score(y_test, y_pred_ridge))
print("MSE:", mean_squared_error(y_test, y_pred_ridge))
print("Оптимальное alpha:", ridge.alpha_)

# 7
kf = KFold(n_splits=5, shuffle=True, random_state=42)
r2_scores = cross_val_score(lr_multi, X, y, cv=kf, scoring="r2")
mse_scores = -cross_val_score(lr_multi, X, y, cv=kf, scoring="neg_mean_squared_error")

print("Кросс-валидация:")
print("Средний R²:", np.mean(r2_scores))
print("Средний MSE:", np.mean(mse_scores))

# 8
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X_train_scaled)
X_test_poly = poly.transform(X_test_scaled)

lr_poly = LinearRegression()
lr_poly.fit(X_poly, y_train)

y_pred_poly = lr_poly.predict(X_test_poly)

print("Полиномиальная регрессия (степень 2):")
print("R²:", r2_score(y_test, y_pred_poly))
print("MSE:", mean_squared_error(y_test, y_pred_poly))

# 9
models = {
    "Simple LR": (r2_score(y_test, y_pred_simple), mean_squared_error(y_test, y_pred_simple)),
    "Multiple LR": (r2_score(y_test, y_pred_multi), mean_squared_error(y_test, y_pred_multi)),
    "Standardized LR": (r2_score(y_test, y_pred_scaled), mean_squared_error(y_test, y_pred_scaled)),
    "Lasso": (r2_score(y_test, y_pred_lasso), mean_squared_error(y_test, y_pred_lasso)),
    "Ridge": (r2_score(y_test, y_pred_ridge), mean_squared_error(y_test, y_pred_ridge)),
    "Polynomial LR": (r2_score(y_test, y_pred_poly), mean_squared_error(y_test, y_pred_poly)),
}

comparison = pd.DataFrame(models, index=["R²", "MSE"])
print(comparison)
