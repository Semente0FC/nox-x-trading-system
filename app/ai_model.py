import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
import logging
from typing import Dict, List, Tuple, Optional
import os
from datetime import datetime

class AIModel:
    def __init__(self, config: dict):
        """Initialize AI model with configuration"""
        self.config = config['ai']
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.scaler = MinMaxScaler()
        self.feature_columns = self.config['features']
        self.sequence_length = self.config['input_sequence_length']
        self.model_version = 0
        self.initialize_model()

    def initialize_model(self):
        """Create or load the LSTM model"""
        try:
            # Try to load existing model
            model_path = f"app/models/lstm_model_v{self.model_version}.h5"
            if os.path.exists(model_path):
                self.model = load_model(model_path)
                self.logger.info(f"Loaded existing model: {model_path}")
            else:
                self._create_new_model()
                self.logger.info("Created new LSTM model")
        except Exception as e:
            self.logger.error(f"Error initializing model: {str(e)}")
            self._create_new_model()

    def _create_new_model(self):
        """Create a new LSTM model architecture"""
        try:
            self.model = Sequential([
                LSTM(units=50, return_sequences=True, 
                     input_shape=(self.sequence_length, len(self.feature_columns))),
                Dropout(0.2),
                LSTM(units=50, return_sequences=True),
                Dropout(0.2),
                LSTM(units=50),
                Dropout(0.2),
                Dense(units=32, activation='relu'),
                Dense(units=3, activation='softmax')  # 3 classes: buy, sell, hold
            ])

            self.model.compile(
                optimizer=Adam(learning_rate=self.config['training']['learning_rate']),
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
        except Exception as e:
            self.logger.error(f"Error creating model: {str(e)}")
            raise

    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for training or prediction"""
        try:
            # Ensure all required features are present
            missing_features = set(self.feature_columns) - set(df.columns)
            if missing_features:
                raise ValueError(f"Missing features: {missing_features}")

            # Extract features and scale them
            features = df[self.feature_columns].values
            scaled_features = self.scaler.fit_transform(features)

            # Create sequences
            X, y = [], []
            for i in range(len(scaled_features) - self.sequence_length):
                X.append(scaled_features[i:(i + self.sequence_length)])
                
                # Create target (next candle's direction)
                next_close = df['close'].iloc[i + self.sequence_length]
                current_close = df['close'].iloc[i + self.sequence_length - 1]
                
                if next_close > current_close * 1.001:  # 0.1% threshold for buy
                    target = [1, 0, 0]  # buy
                elif next_close < current_close * 0.999:  # -0.1% threshold for sell
                    target = [0, 1, 0]  # sell
                else:
                    target = [0, 0, 1]  # hold
                    
                y.append(target)

            return np.array(X), np.array(y)

        except Exception as e:
            self.logger.error(f"Error preparing data: {str(e)}")
            raise

    def train(self, df: pd.DataFrame, save_model: bool = True) -> Dict:
        """Train the model with new data"""
        try:
            X, y = self.prepare_data(df)
            
            if len(X) == 0:
                raise ValueError("No training data available")

            # Split into training and validation sets
            split_idx = int(len(X) * (1 - self.config['training']['validation_split']))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]

            # Train the model
            history = self.model.fit(
                X_train, y_train,
                batch_size=self.config['training']['batch_size'],
                epochs=self.config['training']['epochs'],
                validation_data=(X_val, y_val),
                verbose=0
            )

            # Save the model if requested
            if save_model:
                self.save_model()

            # Return training metrics
            return {
                'train_loss': history.history['loss'][-1],
                'train_accuracy': history.history['accuracy'][-1],
                'val_loss': history.history['val_loss'][-1],
                'val_accuracy': history.history['val_accuracy'][-1]
            }

        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}")
            raise

    def predict(self, df: pd.DataFrame) -> List[Dict]:
        """Generate predictions for the given data"""
        try:
            # Prepare the most recent sequence
            X, _ = self.prepare_data(df)
            if len(X) == 0:
                raise ValueError("Insufficient data for prediction")

            # Get the last sequence
            last_sequence = X[-1:]

            # Generate prediction
            prediction = self.model.predict(last_sequence, verbose=0)[0]
            
            # Convert prediction to trading signal
            signal_strength = max(prediction)
            signal_index = np.argmax(prediction)
            
            signals = ['BUY', 'SELL', 'HOLD']
            signal = signals[signal_index]

            return {
                'signal': signal,
                'confidence': float(signal_strength),
                'probabilities': {
                    'buy': float(prediction[0]),
                    'sell': float(prediction[1]),
                    'hold': float(prediction[2])
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error generating prediction: {str(e)}")
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'probabilities': {'buy': 0.0, 'sell': 0.0, 'hold': 1.0},
                'timestamp': datetime.now().isoformat()
            }

    def save_model(self):
        """Save the current model"""
        try:
            self.model_version += 1
            model_path = f"app/models/lstm_model_v{self.model_version}.h5"
            self.model.save(model_path)
            
            # Save scaler state
            scaler_path = f"app/models/scaler_v{self.model_version}.npy"
            np.save(scaler_path, self.scaler.scale_)
            
            self.logger.info(f"Model saved: {model_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            raise

    def load_specific_version(self, version: int):
        """Load a specific version of the model"""
        try:
            model_path = f"app/models/lstm_model_v{version}.h5"
            scaler_path = f"app/models/scaler_v{version}.npy"
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model version {version} not found")
                
            self.model = load_model(model_path)
            self.scaler.scale_ = np.load(scaler_path)
            self.model_version = version
            
            self.logger.info(f"Loaded model version {version}")
            
        except Exception as e:
            self.logger.error(f"Error loading model version {version}: {str(e)}")
            raise

    def online_update(self, new_data: pd.DataFrame) -> Dict:
        """Update the model with new data (online learning)"""
        try:
            X, y = self.prepare_data(new_data)
            
            if len(X) == 0:
                raise ValueError("Insufficient data for online update")

            # Perform a single epoch update
            history = self.model.fit(
                X, y,
                batch_size=min(len(X), self.config['training']['batch_size']),
                epochs=1,
                verbose=0
            )

            return {
                'loss': history.history['loss'][-1],
                'accuracy': history.history['accuracy'][-1]
            }

        except Exception as e:
            self.logger.error(f"Error in online update: {str(e)}")
            return {'loss': None, 'accuracy': None}
