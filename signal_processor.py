import logging
from datetime import datetime
from typing import Dict, Optional
from config import Config
from telegram_bot import TelegramBot

logger = logging.getLogger(__name__)

class SignalProcessor:
    def __init__(self):
        self.telegram_bot = TelegramBot()
    
    async def process_signal(self, raw_data: Dict) -> bool:
        """
        Process incoming TradingView signal and send to Telegram if valid
        
        Args:
            raw_data: Raw webhook data from TradingView
            
        Returns:
            bool: True if signal was processed and sent, False if filtered out
        """
        try:
            # Parse and normalize the signal data
            signal = self.parse_signal(raw_data)
            
            if not signal:
                logger.warning("Failed to parse signal data")
                return False
            
            # Apply filters
            if not self.should_process_signal(signal):
                logger.info(f"Signal filtered out: {signal.get('token')} - {signal.get('strategy')}")
                return False
            
            # Send to Telegram
            await self.telegram_bot.send_signal(signal)
            logger.info(f"Signal processed successfully: {signal.get('token')} - {signal.get('action')}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing signal: {e}")
            return False
    
    def parse_signal(self, raw_data: Dict) -> Optional[Dict]:
        """
        Parse raw webhook data into normalized signal format
        
        Expected TradingView webhook format:
        {
            "secret": "your_secret",
            "action": "BUY/SELL/LONG/SHORT", 
            "token": "BTCUSD",
            "strategy": "EMA_Cross",
            "price": "45000",
            "message": "Additional details",
            "exchange": "Binance",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        """
        try:
            # Handle different possible field names from TradingView
            signal = {
                'action': self._extract_field(raw_data, ['action', 'side', 'signal']),
                'token': self._extract_field(raw_data, ['token', 'symbol', 'ticker']),
                'strategy': self._extract_field(raw_data, ['strategy', 'indicator', 'source']),
                'price': self._extract_field(raw_data, ['price', 'close', 'current_price']),
                'exchange': self._extract_field(raw_data, ['exchange', 'market']),
                'message': self._extract_field(raw_data, ['message', 'comment', 'alert_message']),
                'timestamp': raw_data.get('timestamp', datetime.now().isoformat())
            }
            
            # Validate required fields
            if not signal['action'] or not signal['token']:
                logger.warning(f"Missing required fields in signal: {raw_data}")
                return None
            
            # Normalize action to uppercase
            signal['action'] = signal['action'].upper()
            
            # Clean up token symbol (remove exchange prefix if present)
            if signal['token']:
                signal['token'] = signal['token'].split(':')[-1]  # Remove exchange prefix like "BINANCE:BTCUSDT"
            
            return signal
            
        except Exception as e:
            logger.error(f"Error parsing signal: {e}")
            return None
    
    def _extract_field(self, data: Dict, possible_keys: list) -> Optional[str]:
        """Extract field value from data using multiple possible key names"""
        for key in possible_keys:
            if key in data and data[key] is not None:
                return str(data[key])
        return None
    
    def should_process_signal(self, signal: Dict) -> bool:
        """
        Apply filtering logic to determine if signal should be processed
        
        Args:
            signal: Normalized signal data
            
        Returns:
            bool: True if signal should be processed, False otherwise
        """
        # Check if token is in allowed list (if configured)
        if Config.ALLOWED_TOKENS:
            token = signal.get('token', '').upper()
            allowed_tokens_upper = [t.upper() for t in Config.ALLOWED_TOKENS if t.strip()]
            if token not in allowed_tokens_upper:
                logger.info(f"Token {token} not in allowed list: {allowed_tokens_upper}")
                return False
        
        # Check if strategy is in allowed list (if configured)
        if Config.ALLOWED_STRATEGIES:
            strategy = signal.get('strategy', '').upper()
            allowed_strategies_upper = [s.upper() for s in Config.ALLOWED_STRATEGIES if s.strip()]
            if strategy not in allowed_strategies_upper:
                logger.info(f"Strategy {strategy} not in allowed list: {allowed_strategies_upper}")
                return False
        
        # Validate action is supported
        valid_actions = ['BUY', 'SELL', 'LONG', 'SHORT']
        action = signal.get('action', '').upper()
        if action not in valid_actions:
            logger.warning(f"Invalid action: {action}")
            return False
        
        return True