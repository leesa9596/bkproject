#pip install -U finance-datareader
import FinanceDataReader as fdr
import pandas as pd
# #df = pdr.get_data_yahoo("005930.KS", "2022-02-21", "2022-02-22")
# pip install yfinance
 
# from pandas_datareader import data as pdr
#price = pdr.get_data_yahoo("QQQ","2023-12-10","2023-12-16")

# import yfinance as yf
# yf.pdr_override()
# yf.download('QQQ','2023-12-10','2023-12-16')

def get_price(ticker, start_date, end_date):
    price = fdr.DataReader(ticker, start_date, end_date).reset_index()
    price['PctChange'] = -1 +price.Close/price.Close.shift(1)
    price.dropna(inplace=True)
    return price

#get_price('005930',"2023-12-10", "2023-12-16")[['Date','Close','PctChange']]

def get_exchage_rate_daily(start_date, end_date):
    exchange_rate_daily = fdr.DataReader('USD/KRW', start_date, end_date).reset_index()
    return exchange_rate_daily

def calculate_investment_amount(asset_amount_krw, qqq_closing_price_usd, exchange_rate):
    return asset_amount_krw / exchange_rate * qqq_closing_price_usd

def simulate_trading(asset_amount_krw, qqq_closing_prices_krw, buy_threshold, sell_threshold, buy_ratio, sell_ratio):
    #asset_amounts = [asset_amount_krw] * len(qqq_closing_prices_krw) #자산액 변화, 매수할 때에는 변화가 없고 매도할 경우에만 추가되어야 한다.
    asset_amounts = [asset_amount_krw]
    total_investment = 0     #현재 투입되어있는 금액
    holdings = 0     #현재 보유 수량
    actions = [] # 액션 변수
    current_average_price = 0 #평단가 (total_investment / holdings, 소수점 둘째자리까지 계산)

    for i in range(0, len(qqq_closing_prices_krw)):
        #현재가
        current_price = qqq_closing_prices_krw.iloc[i].CloseKrw

        #매도 먼저 확인, 그 이후 매수
        if current_price!=0 and holdings >=1 and (-1 + (current_price/current_average_price)) >= sell_threshold:
            #Sell Action
            #매도금액 : 보유금액 * sell_ratio or 종목 1주 가격 중 큰 값
            sell_amount = round(max(total_investment*sell_ratio, current_price),2)
            sell_holdings =  int(sell_amount/current_price)
            holdings -= sell_holdings

            #투입자산 변경 (평단가 * 매도량만큼 자산 감소)
            total_investment -= round(current_average_price*int(sell_amount/current_price),2)

            #내 자산 변경액 (수익금, 현재가*매도량 - 평단가*매도량 만큼 자산 증가)
            asset_amount = round((current_price-current_average_price)*sell_holdings,2)
            #print(i,'sell', '판 금액 : ', sell_amount, '평단가 : ', current_average_price, '판 개수 :', sell_holdings, '투입금 : ', total_investment, '수익금 : ', asset_amount)
            
            current_average_price = round(total_investment / holdings,2)
            actions.append((i, str(qqq_closing_prices_krw.iloc[i].Date), 'Sell', sell_amount, total_investment, current_average_price, current_price, sell_holdings, holdings, asset_amount))
            #자산 변경 반영 (전일 자산 + 수익금)
            #asset_amounts[i] = asset_amounts[i-1]+asset_amount
            
            asset_amounts.append(asset_amounts[-1]+asset_amount)
            
        if qqq_closing_prices_krw.iloc[i].PctChange <= - buy_threshold:
            #Buy Action
            #매수금액 : 투자가능자산액 * buy_ratio (단 이 금액이 주식 1주가격보다 작다면 매수진행하지 않음)
            #현재 남아있는금액
            remain_amount = asset_amount_krw - total_investment
            buy_amount = round(remain_amount*buy_ratio,2)
            buy_holdings = int(buy_amount/current_price)
            if buy_amount >=current_price:
                holdings += buy_holdings

                # buy_amount를 더해도 되지만 좀 더 정확한 계산을 위해(매수수량이 정수단위로 버림되므로) 매수수량에 종가를 곱함.
                total_investment += round(current_price*int(buy_amount/current_price),2)
                
                current_average_price = round(total_investment / holdings,2)
                actions.append((i, str(qqq_closing_prices_krw.iloc[i].Date), 'Buy', buy_amount, total_investment, current_average_price, current_price, buy_holdings, holdings))

                #print(i, 'buy', '산 금액 : ', buy_amount, '평단가 : ', current_average_price, '산 개수 :', buy_holdings, '투입금액 : ', total_investment)

                #자산은 전날 자산과 기본적으로 동일하나 같은 날 매수내역이 있으면 매수내역을 반영한 자산이 그대로 남아있어야함.
                #매수 내역 여부 확인 후 asset_amount 값 변경하기
                if len(asset_amounts) == i+1:
                    pass
                else :
                    asset_amounts.append(asset_amounts[-1])

        if len(asset_amounts) != (i+1) :
            #print(i, 'nothing to do')
            asset_amounts.append(asset_amounts[-1])
    return asset_amounts, actions

