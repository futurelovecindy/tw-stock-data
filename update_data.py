import requests
import pandas as pd
import json
from datetime import datetime

STOCKS = [
    '2383', '6488', '3708', '1789', '2002', '2027', '3583', '2404', '6139',
    '5536', '6196', '6691', '3661', '3443', '3035', '2379', '8081', '6719',
    '2330', '2303', '5347', '3711', '6239', '6222', '6510', '6217', '2408',
    '2344', '8299', '4967', '4958', '3037', '2313', '8046', '3189', '6435',
    '8261', '3317', '2481', '2327', '2492', '2478', '3017', '3324', '3653',
    '6230', '2421', '3665', '3533', '3023', '2392', '6442', '3081', '3363',
    '3163', '4979', '3008', '3231', '2382', '2317', '6669', '2356', '2376',
    '2357'
]

def fetch_json(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"抓取失敗 {url}: {e}")
        return []

def main():
    print(f"開始抓取台股資料: {datetime.now()}")
    
    twse_price = fetch_json('https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL')
    tpex_price = fetch_json('https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes')
    twse_val = fetch_json('https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL')
    tpex_val = fetch_json('https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio_analysis')

    df_price = pd.DataFrame(twse_price + tpex_price)
    df_val = pd.DataFrame(twse_val + tpex_val)
    
    if not df_price.empty:
        df_price.rename(columns={'SecuritiesCompanyCode': 'Code', 'ClosingPrice': 'Close'}, inplace=True)
    if not df_val.empty:
        df_val.rename(columns={'SecuritiesCompanyCode': 'Code'}, inplace=True)

    result_rows = []
    for code in STOCKS:
        stock_data = {"id": code}
        
        if not df_price.empty and 'Code' in df_price.columns:
            p_row = df_price[df_price['Code'] == code]
            if not p_row.empty:
                stock_data['close'] = pd.to_numeric(p_row.iloc[0].get('Close', 0), errors='coerce')
                stock_data['volumeShares'] = pd.to_numeric(p_row.iloc[0].get('TradeVolume', 0), errors='coerce')
                change = pd.to_numeric(p_row.iloc[0].get('Change', 0), errors='coerce')
                stock_data['change'] = change if pd.notnull(change) else 0

        if not df_val.empty and 'Code' in df_val.columns:
            v_row = df_val[df_val['Code'] == code]
            if not v_row.empty:
                stock_data['per'] = pd.to_numeric(v_row.iloc[0].get('PEratio', 0), errors='coerce')
                stock_data['pbr'] = pd.to_numeric(v_row.iloc[0].get('PBratio', 0), errors='coerce')
                stock_data['dividendYield'] = pd.to_numeric(v_row.iloc[0].get('DividendYield', 0), errors='coerce')

        result_rows.append(stock_data)

    final_output = {
        "updatedAt": datetime.now().isoformat(),
        "rows": result_rows
    }
    
    with open('stock_latest.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
        
    print("資料更新完成，已儲存至 stock_latest.json")

if __name__ == "__main__":
    main()
