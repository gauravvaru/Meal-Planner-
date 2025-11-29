import streamlit as st
import pandas as pd
import requests 
import random
import time
from data import food_items_breakfast, food_items_lunch, food_items_dinner
from prompts import pre_prompt_b, pre_prompt_l, pre_prompt_d, pre_breakfast, pre_lunch, pre_dinner, end_text, \
    example_response_l, example_response_d, negative_prompt

UNITS_CM_TO_IN = 0.393701
UNITS_KG_TO_LB = 2.20462
UNITS_LB_TO_KG = 0.453592
UNITS_IN_TO_CM = 2.54

# Configure Groq API
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
    "Content-Type": "application/json"
}

# Disable SSL verification warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="AI - Meal Planner", page_icon="🍴", layout="wide")

st.markdown("<h1 style='text-align: center;'>AI Meal Planner 🍴</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Plan your meals efficiently and deliciously with AI!</p>", unsafe_allow_html=True)
st.markdown("---")

st.write("### Tell us about yourself:")

with st.container(border=True):
    name = st.text_input("Enter your name", placeholder="John Doe")
    age = st.number_input("Enter your age", min_value=1, max_value=120, step=1)

    unit_preference = st.radio("Preferred units:", ["Metric (kg, cm)", "Imperial (lb, ft + in)"], horizontal=True)

    col1, col2 = st.columns(2)
    if unit_preference == "Metric (kg, cm)":
        with col1:
            weight = st.number_input("Enter your weight (kg)", min_value=1.0, max_value=300.0, step=0.5)
        with col2:
            height = st.number_input("Enter your height (cm)", min_value=1.0, max_value=250.0, step=0.5)
    else:
        with col1:
            weight_lb = st.number_input("Enter your weight (lb)", min_value=1.0, max_value=600.0, step=1.0)
        with col2:
            height_ft = st.number_input("Enter your height (ft)", min_value=1, max_value=8, step=1)
            height_in = st.number_input("Enter your height (in)", min_value=0, max_value=11, step=1)

        weight = weight_lb * UNITS_LB_TO_KG
        height = (height_ft * 12 + height_in) * UNITS_IN_TO_CM

    gender = st.radio("Choose your gender:", ["Male", "Female"], horizontal=True)

example_response = f"Hello {name}! I'm thrilled to be your meal planner for the day, and I've crafted a delightful and flavorful meal plan just for you. But fear not, this isn't your ordinary, run-of-the-mill meal plan. It's a culinary adventure designed to keep your taste buds excited while considering the calories you can intake. So, get ready!"


def calculate_bmr(weight, height, age, gender):
    if gender == "Male":
        bmr = 9.99 * weight + 6.25 * height - 4.92 * age + 5
    else:
        bmr = 9.99 * weight + 6.25 * height - 4.92 * age - 161

    return bmr


def get_user_preferences():
    preferences = st.multiselect("Choose your food preferences:", list(food_items_breakfast.keys()))
    return preferences


def get_user_allergies():
    allergies = st.multiselect("Choose your food allergies:", list(food_items_breakfast.keys()))
    return allergies


def generate_items_list(target_calories, food_groups):
    calories = 0
    selected_items = []
    total_items = set()
    for foods in food_groups.values():
        total_items.update(foods.keys())

    while abs(calories - target_calories) >= 10 and len(selected_items) < len(total_items):
        group = random.choice(list(food_groups.keys()))
        foods = food_groups[group]
        item = random.choice(list(foods.keys()))

        if item not in selected_items:
            cals = foods[item]
            if calories + cals <= target_calories:
                selected_items.append(item)
                calories += cals

    return selected_items, calories