# 사용자 입력 받기
# asset_amount_krw = float(input("내 자산액 (KRW): "))
# buy_threshold = float(input("매수 기준점 (%): ")) / 100
# sell_threshold = float(input("매도 기준점 (%): ")) / 100
# buy_ratio = float(input("매수 비중 (%): ")) / 100
# sell_ratio = float(input("매도 비중 (%): ")) / 100

def bkproject(asset_amount_krw, buy_threshold, sell_threshold, buy_ratio, sell_ratio, ticker, start_date, end_date,country):
    if country == 'US':    
        closing_prices_usd = get_price(ticker,start_date, end_date)[['Date','Close','PctChange']]
        exchange_rates = get_exchage_rate_daily(start_date, end_date)[['Date','Close']]
        closing_prices_krw = pd.merge(closing_prices_usd , exchange_rates, on='Date')
        closing_prices_krw['CloseKrw'] = round(closing_prices_krw.Close_x * closing_prices_krw.Close_y,2)
    
    elif country == 'KR':
        closing_prices_krw = get_price(ticker, start_date, end_date)[['Date','Close','PctChange']]
        closing_prices_krw.rename(columns=['Close','CloseKrw'], inplace=True)
        closing_prices_krw['CloseKrw'] = round(closing_prices_krw.CloseKrw,2)

    asset_amounts, actions = simulate_trading(asset_amount_krw, closing_prices_krw, buy_threshold, sell_threshold, buy_ratio, sell_ratio)

    #pd.DataFrame(actions).to_csv(f'actions_{asset_amount_krw}_{buy_threshold}_{sell_threshold}_{buy_ratio}_{sell_ratio}_{ticker}.csv')
    #pd.DataFrame(asset_amounts).to_csv(f'assets_{asset_amount_krw}_{buy_threshold}_{sell_threshold}_{buy_ratio}_{sell_ratio}_{ticker}.csv')
    #pd.DataFrame(closing_prices_krw.Date).to_csv(f'date_{asset_amount_krw}_{buy_threshold}_{sell_threshold}_{buy_ratio}_{sell_ratio}_{ticker}.csv')

    return asset_amounts, actions, closing_prices_krw

# asset_amounts, actions = bkproject(100000000, 0.0065, 0.015, 0.15,0.15, 'QQQ','2023-01-01','2023-12-28','US')

# asset_amount_krw = 100000000
# buy_threshold = 0.0065
# sell_threshold = 0.0125
# buy_ratio = 0.15
# sell_ratio = 0.15

# ticker = 'QQQ'  # QQQ ETF의 종목 코드
# start_date = '2023-01-01'
# end_date = '2023-12-28'
# qqq_closing_prices_usd = get_price(ticker, start_date, end_date)[['Date','Close','PctChange']]
# exchange_rates = get_exchage_rate_daily(start_date, end_date)[['Date','Close']]


# qqq_closing_prices_krw = pd.merge(qqq_closing_prices_usd , exchange_rates, on='Date')
# qqq_closing_prices_krw['CloseKrw'] = round(qqq_closing_prices_krw.Close_x * qqq_closing_prices_krw.Close_y,2)
# qqq_closing_prices_krw[qqq_closing_prices_krw.PctChange>=0.0065]

# 시뮬레이션 실행
# asset_amounts, actions = simulate_trading(asset_amount_krw, qqq_closing_prices_krw, buy_threshold, sell_threshold, buy_ratio, sell_ratio)
# pd.DataFrame(actions).to_csv('test.csv')
# pd.DataFrame(asset_amounts).to_csv('asset.csv')
# pd.DataFrame(qqq_closing_prices_krw.Date).to_csv('date.csv')
