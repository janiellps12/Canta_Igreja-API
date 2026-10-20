import pandas as pd
import os


content = pd.read_csv('duplicidades-tratado.csv')
content = content[content['Duplicados'] == True]
for item in set(content['similar']):
    index = int(item.split('-')[0])

    origin = '../dados/musicas' if index < 633 else '../dados/musicas2'

    os.rename(f"{origin}/{item}", f"../dados/musicas-duplicadas/{item}")