def knapsack(target_calories, food_groups):
    items = []
    for group, foods in food_groups.items():
        for item, calories in foods.items():
            items.append((calories, item))

    n = len(items)
    dp = [[0 for _ in range(target_calories + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(target_calories + 1):
            value, _ = items[i - 1]

            if value > j:
                dp[i][j] = dp[i - 1][j]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i - 1][j - value] + value)

    selected_items = []
    j = target_calories
    for i in range(n, 0, -1):
        if dp[i][j] != dp[i - 1][j]:
            _, item = items[i - 1]
            selected_items.append(item)
            j -= items[i - 1][0]

    return selected_items, dp[n][target_calories]


if name and age and weight and height and gender:
    bmr = calculate_bmr(weight, height, age, gender)
    round_bmr = round(bmr, 2)
    st.markdown("---")
    st.markdown(f"### Your Estimated Daily Calorie Needs:")
    st.info(f"Based on your input, your Basal Metabolic Rate (BMR) suggests you need approximately **{round_bmr} calories** per day to maintain your current weight.")

    st.markdown("---")
    choose_algo = "Knapsack" # Defaulting to Knapsack algorithm

    with st.expander("Optional: Food Preferences and Allergies"):
        user_preferences = get_user_preferences()
        user_allergies = get_user_allergies()

    if 'clicked' not in st.session_state:
        st.session_state.clicked = False
else:
    st.warning("Please fill in all your personal information to calculate your daily calorie needs and proceed with meal planning.")
    # Prevent further execution if information is incomplete
    st.stop()


def click_button():
    st.session_state.clicked = True


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "llama-3.3-70b-versatile"
    # st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.button("Create a Basket", on_click=click_button)
if st.session_state.clicked:
    calories_breakfast = round((bmr * 0.5), 2)
    calories_lunch = round((bmr * (1 / 3)), 2)
    calories_dinner = round((bmr * (1 / 6)), 2)

    if choose_algo == "Random Greedy":
        meal_items_morning, cal_m = generate_items_list(calories_breakfast, food_items_breakfast)
        meal_items_lunch, cal_l = generate_items_list(calories_lunch, food_items_lunch)
        meal_items_dinner, cal_d = generate_items_list(calories_dinner, food_items_dinner)

    else:
        meal_items_morning, cal_m = knapsack(int(calories_breakfast), food_items_breakfast)
        meal_items_lunch, cal_l = knapsack(int(calories_lunch), food_items_lunch)
        meal_items_dinner, cal_d = knapsack(int(calories_dinner), food_items_dinner)
    st.header("Your Personalized Meal Plan")
    col1, col2, col3 = st.columns(3)
    with st.container(border=True):
        st.markdown("### Your Meal Basket:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Morning Calories", value=f"{calories_breakfast} cal")
            st.dataframe(pd.DataFrame({"Morning": meal_items_morning}), use_container_width=True)
            st.write(f"Total Calories: **{cal_m}**")

        with col2:
            st.metric("Lunch Calories", value=f"{calories_lunch} cal")
            st.dataframe(pd.DataFrame({"Lunch": meal_items_lunch}), use_container_width=True)
            st.write(f"Total Calories: **{cal_l}**")

        with col3:
            st.metric("Dinner Calories", value=f"{calories_dinner} cal")
            st.dataframe(pd.DataFrame({"Dinner": meal_items_dinner}), use_container_width=True)
            st.write(f"Total Calories: **{cal_d}**")
    
    st.markdown("---")
    st.markdown("### AI-Generated Meal Plan:")

    if st.button("Generate Meal Plan", use_container_width=True):
        st.subheader("Breakfast")
        user_content = pre_prompt_b + str(meal_items_morning) + example_response + pre_breakfast + negative_prompt
        temp_messages = [{"role": "user", "content": user_content}]
        with st.chat_message("assistant"):
            full_response = ""
            with st.spinner("Generating breakfast ideas..."):
                response = requests.post(
                    GROQ_API_URL,
                    headers=HEADERS,
                    json={
                        "model": st.session_state["openai_model"],
                        "messages": temp_messages
                    },
                    verify=False
                )
                response_json = response.json()
                if "choices" in response_json:
                    full_response = response_json["choices"][0]["message"]["content"]
                    st.write(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response})

        st.markdown("---")
        st.subheader("Lunch")
        user_content = pre_prompt_l + str(meal_items_lunch) + example_response + pre_lunch + negative_prompt
        temp_messages = [{"role": "user", "content": user_content}]
        with st.chat_message("assistant"):
            full_response = ""
            with st.spinner("Generating lunch ideas..."):
                response = requests.post(
                    GROQ_API_URL,
                    headers=HEADERS,
                    json={
                        "model": st.session_state["openai_model"],
                        "messages": temp_messages
                    },
                    verify=False
                )
                response_json = response.json()
                if "choices" in response_json:
                    full_response = response_json["choices"][0]["message"]["content"]
                    st.write(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response})

        st.markdown("---")
        st.subheader("Dinner")
        user_content = pre_prompt_d + str(meal_items_dinner) + example_response + pre_dinner + negative_prompt
        temp_messages = [{"role": "user", "content": user_content}]
        with st.chat_message("assistant"):
            full_response = ""
            with st.spinner("Generating dinner ideas..."):
                response = requests.post(
                    GROQ_API_URL,
                    headers=HEADERS,
                    json={
                        "model": st.session_state["openai_model"],
                        "messages": temp_messages
                    },
                    verify=False
                )
                response_json = response.json()
                if "choices" in response_json:
                    full_response = response_json["choices"][0]["message"]["content"]
                    st.write(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response})
        st.markdown("---")
        st.success("Thank you for using our AI app! I hope you enjoyed your personalized meal plan!")

# Clean up existing custom CSS if it's no longer needed, assuming config.toml handles theming
# The original hide_streamlit_style block is removed as the new config.toml takes care of the theme.
# If specific custom CSS is still desired, it can be re-added or refined.
