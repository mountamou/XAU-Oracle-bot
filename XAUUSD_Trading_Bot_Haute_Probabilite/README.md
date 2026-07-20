# XAUUSD Trading Bot - Haute Probabilite

## Description
Bot de trading pour l'or (XAU/USD) base sur une strategie de confluence multi-indicateurs :
- EMA 9 / 20 / 50 (Tendance)
- MACD (Momentum)
- RSI 14 (Force)
- Fibonacci 0.618 (Structure)
- ATR 14 (Volatilite / SL-TP)

## Structure du projet
```
.
├── main.py          # Code source complet du bot
├── buildozer.spec   # Configuration compilation APK
├── requirements.txt # Dependances Python
└── README.md        # Ce fichier
```

## Execution sur PC (test)
```bash
pip install -r requirements.txt
python main.py
```

## Compilation APK (Android)

### 1. Installation des dependances (Linux/WSL)
```bash
pip install buildozer
pip install cython==0.29.33
sudo apt-get install -y python3-pip git python3-dev ffmpeg \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    zlib1g-dev libgstreamer1.0 gstreamer1.0-plugins-good \
    build-essential libsqlite3-dev sqlite3 bzip2 libbz2-dev \
    libssl-dev openssl libffi-dev liblzma-dev libreadline-dev \
    libncursesw5-dev uuid-dev
```

### 2. Initialisation (une seule fois)
```bash
buildozer init
```

### 3. Compilation
```bash
buildozer android debug
```

L'APK sera genere dans : `bin/xauusd_bot-1.0-arm64-v8a-debug.apk`

### 4. Deploiement direct
```bash
buildozer android debug deploy run
```

## Strategie de Confluence

### Signal LONG (Achat)
- Prix > EMA20 > EMA50 (tendance haussiere)
- MACD ligne > Signal & Histogramme croissant
- RSI entre 45 et 70
- Prix au-dessus du niveau Fibonacci 0.618
- ADX > 25 (tendance forte)

### Signal SHORT (Vente)
- Prix < EMA20 < EMA50 (tendance baissiere)
- MACD ligne < Signal & Histogramme decroissant
- RSI entre 30 et 55
- Prix sous le niveau Fibonacci 0.618

### Gestion des Risques
- Stop Loss : 1.5 x ATR
- Take Profit : 2.0 x ATR
- Ratio R:R = 1:1.33
- Minimum 4/5 conditions alignees pour un signal

## Avertissement
Le trading comporte des risques significatifs. Ce bot est fourni a titre educatif uniquement.
Testez toujours sur compte demo avant tout usage reel. Ne risquez jamais plus de 1-2% par trade.
