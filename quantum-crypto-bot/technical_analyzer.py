import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

class TechnicalAnalyzer:
    def __init__(self):
        self.price_history = {}
    
    def calculate_rsi(self, prices, period=14):
        """RSI (Relative Strength Index) hesapla"""
        try:
            if len(prices) < period:
                return None
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gains = pd.Series(gains).rolling(window=period).mean()
            avg_losses = pd.Series(losses).rolling(window=period).mean()
            
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))
            
            return round(rsi.iloc[-1], 2) if not np.isnan(rsi.iloc[-1]) else None
            
        except Exception as e:
            logging.error(f"RSI hesaplama hatası: {e}")
            return None
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """MACD hesapla"""
        try:
            if len(prices) < slow:
                return None
            
            exp1 = pd.Series(prices).ewm(span=fast).mean()
            exp2 = pd.Series(prices).ewm(span=slow).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=signal).mean()
            histogram = macd - signal_line
            
            return {
                'macd': round(macd.iloc[-1], 4),
                'signal': round(signal_line.iloc[-1], 4),
                'histogram': round(histogram.iloc[-1], 4)
            }
            
        except Exception as e:
            logging.error(f"MACD hesaplama hatası: {e}")
            return None
    
    def calculate_support_resistance(self, prices):
        """Basit support/resistance seviyeleri"""
        try:
            if len(prices) < 10:
                return None
            
            # Basit pivot noktaları
            support = min(prices[-10:])
            resistance = max(prices[-10:])
            current = prices[-1]
            
            return {
                'support': round(support, 2),
                'resistance': round(resistance, 2),
                'current': round(current, 2),
                'distance_to_support': round(((current - support) / current) * 100, 2),
                'distance_to_resistance': round(((resistance - current) / current) * 100, 2)
            }
            
        except Exception as e:
            logging.error(f"Support/Resistance hatası: {e}")
            return None
    
    def generate_technical_signals(self, coin_data):
        """Teknik sinyaller oluştur"""
        try:
            signals = []
            
            # RSI Sinyali
            rsi = self.calculate_rsi(coin_data.get('price_history', []))
            if rsi:
                if rsi > 70:
                    signals.append(f"RSI {rsi} - OVERBOUGHT ⚠️")
                elif rsi < 30:
                    signals.append(f"RSI {rsi} - OVERSOLD 🟢")
                else:
                    signals.append(f"RSI {rsi} - Neutral")
            
            # MACD Sinyali
            macd = self.calculate_macd(coin_data.get('price_history', []))
            if macd:
                if macd['macd'] > macd['signal'] and macd['histogram'] > 0:
                    signals.append("MACD BULLISH 📈")
                elif macd['macd'] < macd['signal'] and macd['histogram'] < 0:
                    signals.append("MACD BEARISH 📉")
            
            # Support/Resistance
            sr = self.calculate_support_resistance(coin_data.get('price_history', []))
            if sr:
                if sr['distance_to_support'] < 2:
                    signals.append("NEAR SUPPORT 🛡️")
                if sr['distance_to_resistance'] < 2:
                    signals.append("NEAR RESISTANCE ⚡")
            
            return signals if signals else ["No clear signals"]
            
        except Exception as e:
            logging.error(f"Teknik sinyal hatası: {e}")
            return ["Analysis pending"]
    
    def get_trend_strength(self, prices):
        """Trend gücünü analiz et"""
        try:
            if len(prices) < 5:
                return "No data"
            
            recent = prices[-5:]
            trend = "SIDEWAYS"
            strength = 0
            
            if all(recent[i] < recent[i+1] for i in range(len(recent)-1)):
                trend = "UPTREND"
                strength = min(100, ((recent[-1] - recent[0]) / recent[0]) * 1000)
            elif all(recent[i] > recent[i+1] for i in range(len(recent)-1)):
                trend = "DOWNTREND" 
                strength = min(100, ((recent[0] - recent[-1]) / recent[0]) * 1000)
            
            return f"{trend} ({strength:.1f})"
            
        except Exception as e:
            logging.error(f"Trend analiz hatası: {e}")
            return "Unknown"