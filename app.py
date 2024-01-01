import streamlit as st
import pandas as pd
from trading_simulation import bkproject
import altair as alt

st.title('BK Project')

col1,col2 = st.columns([1,3])
# 공간을 2:3 으로 분할하여 col1과 col2라는 이름을 가진 컬럼 생성

def get_chart(data, asset_amount_krw):
        hover = alt.selection_single(
            fields=["date"],
            nearest=True,
            on="mouseover",
            empty="none",
        )

        lines = (
            alt.Chart(data, title="assets")
            .mark_line()
            .encode(
                x="date",
                y="asset"
            )
        )

        # Draw points on the line, and highlight based on selection
        points = lines.transform_filter(hover).mark_circle(size=65)

        # Draw a rule at the location of the selection
        tooltips = (
            alt.Chart(data)
            .mark_rule()
            .encode(
                x="date",
                y="asset",
                opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                tooltip=[
                    alt.Tooltip("date", title="Date"),
                    alt.Tooltip("asset", title="Asset(KRW)"),
                ],
            )
            .add_selection(hover)
        )
        #min_asset_value = asset_amount_krw*0.9  # Replace with your desired minimum value
        #lines.encoding.y.scale = alt.Scale(domain=[min_asset_value, 'auto'])

        return (lines + points + tooltips).interactive()

with col1 :
  # column 1 에 담을 내용
  st.write('선택사항')

    #asset_amount_krw, buy_threshold, sell_threshold, buy_ratio, sell_ratio, ticker, start_date, end_date, country

  asset_amount_krw = st.number_input('투입 자산을 입력하세요(원)', value=100000000, key = 'asset_amount_krw')
  buy_threshold = st.number_input('매수 기준점(%)', value=0.65, key = 'buy_threshold')
  sell_threshold = st.number_input('매도 기준점(%)', value=1.25, key = 'sell_threshold')

  buy_ratio = st.number_input('매수 비중(%)', value=15, key = 'buy_ratio')
  sell_ratio = st.number_input('매도 비중(%)', value=15, key = 'sell_ratio')

  ticker = st.text_input('티커(예: QQQ, 005930)', value='QQQ', key='ticker')
  start_date = st.text_input('시작 날짜(예: 2023-01-01)', value='2023-01-01', key= 'start_date')
  end_date = st.text_input('끝 날짜(예: 2023-12-31)', value='2023-12-31', key= 'end_date')
  country = st.text_input('국가 (US/KR 중 적으세요)', value = 'US', key= 'country')

  
with col2 :
  # column 2 에 담을 내용
  #st.write('결과')
  if st.button('Calculate'):
    # Call bkproject with the input values
    asset_amounts, actions, closing_prices_krw = bkproject(asset_amount_krw,  buy_threshold/100, sell_threshold/100, buy_ratio/100, sell_ratio/100, ticker, start_date, end_date, country)
    asset_df = pd.DataFrame({'date': closing_prices_krw.Date, 'asset': asset_amounts})
    asset_df['pct_change'] = (asset_df['asset'] / asset_df['asset'].iloc[0] - 1)*100
    # st.line_chart(asset_df.set_index('date')['asset'], height=400, use_container_width=True)
    st.write("최종 결과")
    st.write("마지막 날짜 : ", asset_df.iloc[-1]['date'])
    st.write("자산 : ", round(asset_df.iloc[-1]['asset'],2), "원")
    st.write("수익률 : ", round(asset_df.iloc[-1]['pct_change'],2), "%")
    
    chart = get_chart(asset_df, asset_amount_krw)
    st.altair_chart(chart.interactive(),use_container_width=True)


    # Set the minimum value for the y-axis
    #min_asset_value = 100  # Replace with your desired minimum value
    #chart.encoding.y.scale = alt.Scale(domain=[min_asset_value, 'auto'])

  #st.checkbox('this is checkbox1 in col2 ')


# 탭 생성 : 첫번째 탭의 이름은 Tab A 로, Tab B로 표시합니다. 
    tab1, tab2= st.tabs(['Actions' , 'Amount'])

    with tab1:
        st.write('actions')
        
        st.write(pd.DataFrame(actions))
        
    with tab2:
        st.write('amount')
        #asset_df['pct_change'] = (asset_df['asset'] / asset_df['asset'].iloc[0] - 1)*100
        #st.write(asset_df.iloc[-1])
        st.write(asset_df)
