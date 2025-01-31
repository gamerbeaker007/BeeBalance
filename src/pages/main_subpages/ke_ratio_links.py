import streamlit as st

posts = [
    {
        "title": "New Splinterlands Contest & KE Indicator Guide",
        "summary": "This post introduces a new Splinterlands contest, explaining the KE Indicator—a metric for assessing player engagement and knowledge. It provides strategies to improve KE scores and details the contest rules.",
        "url": "https://peakd.com/@libertycrypto27/new-splinterlands-contest-rules-ke-indicator-what-it-is-how-to-improve-it-engita-835",
        "thumbnail": "https://images.hive.blog/0x0/https://files.peakd.com/file/peakd-hive/libertycrypto27/23uR1ARfnpLNq1Pb2fwjzPW2UxpTVDkz5frNkUT7YTPkvvsBBBpx456nLCPnqaoxNuwya.png"
    },
    {
        "title": "Understand KE Ratio and New Splinterlands Challenge Rules",
        "summary": "This post explores the application of the KE-Ratio within Splinterlands and discusses recent changes in the game's challenge rules to enhance community engagement and fair competition.",
        "url": "https://peakd.com/hive-13323/@underlock/understand-ke-ratio-and-new-splinterlands-challenge-rules",
        "thumbnail": "https://images.hive.blog/0x0/https://files.peakd.com/file/peakd-hive/underlock/23tm7JzLFRiCcgMLp5qXYtYYrVWQ9btMLuD9xAwmcnD5bWfQvziUYd6hhFqNTyZ1bs9KG.png"  # Replace with actual thumbnail URL
    },
    {
        "title": "KE-Ratio as a Guide",
        "summary": "The KE-Ratio is introduced as a metric to assess Hive users' investment behavior, distinguishing between long-term investors and potential extractors within the ecosystem.",
        "url": "https://peakd.com/@azircon/ke-ratio-as-a-guide",
        "thumbnail": "https://images.hive.blog/0x0/https://files.peakd.com/file/peakd-hive/zord189/Zcxlm2md-azircon.gif"  # Replace with actual thumbnail URL
    },
    {
        "title": "Bee Kind, Bee Honest, Bee Hive: Acting Right on the Blockchain",
        "summary": "This article emphasizes the importance of ethical behavior within the Hive blockchain community, advocating for kindness, honesty, and active participation to foster a positive environment.",
        "url": "https://peakd.com/hive-13323/@beaker007/bee-kind-bee-honest-bee-hive-acting-right-on-the-blockchain#@captaindingus/re-beaker007-sqwdq1",
        "thumbnail": "https://images.hive.blog/0x0/https://files.peakd.com/file/peakd-hive/beaker007/23vsWgnyTQ1jvgs6u2dJjifiMhDiaWGPDdJMGtKeCGWo2jCUKApVgXbRQajEpWm8PxE7n.png"
    },

]

def get_page():
    for post in posts:
        with st.container():
            col1, col2 = st.columns([1, 5])

            with col1:
                st.image(post["thumbnail"], width=300)

            with col2:
                st.subheader(post["title"])
                st.write(post["summary"])
                st.markdown(f"[Read more]({post['url']})", unsafe_allow_html=True)

        st.markdown("<hr style='border:1px solid #ccc'>", unsafe_allow_html=True)
