import pytest
import json
from unittest.mock import AsyncMock, patch
from signal_processor import SignalProcessor

@pytest.fixture
def signal_processor():
    return SignalProcessor()

@pytest.fixture
def sample_tradingview_webhook():
    return {
        "secret": "test_secret",
        "action": "BUY",
        "token": "BTCUSD",
        "strategy": "EMA_Cross",
        "price": "45000",
        "exchange": "Binance",
        "message": "EMA crossover detected",
        "timestamp": "2025-01-01T12:00:00Z"
    }

class TestSignalProcessor:
    
    def test_parse_signal_valid_data(self, signal_processor, sample_tradingview_webhook):
        """Test parsing valid TradingView webhook data"""
        result = signal_processor.parse_signal(sample_tradingview_webhook)
        
        assert result is not None
        assert result['action'] == 'BUY'
        assert result['token'] == 'BTCUSD'
        assert result['strategy'] == 'EMA_Cross'
        assert result['price'] == '45000'
    
    def test_parse_signal_with_exchange_prefix(self, signal_processor):
        """Test parsing signal with exchange prefix in token"""
        data = {
            "action": "SELL",
            "token": "BINANCE:BTCUSDT",
            "strategy": "RSI"
        }
        
        result = signal_processor.parse_signal(data)
        
        assert result is not None
        assert result['token'] == 'BTCUSDT'  # Exchange prefix removed
    
    def test_parse_signal_missing_required_fields(self, signal_processor):
        """Test parsing with missing required fields"""
        data = {
            "strategy": "EMA_Cross",
            "price": "45000"
            # Missing action and token
        }
        
        result = signal_processor.parse_signal(data)
        
        assert result is None
    
    @patch('signal_processor.Config')
    def test_should_process_signal_allowed_tokens(self, mock_config, signal_processor):
        """Test token filtering"""
        mock_config.ALLOWED_TOKENS = ['BTCUSD', 'ETHUSD']
        mock_config.ALLOWED_STRATEGIES = []
        
        signal = {'action': 'BUY', 'token': 'BTCUSD', 'strategy': 'EMA'}
        assert signal_processor.should_process_signal(signal) == True
        
        signal = {'action': 'BUY', 'token': 'ADAUSD', 'strategy': 'EMA'}
        assert signal_processor.should_process_signal(signal) == False
    
    @patch('signal_processor.Config')
    def test_should_process_signal_allowed_strategies(self, mock_config, signal_processor):
        """Test strategy filtering"""
        mock_config.ALLOWED_TOKENS = []
        mock_config.ALLOWED_STRATEGIES = ['EMA_Cross', 'RSI_Divergence']
        
        signal = {'action': 'BUY', 'token': 'BTCUSD', 'strategy': 'EMA_Cross'}
        assert signal_processor.should_process_signal(signal) == True
        
        signal = {'action': 'BUY', 'token': 'BTCUSD', 'strategy': 'MACD'}
        assert signal_processor.should_process_signal(signal) == False
    
    def test_should_process_signal_invalid_action(self, signal_processor):
        """Test invalid action filtering"""
        signal = {'action': 'INVALID', 'token': 'BTCUSD', 'strategy': 'EMA'}
        assert signal_processor.should_process_signal(signal) == False
        
        signal = {'action': 'BUY', 'token': 'BTCUSD', 'strategy': 'EMA'}
        assert signal_processor.should_process_signal(signal) == True

if __name__ == "__main__":
    pytest.main([__file__])