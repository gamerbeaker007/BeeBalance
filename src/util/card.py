# Define custom CSS for cards
card_style = """
<style>
.card-container {
    display: flex;
    flex-wrap: wrap; /* Allows cards to move to the next row */
    justify-content: center; /* Centers the cards */
    gap: 15px; /* Adds space between cards */
    padding: 10px;
}

.card {
    border-radius: 15px;
    padding: 20px;
    padding-top: 10px;
    margin: 10px;
    width: 200px;
    height: 100px;
    color: white;
    position: relative;
    background-size: cover;
    background-position: center;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
    justify-content: start;
    overflow: hidden;
    flex: 1 1 calc(33.333% - 20px); /* Allows flexible resizing */
}

.card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.4);
    z-index: 0;
}

.card-title, .card-value {
    position: relative;
    z-index: 1;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
}

.card-title {
    font-size: 16px;
    font-weight: bold;
}

.card-value {
    font-size: 13px;
    padding-top: 10px;
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
