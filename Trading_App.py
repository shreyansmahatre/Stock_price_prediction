import streamlit as st

st.set_page_config(
    page_title="Trading App",
    page_icon="heavy_dollar_sign:",
    layout="wide"
)

st.title("Trading Guide App:bar_Chart:")

st.header("We provide the greatest platform for you to collect all information prior to investing in stocks.")

st.image("app.png")

st.markdown("## we provided the follwing Services:")

st.markdown("#### :one: stock Information ")
st.write ("Through this page,you can see all the information about a stock you want to know,including the stock price,company profile,financial statement and so on.")

st.markdown("#### :two: stock Prediction")
st.write ("You can explore predicted closing prices for the next 30 days based on historical stock data and advanced forcasting model.")

st.markdown("#### :three: CAPM Return ")
st.write ("Discover how the capital asset pricing model (CAPM) calculate the expected return of the different stocks asset based on its risk.")

st.markdown("#### :four: CAPM Beta")
st.write ("CAlculate beta and Expected return of a stock based on its historical price data and the market index.")