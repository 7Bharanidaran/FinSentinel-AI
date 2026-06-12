# Exploratory Data Analysis Findings

## Dataset Overview

* Dataset contains 6,362,620 transactions.
* Total number of features: 11.
* No missing values were observed.

## Fraud Distribution

* Fraud transactions represent a very small percentage of the dataset.
* The dataset is highly imbalanced.

## Transaction Types

The dataset contains the following transaction categories:

* CASH_IN
* CASH_OUT
* PAYMENT
* TRANSFER
* DEBIT

Among these, fraudulent activity is primarily associated with:

* CASH_OUT
* TRANSFER

## Key Observations

* Most transactions are legitimate.
* Fraudulent transactions are rare compared to normal transactions.
* Transaction amount distributions are highly skewed.
* Feature relationships can be analyzed further using correlation analysis.
* Additional feature engineering will be required before model development.

## Next Steps

* Data cleaning
* Feature engineering
* Encoding categorical variables
* Feature selection
* Train-test split
* Machine learning model development
