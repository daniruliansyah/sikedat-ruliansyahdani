import pandas as pd

df = pd.read_csv('labeled_frekuensi-cyclefailure/sorted.csv')  # sesuaikan nama file

print(df['Tingkat_Kepadatan'].value_counts().sort_index())
print()
print("Jumlah nilai 0:", (df['Tingkat_Kepadatan'] == 0).sum())
print("Persentase nilai 0:", (df['Tingkat_Kepadatan'] == 0).mean() * 100, "%")