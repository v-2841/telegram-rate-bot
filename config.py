pairs = [
    ['eur', 'usd'],
    ['usd', 'rub'],
    ['eur', 'rub'],
    ['amd', 'rub'],
    ['rub', 'amd'],
    ['usd', 'amd'],
    ['eur', 'amd'],
]

url_template = ('https://cdn.jsdelivr.net/gh/fawazahmed0/'
                + 'currency-api@1/latest/currencies/{}/{}.json')

rates_message = ('Курсы валют на {date} 💸\n\n'
                 + 'Евро 🇪🇺 -> Доллар 🇺🇸: {eur_usd}\n\n'
                 + 'Доллар 🇺🇸 -> Рубль 🇷🇺: {usd_rub}\n'
                 + 'Евро 🇪🇺 -> Рубль 🇷🇺: {eur_rub}\n\n'
                 + 'Драм 🇦🇲 -> Рубль 🇷🇺: {amd_rub}\n'
                 + 'Рубль 🇷🇺 -> Драм 🇦🇲: {rub_amd}\n\n'
                 + 'Доллар 🇺🇸 -> Драм 🇦🇲: {usd_amd}\n'
                 + 'Евро 🇪🇺 -> Драм 🇦🇲: {eur_amd}'
                 )
