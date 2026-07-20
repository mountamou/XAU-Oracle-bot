# main.py - Bot de Trading XAUUSD Haute Probabilité
# À compiler avec Buildozer pour APK Android

import json
import threading
import time
from datetime import datetime
from collections import deque

# Kivy UI
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivy.graphics import Color, Rectangle

# ==================== MOTEUR DE STRATÉGIE ====================

class XAUUSDStrategy:
    """
    Stratégie de Confluence Haute Probabilité pour XAUUSD
    Basée sur EMA + MACD + RSI + Fibonacci + ATR
    """

    def __init__(self):
        self.prices = deque(maxlen=200)
        self.highs = deque(maxlen=200)
        self.lows = deque(maxlen=200)
        self.closes = deque(maxlen=200)

        # Paramètres
        self.ema_fast = 9
        self.ema_slow = 20
        self.ema_trend = 50
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.atr_period = 14
        self.adx_period = 14

        # État
        self.position = None  # 'LONG', 'SHORT', None
        self.entry_price = 0
        self.sl_price = 0
        self.tp_price = 0
        self.trades_history = []

    def ema(self, data, period):
        """Calcule l'EMA"""
        if len(data) < period:
            return None
        k = 2 / (period + 1)
        ema_val = sum(list(data)[:period]) / period
        for price in list(data)[period:]:
            ema_val = price * k + ema_val * (1 - k)
        return ema_val

    def rsi(self, data, period):
        """Calcule le RSI"""
        if len(data) < period + 1:
            return None
        closes_list = list(data)
        gains = []
        losses = []
        for i in range(1, period + 1):
            change = closes_list[-period - 1 + i] - closes_list[-period - 2 + i]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def macd(self, data):
        """Calcule MACD"""
        ema12 = self.ema(data, self.macd_fast)
        ema26 = self.ema(data, self.macd_slow)
        if ema12 is None or ema26 is None:
            return None, None, None
        macd_line = ema12 - ema26
        macd_history = []
        closes_list = list(data)
        for i in range(self.macd_signal + self.macd_slow, len(closes_list) + 1):
            subset = closes_list[:i]
            e12 = self.ema(deque(subset, maxlen=200), self.macd_fast)
            e26 = self.ema(deque(subset, maxlen=200), self.macd_slow)
            if e12 and e26:
                macd_history.append(e12 - e26)
        signal_line = sum(macd_history[-self.macd_signal:]) / self.macd_signal if len(macd_history) >= self.macd_signal else macd_line
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def atr(self, highs, lows, closes, period):
        """Calcule l'ATR"""
        if len(highs) < period + 1:
            return None
        h = list(highs)
        l = list(lows)
        c = list(closes)
        tr_list = []
        for i in range(-period, 0):
            tr1 = h[i] - l[i]
            tr2 = abs(h[i] - c[i-1])
            tr3 = abs(l[i] - c[i-1])
            tr_list.append(max(tr1, tr2, tr3))
        return sum(tr_list) / period

    def fibonacci_618(self, highs, lows):
        """Calcule le niveau Fibonacci 0.618"""
        if len(highs) < 10 or len(lows) < 10:
            return None
        swing_high = max(list(highs)[-20:])
        swing_low = min(list(lows)[-20:])
        return swing_low + 0.618 * (swing_high - swing_low)

    def adx(self, highs, lows, closes, period):
        """Calcule l'ADX simplifié"""
        if len(highs) < period * 2:
            return None
        h = list(highs)[-period:]
        l = list(lows)[-period:]
        avg_range = sum(h[i] - l[i] for i in range(period)) / period
        return min(avg_range * 10, 50)

    def analyze(self, price_data):
        """
        Analyse complète et génération de signal
        price_data: dict avec 'open', 'high', 'low', 'close', 'timestamp'
        """
        self.prices.append(price_data['close'])
        self.highs.append(price_data['high'])
        self.lows.append(price_data['low'])
        self.closes.append(price_data['close'])

        if len(self.closes) < 50:
            return {'signal': 'WAIT', 'reason': 'Données insuffisantes'}

        ema9 = self.ema(self.closes, self.ema_fast)
        ema20 = self.ema(self.closes, self.ema_slow)
        ema50 = self.ema(self.closes, self.ema_trend)
        rsi_val = self.rsi(self.closes, self.rsi_period)
        macd_line, signal_line, hist = self.macd(self.closes)
        atr_val = self.atr(self.highs, self.lows, self.closes, self.atr_period)
        fib618 = self.fibonacci_618(self.highs, self.lows)
        adx_val = self.adx(self.highs, self.lows, self.closes, self.adx_period)

        if any(v is None for v in [ema9, ema20, ema50, rsi_val, macd_line, signal_line, atr_val, fib618]):
            return {'signal': 'WAIT', 'reason': 'Calculs en cours'}

        result = {
            'timestamp': price_data['timestamp'],
            'price': price_data['close'],
            'ema9': round(ema9, 2),
            'ema20': round(ema20, 2),
            'ema50': round(ema50, 2),
            'rsi': round(rsi_val, 2),
            'macd': round(macd_line, 4),
            'macd_signal': round(signal_line, 4),
            'atr': round(atr_val, 2),
            'fib618': round(fib618, 2),
            'adx': round(adx_val, 2) if adx_val else 0,
            'signal': 'WAIT',
            'confidence': 0,
            'reason': ''
        }

        long_conditions = {
            'trend': price_data['close'] > ema20 > ema50,
            'momentum': macd_line > signal_line and hist > 0,
            'rsi_ok': 45 < rsi_val < 70,
            'fib_ok': price_data['close'] > fib618,
            'adx_ok': adx_val > 25 if adx_val else True
        }

        short_conditions = {
            'trend': price_data['close'] < ema20 < ema50,
            'momentum': macd_line < signal_line and hist < 0,
            'rsi_ok': 30 < rsi_val < 55,
            'fib_ok': price_data['close'] < fib618,
            'adx_ok': adx_val > 25 if adx_val else True
        }

        long_score = sum(long_conditions.values())
        short_score = sum(short_conditions.values())

        if long_score >= 4 and self.position != 'LONG':
            sl = price_data['close'] - 1.5 * atr_val
            tp = price_data['close'] + 2.0 * atr_val
            result.update({
                'signal': 'BUY',
                'confidence': long_score * 20,
                'reason': f"Confluence: {long_score}/5 alignés",
                'sl': round(sl, 2),
                'tp': round(tp, 2),
                'risk_reward': '1:1.33'
            })
            self.position = 'LONG'
            self.entry_price = price_data['close']
            self.sl_price = sl
            self.tp_price = tp

        elif short_score >= 4 and self.position != 'SHORT':
            sl = price_data['close'] + 1.5 * atr_val
            tp = price_data['close'] - 2.0 * atr_val
            result.update({
                'signal': 'SELL',
                'confidence': short_score * 20,
                'reason': f"Confluence: {short_score}/5 alignés",
                'sl': round(sl, 2),
                'tp': round(tp, 2),
                'risk_reward': '1:1.33'
            })
            self.position = 'SHORT'
            self.entry_price = price_data['close']
            self.sl_price = sl
            self.tp_price = tp
        else:
            result['reason'] = f"LONG:{long_score}/5 | SHORT:{short_score}/5"

        return result


