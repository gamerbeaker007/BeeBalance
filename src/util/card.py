import streamlit as st

# Define custom CSS for cards
card_style = """
<style>
.card {
    border-radius: 15px;
    padding: 20px;
    margin: 10px;
    width: 300px;
    height: 150px;
    color: white;
    background-size: cover;
    background-position: center;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.card-title {
    font-size: 24px;
    font-weight: bold;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
}
.card-value {
    font-size: 18px;
    margin-top: 10px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
}
</style>
"""


def create_card(title, value, image_url):
    return f"""
    <div class="card" style="background-image: url('{image_url}');">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
    </div>
    """
