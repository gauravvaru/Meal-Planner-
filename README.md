# AI Meal Planner

## Description

AI Meal Planner is an innovative web application that leverages artificial intelligence to generate personalized meal plans based on user input such as age, weight, height, and gender. The application also considers user-defined food preferences and allergies, offering a tailored culinary experience. It utilizes the Streamlit framework for a user-friendly interface and the Groq API for AI-powered meal suggestions.

## Features

-   **Personalized Meal Planning:** Generates daily meal plans (breakfast, lunch, dinner) based on individual caloric needs.
-   **User-Centric Input:** Accounts for age, weight, height, and gender for accurate BMR calculation.
-   **Dietary Customization:** Allows users to select food preferences and declare allergies.
-   **AI-Powered Suggestions:** Integrates with the Groq API to provide creative and diverse meal ideas.
-   **Unit Flexibility:** Supports both Metric (kg, cm) and Imperial (lb, ft + in) units.
-   **Interactive Interface:** Built with Streamlit for a rich and intuitive user experience.

## Demo

Experience the AI Meal Planner live: [https://meal-planner-gauravv.streamlit.app](https://meal-planner-gauravv.streamlit.app)

## How to Install and Run Locally

Follow these steps to set up and run the AI Meal Planner on your local machine:

### Prerequisites

-   Python 3.8+
-   `pip` (Python package installer)
-   A Groq API Key

### Installation

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/gauravvaru/Meal-Planner-.git
    cd Meal-Planner-
    ```

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    conda create -n meal-planner-env python=3.9 -y
    conda activate meal-planner-env
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Groq API Key:**

    Create a `.streamlit` directory in the root of your project if it doesn't exist:

    ```bash
    mkdir -p .streamlit
    ```

    Inside the `.streamlit` directory, create a file named `secrets.toml` and add your Groq API key:

    ```toml
    # .streamlit/secrets.toml
    GROQ_API_KEY="your_groq_api_key_here"
    ```

    Replace `"your_api_key_here"` with your actual Groq API Key.

### Running the Application

To run the Streamlit application, execute the following command in your terminal:

```bash
streamlit run streamlit_meal_planner.py
```

Your app will open in your default web browser at `http://localhost:8501`.

## Usage

1.  **Enter Your Details:** Fill in your name, age, weight, height, and gender.
2.  **Set Preferences (Optional):** Choose your food preferences and declare any allergies.
3.  **Generate Meal Plan:** Click the "Create a Basket" button to generate a personalized meal basket, then click "Generate Meal Plan" for AI-powered meal suggestions.

## Contributing

Contributions are welcome! If you have suggestions for improvements, new features, or bug fixes, please open an issue or submit a pull request.

## License

This project is open-source and available under the [MIT License](LICENSE).