# ==================== SIMULATEUR DE MARCHÉ ====================

class MarketSimulator:
    """Simule les données XAUUSD pour démonstration"""

    def __init__(self):
        self.base_price = 2400.0
        self.trend = 0.5
        self.volatility = 8.0

    def get_tick(self):
        import random
        self.base_price += random.gauss(self.trend, self.volatility)
        noise = random.gauss(0, self.volatility * 0.3)
        return {
            'timestamp': datetime.now().isoformat(),
            'open': round(self.base_price - noise, 2),
            'high': round(self.base_price + abs(random.gauss(0, self.volatility)), 2),
            'low': round(self.base_price - abs(random.gauss(0, self.volatility)), 2),
            'close': round(self.base_price, 2)
        }


# ==================== INTERFACE KIVY ====================

class SignalCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 120
        self.padding = 10
        self.spacing = 5

        with self.canvas.before:
            Color(0.12, 0.12, 0.15, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class TradingBotApp(App):
    status_text = StringProperty("En attente de données...")
    is_running = BooleanProperty(False)

    def build(self):
        self.strategy = XAUUSDStrategy()
        self.simulator = MarketSimulator()
        self.signals_history = []

        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        header = BoxLayout(size_hint_y=None, height=60)
        self.title_label = Label(
            text='XAU ORACLE - Haute Probabilite',
            font_size='22sp',
            bold=True,
            color=(1, 0.84, 0, 1)
        )
        header.add_widget(self.title_label)
        root.add_widget(header)

        # Status
        status_box = BoxLayout(size_hint_y=None, height=40)
        self.status_label = Label(
            text=self.status_text,
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        status_box.add_widget(self.status_label)
        root.add_widget(status_box)

        # Zone des indicateurs
        indicators_grid = GridLayout(cols=3, size_hint_y=None, height=180, spacing=5)

        self.ema_label = Label(text='EMA: --', font_size='12sp', color=(0.7, 0.7, 0.7, 1))
        self.rsi_label = Label(text='RSI: --', font_size='12sp', color=(0.7, 0.7, 0.7, 1))
        self.macd_label = Label(text='MACD: --', font_size='12sp', color=(0.7, 0.7, 0.7, 1))
        self.atr_label = Label(text='ATR: --', font_size='12sp', color=(0.7, 0.7, 0.7, 1))
        self.fib_label = Label(text='FIB 0.618: --', font_size='12sp', color=(0.7, 0.7, 0.7, 1))
        self.adx_label = Label(text='ADX: --', font_size='12sp', color=(0.7, 0.7, 0.7, 1))

        for lbl in [self.ema_label, self.rsi_label, self.macd_label,
                    self.atr_label, self.fib_label, self.adx_label]:
            indicators_grid.add_widget(lbl)
        root.add_widget(indicators_grid)

        # Zone Signal
        self.signal_box = BoxLayout(size_hint_y=None, height=100, padding=10)
        with self.signal_box.canvas.before:
            Color(0.08, 0.08, 0.1, 1)
            self.signal_rect = Rectangle(pos=self.signal_box.pos, size=self.signal_box.size)
        self.signal_box.bind(pos=self.update_signal_rect, size=self.update_signal_rect)

        self.signal_label = Label(
            text='SIGNAL: EN ATTENTE\nConfluence: 0/5',
            font_size='16sp',
            bold=True,
            color=(0.5, 0.5, 0.5, 1)
        )
        self.signal_box.add_widget(self.signal_label)
        root.add_widget(self.signal_box)

        # Boutons
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.start_btn = Button(
            text='DEMARRER',
            background_color=(0, 0.7, 0.3, 1),
            on_press=self.toggle_bot
        )
        self.reset_btn = Button(
            text='REINITIALISER',
            background_color=(0.3, 0.3, 0.7, 1),
            on_press=self.reset_bot
        )
        btn_box.add_widget(self.start_btn)
        btn_box.add_widget(self.reset_btn)
        root.add_widget(btn_box)

        # Historique des signaux
        scroll = ScrollView()
        self.history_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        scroll.add_widget(self.history_layout)
        root.add_widget(scroll)

        Clock.schedule_interval(self.update_ui, 1.0)

        return root

    def update_signal_rect(self, *args):
        self.signal_rect.pos = self.signal_box.pos
        self.signal_rect.size = self.signal_box.size

    def toggle_bot(self, instance):
        self.is_running = not self.is_running
        if self.is_running:
            self.start_btn.text = 'ARRETER'
            self.start_btn.background_color = (0.8, 0.1, 0.1, 1)
            self.status_text = "Bot actif - Analyse en cours..."
        else:
            self.start_btn.text = 'DEMARRER'
            self.start_btn.background_color = (0, 0.7, 0.3, 1)
            self.status_text = "Bot en pause"
        self.status_label.text = self.status_text

    def reset_bot(self, instance):
        self.strategy = XAUUSDStrategy()
        self.signals_history = []
        self.history_layout.clear_widgets()
        self.signal_label.text = 'SIGNAL: EN ATTENTE\nConfluence: 0/5'
        self.signal_label.color = (0.5, 0.5, 0.5, 1)
        self.status_text = "Bot reinitialise"
        self.status_label.text = self.status_text

    def update_ui(self, dt):
        if not self.is_running:
            return

        tick = self.simulator.get_tick()
        result = self.strategy.analyze(tick)

        self.ema_label.text = f"EMA9: {result.get('ema9', '--')}\nEMA20: {result.get('ema20', '--')}\nEMA50: {result.get('ema50', '--')}"
        self.rsi_label.text = f"RSI: {result.get('rsi', '--')}"
        self.macd_label.text = f"MACD: {result.get('macd', '--')}\nSignal: {result.get('macd_signal', '--')}"
        self.atr_label.text = f"ATR: {result.get('atr', '--')}"
        self.fib_label.text = f"FIB 0.618: {result.get('fib618', '--')}"
        self.adx_label.text = f"ADX: {result.get('adx', '--')}"

        signal = result['signal']
        if signal == 'BUY':
            self.signal_label.text = f"SIGNAL ACHAT\nPrix: {result['price']} | Confiance: {result['confidence']}%\nSL: {result['sl']} | TP: {result['tp']}"
            self.signal_label.color = (0, 1, 0.3, 1)
            self.add_signal_to_history(result, 'BUY')
        elif signal == 'SELL':
            self.signal_label.text = f"SIGNAL VENTE\nPrix: {result['price']} | Confiance: {result['confidence']}%\nSL: {result['sl']} | TP: {result['tp']}"
            self.signal_label.color = (1, 0.2, 0.2, 1)
            self.add_signal_to_history(result, 'SELL')
        else:
            self.signal_label.text = f"{result['reason']}\nPrix: {result['price']}"
            self.signal_label.color = (0.7, 0.7, 0.7, 1)

    def add_signal_to_history(self, result, signal_type):
        if self.signals_history and self.signals_history[-1]['signal'] == signal_type:
            return

        self.signals_history.append(result)

        card = SignalCard()
        color = (0, 0.8, 0.3, 1) if signal_type == 'BUY' else (0.9, 0.1, 0.1, 1)

        time_str = result['timestamp'].split('T')[1].split('.')[0]
        card.add_widget(Label(
            text=f"[{time_str}] {signal_type} @ {result['price']}",
            color=color,
            font_size='13sp',
            bold=True,
            size_hint_y=None,
            height=25
        ))
        card.add_widget(Label(
            text=f"Confiance: {result['confidence']}% | SL: {result['sl']} | TP: {result['tp']}",
            color=(0.8, 0.8, 0.8, 1),
            font_size='11sp',
            size_hint_y=None,
            height=20
        ))
        card.add_widget(Label(
            text=f"Raisons: {result['reason']}",
            color=(0.6, 0.6, 0.6, 1),
            font_size='10sp',
            size_hint_y=None,
            height=20
        ))

        self.history_layout.add_widget(card)
        self.history_layout.height = len(self.history_layout.children) * 125


if __name__ == '__main__':
    TradingBotApp().run()
