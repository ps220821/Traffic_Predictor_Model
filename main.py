import os
import pandas as pd

# === Zet hier de map waar je CSV's staan ===
input_folder = r"C:\Users\inanc\Desktop\Fontys\semester 3\ai & data\IndividueelChallanges\Traffic model\data"
output_file = r"C:\Users\inanc\Desktop\Fontys\semester 3\ai & data\IndividueelChallanges\Traffic model\data\DataMerged.parquet"

# Alle CSV-bestanden in de map ophalen
csv_files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]

# Dataframes samenvoegen
df_list = []
for file in csv_files:
    file_path = os.path.join(input_folder, file)
    df = pd.read_csv(file_path)
    df_list.append(df)

# Alle CSV's aan elkaar plakken
merged_df = pd.concat(df_list, ignore_index=True)

# Opslaan naar parquet
merged_df.to_parquet(output_file, engine="pyarrow", index=False)

print(f"Samengevoegd parquet bestand opgeslagen als: {output_file}")
