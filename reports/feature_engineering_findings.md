# Feature Engineering Findings

## Data Cleaning

* The dataset contains no missing values.
* Customer identifiers (`nameOrig` and `nameDest`) were removed because they do not contribute to fraud prediction.

## Feature Encoding

* The transaction type column was converted from categorical values to numerical values using Label Encoding.

## Correlation Analysis

* Correlation analysis was performed to understand relationships between features.
* A heatmap was generated to visualize feature correlations.

## Machine Learning Preparation

* Feature matrix (X) and target variable (y) were separated.
* Train-test split was performed with an 80:20 ratio.
* The processed dataset was saved for model training.

## Key Observations

* No missing values were present in the dataset.
* Transaction type encoding allows machine learning models to process categorical information.
* The dataset is now ready for model development.

## Next Steps

* Train Random Forest model.
* Train XGBoost model.
* Train Isolation Forest model.
* Compare model performance.
