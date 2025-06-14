"""
Machine Learning Pipeline Example
Demonstrates common ML engineering patterns and potential issues
for comprehensive code review testing.
"""

import json
import logging
import os
import pickle
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

# ISSUE: Hardcoded configuration values
MODEL_VERSION = "1.0.0"
DATA_PATH = "/tmp/ml_data"
MODEL_PATH = "/tmp/ml_models"
RANDOM_SEED = 42  # ISSUE: Fixed seed may not be appropriate for all scenarios


@dataclass
class ModelMetadata:
    model_name: str
    version: str
    training_date: str
    accuracy: float
    feature_columns: List[str]
    target_column: str
    preprocessing_steps: List[str]


class DataLoader:
    """Data loading and basic preprocessing"""

    def __init__(self, data_source: str):
        self.data_source = data_source
        # ISSUE: No validation of data source

    def load_data(self) -> pd.DataFrame:
        """Load data from various sources"""
        try:
            if self.data_source.endswith(".csv"):
                # ISSUE: No encoding specification
                df = pd.read_csv(self.data_source)
            elif self.data_source.endswith(".json"):
                # ISSUE: No handling of large JSON files
                df = pd.read_json(self.data_source)
            else:
                # ISSUE: Limited file format support
                raise ValueError(f"Unsupported file format: {self.data_source}")

            # ISSUE: No data validation after loading
            return df

        except Exception as e:
            # ISSUE: Generic exception handling
            logging.error(f"Failed to load data: {e}")
            raise

    def basic_cleaning(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic data cleaning operations"""

        # ISSUE: Hardcoded cleaning strategies
        # Remove rows with any missing values
        df_clean = df.dropna()

        # ISSUE: No logging of data loss
        rows_removed = len(df) - len(df_clean)

        # ISSUE: Remove duplicates without considering business logic
        df_clean = df_clean.drop_duplicates()

        # ISSUE: No outlier detection or handling
        return df_clean


class FeatureEngineer:
    """Feature engineering and preprocessing"""

    def __init__(self):
        self.scalers = {}  # ISSUE: Not thread-safe
        self.encoders = {}
        self.feature_names = []

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create new features from existing data"""

        df_features = df.copy()

        # ISSUE: Hardcoded feature engineering rules
        if "age" in df.columns:
            # Create age groups
            df_features["age_group"] = pd.cut(
                df["age"],
                bins=[0, 18, 35, 50, 65, 100],
                labels=["young", "adult", "middle_age", "senior", "elderly"],
            )

        if "income" in df.columns and "expenses" in df.columns:
            # ISSUE: No handling of division by zero
            df_features["savings_rate"] = (df["income"] - df["expenses"]) / df["income"]

        # ISSUE: No feature validation or sanity checks
        return df_features

    def encode_categorical_features(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Encode categorical features"""

        df_encoded = df.copy()
        categorical_columns = df.select_dtypes(include=["object"]).columns

        for column in categorical_columns:
            if fit:
                # ISSUE: No handling of unseen categories during inference
                encoder = LabelEncoder()
                df_encoded[column] = encoder.fit_transform(df[column])
                self.encoders[column] = encoder
            else:
                if column in self.encoders:
                    try:
                        df_encoded[column] = self.encoders[column].transform(df[column])
                    except ValueError as e:
                        # ISSUE: Poor handling of unseen categories
                        logging.warning(f"Unseen category in {column}: {e}")
                        df_encoded[column] = 0  # Default to 0

        return df_encoded

    def scale_features(self, df: pd.DataFrame, target_column: str, fit: bool = True) -> pd.DataFrame:
        """Scale numerical features"""

        df_scaled = df.copy()
        numerical_columns = df.select_dtypes(include=[np.number]).columns
        feature_columns = [col for col in numerical_columns if col != target_column]

        if fit:
            scaler = StandardScaler()
            df_scaled[feature_columns] = scaler.fit_transform(df[feature_columns])
            self.scalers["standard"] = scaler
        else:
            if "standard" in self.scalers:
                df_scaled[feature_columns] = self.scalers["standard"].transform(df[feature_columns])

        return df_scaled


class ModelTrainer:
    """Model training and evaluation"""

    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.model = None
        self.metadata = None
        # ISSUE: Limited model type support

    def train_model(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
    ) -> Dict[str, Any]:
        """Train the model"""

        # ISSUE: Hardcoded hyperparameters
        if self.model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=RANDOM_SEED,
                # ISSUE: No hyperparameter tuning
                max_depth=10,
                min_samples_split=5,
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

        # ISSUE: No cross-validation
        self.model.fit(X_train, y_train)

        # Evaluate on validation set
        val_predictions = self.model.predict(X_val)
        val_score = self.model.score(X_val, y_val)

        # ISSUE: Limited evaluation metrics
        results = {
            "validation_accuracy": val_score,
            "feature_importance": dict(zip(X_train.columns, self.model.feature_importances_)),
            "classification_report": classification_report(y_val, val_predictions, output_dict=True),
        }

        return results

    def save_model(self, model_path: str, metadata: ModelMetadata):
        """Save trained model and metadata"""

        # ISSUE: No model versioning strategy
        os.makedirs(model_path, exist_ok=True)

        # Save model
        model_file = os.path.join(model_path, "model.pkl")
        # ISSUE: Using pickle for model serialization (security risk)
        with open(model_file, "wb") as f:
            pickle.dump(self.model, f)

        # Save metadata
        metadata_file = os.path.join(model_path, "metadata.json")
        with open(metadata_file, "w") as f:
            # ISSUE: No proper serialization of complex objects
            json.dump(metadata.__dict__, f, indent=2, default=str)

        logging.info(f"Model saved to {model_path}")


class ModelPredictor:
    """Model inference and prediction"""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.metadata = None
        self.feature_engineer = None
        # ISSUE: No model warming or initialization checks

    def load_model(self):
        """Load model and metadata"""

        model_file = os.path.join(self.model_path, "model.pkl")
        metadata_file = os.path.join(self.model_path, "metadata.json")

        # ISSUE: No error handling for missing files
        with open(model_file, "rb") as f:
            # ISSUE: Security risk - loading pickle files
            self.model = pickle.load(f)

        with open(metadata_file, "r") as f:
            metadata_dict = json.load(f)
            self.metadata = ModelMetadata(**metadata_dict)

        # ISSUE: FeatureEngineer not properly reloaded
        self.feature_engineer = FeatureEngineer()

    def predict(self, input_data: pd.DataFrame) -> Dict[str, Any]:
        """Make predictions on new data"""

        if self.model is None:
            self.load_model()

        try:
            # ISSUE: No input validation
            # ISSUE: Feature engineering pipeline not properly applied
            processed_data = self.feature_engineer.encode_categorical_features(input_data, fit=False)
            processed_data = self.feature_engineer.scale_features(processed_data, self.metadata.target_column, fit=False)

            # ISSUE: No handling of missing features
            predictions = self.model.predict(processed_data[self.metadata.feature_columns])
            probabilities = self.model.predict_proba(processed_data[self.metadata.feature_columns])

            return {
                "predictions": predictions.tolist(),
                "probabilities": probabilities.tolist(),
                "model_version": self.metadata.version,
                "prediction_timestamp": pd.Timestamp.now().isoformat(),
            }

        except Exception as e:
            # ISSUE: Generic error handling
            logging.error(f"Prediction failed: {e}")
            raise


class MLPipeline:
    """Complete ML pipeline orchestration"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_loader = None
        self.feature_engineer = None
        self.model_trainer = None
        # ISSUE: No configuration validation

    def run_training_pipeline(self, data_source: str, target_column: str) -> ModelMetadata:
        """Run the complete training pipeline"""

        logging.info("Starting ML training pipeline...")

        # Load data
        self.data_loader = DataLoader(data_source)
        df = self.data_loader.load_data()
        df_clean = self.data_loader.basic_cleaning(df)

        # ISSUE: No data quality checks
        logging.info(f"Loaded {len(df_clean)} samples with {len(df_clean.columns)} features")

        # Feature engineering
        self.feature_engineer = FeatureEngineer()
        df_features = self.feature_engineer.create_features(df_clean)
        df_encoded = self.feature_engineer.encode_categorical_features(df_features)
        df_scaled = self.feature_engineer.scale_features(df_encoded, target_column)

        # Prepare training data
        feature_columns = [col for col in df_scaled.columns if col != target_column]
        X = df_scaled[feature_columns]
        y = df_scaled[target_column]

        # ISSUE: Fixed train-test split ratio
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y)

        # Train model
        self.model_trainer = ModelTrainer(self.config.get("model_type", "random_forest"))
        training_results = self.model_trainer.train_model(X_train, y_train, X_val, y_val)

        # Create metadata
        metadata = ModelMetadata(
            model_name=self.config.get("model_name", "default_model"),
            version=MODEL_VERSION,
            training_date=pd.Timestamp.now().isoformat(),
            accuracy=training_results["validation_accuracy"],
            feature_columns=feature_columns,
            target_column=target_column,
            preprocessing_steps=[
                "cleaning",
                "feature_engineering",
                "encoding",
                "scaling",
            ],
        )

        # Save model
        model_path = os.path.join(MODEL_PATH, metadata.model_name)
        self.model_trainer.save_model(model_path, metadata)

        logging.info(f"Training completed. Validation accuracy: {metadata.accuracy:.3f}")
        return metadata

    def run_batch_prediction(self, data_source: str, model_name: str, output_path: str) -> None:
        """Run batch predictions"""

        logging.info("Starting batch prediction pipeline...")

        # Load data
        data_loader = DataLoader(data_source)
        df = data_loader.load_data()

        # Load model and predict
        model_path = os.path.join(MODEL_PATH, model_name)
        predictor = ModelPredictor(model_path)
        results = predictor.predict(df)

        # ISSUE: No output format validation
        # Save results
        output_df = df.copy()
        output_df["predictions"] = results["predictions"]
        output_df["prediction_timestamp"] = results["prediction_timestamp"]

        # ISSUE: Hardcoded output format
        output_df.to_csv(output_path, index=False)
        logging.info(f"Predictions saved to {output_path}")


# ISSUE: Global configuration
PIPELINE_CONFIG = {
    "model_name": "customer_churn_model",
    "model_type": "random_forest",
    "data_validation": False,  # ISSUE: Data validation disabled
    "feature_selection": False,  # ISSUE: No automatic feature selection
    "hyperparameter_tuning": False,  # ISSUE: No hyperparameter optimization
}


def create_sample_data():
    """Create sample data for testing"""
    # ISSUE: Hardcoded sample data generation
    np.random.seed(RANDOM_SEED)

    n_samples = 1000
    data = {
        "age": np.random.randint(18, 80, n_samples),
        "income": np.random.normal(50000, 20000, n_samples),
        "expenses": np.random.normal(30000, 15000, n_samples),
        "account_length": np.random.randint(1, 120, n_samples),
        "customer_service_calls": np.random.poisson(2, n_samples),
        "plan_type": np.random.choice(["basic", "premium", "enterprise"], n_samples),
        "churn": np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
    }

    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    # ISSUE: No proper logging configuration
    logging.basicConfig(level=logging.INFO)

    # Create sample data
    sample_df = create_sample_data()
    data_file = "/tmp/sample_customer_data.csv"
    sample_df.to_csv(data_file, index=False)

    # ISSUE: Hardcoded paths and configuration
    os.makedirs(MODEL_PATH, exist_ok=True)

    # Run training pipeline
    pipeline = MLPipeline(PIPELINE_CONFIG)

    try:
        metadata = pipeline.run_training_pipeline(data_file, "churn")
        print(f"Model training completed: {metadata.model_name}")
        print(f"Validation accuracy: {metadata.accuracy:.3f}")

        # Test prediction
        test_data = sample_df.head(10).drop("churn", axis=1)
        predictor = ModelPredictor(os.path.join(MODEL_PATH, metadata.model_name))
        predictions = predictor.predict(test_data)
        print(f"Sample predictions: {predictions['predictions'][:5]}")

    except Exception as e:
        # ISSUE: Generic exception handling at top level
        logging.error(f"Pipeline execution failed: {e}")
        raise

    # ISSUE: No cleanup of temporary files
    print("ML Pipeline execution completed!")
