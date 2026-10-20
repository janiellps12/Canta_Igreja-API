import csv

musicas = "../dados/musicas"
# FIXME
arquivo = "/tmp/sample/sample.csv"

with open(arquivo, 'r') as file:
    reader = csv.DictReader(file)

    for row in reader:
        with open(f"{musicas}/{row['indice_geral']}.txt", 'w') as musica:
            musica.write(row['App'])
