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
    position: relative; /* Needed for overlay */
    background-size: cover;
    background-position: center;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden; /* Ensures the overlay doesn't spill out */
}

.card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.4); /* Semi-transparent black overlay */
    z-index: 0; /* Place the overlay behind the content */
}

.card-title, .card-value {
    position: relative; /* Ensures text is above the overlay */
    z-index: 1; /* Place text above the overlay */
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
}

.card-title {
    font-size: 24px;
    font-weight: bold;
}

.card-value {
    font-size: 18px;
    margin-top: 10px;
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
