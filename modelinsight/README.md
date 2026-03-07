# ModelInsight

ModelInsight is a Machine Learning application that allows you to submit CSV datasets, automatically train multiple models, and visualize the results in interactive comparative dashboards.

The system analyzes the data submitted by the user, trains different Machine Learning algorithms, and selects the best model based on performance metrics.

---

## System Architecture

Frontend
↓ REST API (FastAPI)
↓ Machine Learning Pipeline
↓ Model Training and Evaluation
↓ Comparison Dashboard

The frontend communicates with the backend via REST API to send data and receive the results of model training.

---

## Technologies Used

### Backend
- Python
- FastAPI
- pandas
- NumPy
- scikit-learn

### Frontend
- HTML
- CSS
- JavaScript
- GSAP (animations)
- Chart.js (data visualization)

### Infrastructure
- Docker
- REST API

---

## Machine Learning Algorithms

The system automatically trains multiple models:

- Linear Regression
- Random Forest
- Support Vector Machine (SVM)
- Logistic Regression
- Naive Bayes
- Gradient Boosting

---

## Machine Learning Techniques Used

The project uses several important techniques to improve model performance:

- K-Fold Cross Validation
- GridSearchCV for hyperparameter optimization
- Feature Scaling
- Automatic selection of the best model

---

## Evaluation Metrics

Depending on the type of Problem, the system can use:

- Mean Squared Error (MSE)
- R² Score
- Recall
- Precision
- Confusion Matrix

---

## Features

- CSV file upload
- Automatic data processing
- Training of multiple models
- Comparison between predictions and real data
- Interactive dashboard
- Visualization of performance metrics
- Automatic selection of the best model

---

## Project Structure

modelinsight
│
├── backend
│ ├── main.py
│ ├── routes
│ ├── services
│ ├── models
│ ├── ml
│ │ ├── training.py
│ │ ├── evaluation.py
│ │ └── preprocessing.py
│
├── frontend
│ ├── index.html
│ ├── css
│ ├── js
│ └── dashboard
│
├── date
│ ├── uploads
│ └── processed
│
├── docker
│ ├── Dockerfile
│ └── docker-compose.yml
│
└── README.md

---

## Workflow

1. User submits a CSV file
2. The backend processes the data
3. The Machine Learning pipeline prepares the data
4. Different models are trained
5. GridSearchCV optimizes the parameters
6. The best model is selected
7. The results are sent to the frontend
8. The dashboard displays comparative graphs

---

## Project Objective

The objective of ModelInsight is to demonstrate the integration between:

- Machine Learning
- Software Engineering
- APIs
- Data Visualization

This project simulates a real-world application where users can analyze data and compare predictive models in a simple way.

---

## Possible Future Improvements

- Support for multiple datasets
- Persistence of trained models
- User authentication
- Database storage
- Cloud deployment

---

## License

Educational project for the study of Machine Learning and API development.