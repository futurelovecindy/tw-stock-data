import requests
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
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"抓取失敗 {url}: {e}")
        return []

def safe_float(val):
    # 安全轉換數值，自動去除逗號（例如 2,500 轉為 2500）
    try:
        return float(str(val).replace(',', '').strip())
    except:
        return 0.0

def main():
    print(f"開始抓取台股資料: {datetime.now()}")
    
    twse_price = fetch_json('https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL')
    tpex_price = fetch_json('https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes')
    twse_val = fetch_json('https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL')
    tpex_val = fetch_json('https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio_analysis')

    # 建立字典快速對應代號，徹底避開 Pandas 欄位衝突錯誤
    price_map = {}
    for item in (twse_price + tpex_price):
        code = str(item.get('Code') or item.get('SecuritiesCompanyCode') or '').strip()
        if code:
            price_map[code] = item

    val_map = {}
    for item in (twse_val + tpex_val):
        code = str(item.get('Code') or item.get('SecuritiesCompanyCode') or '').strip()
        if code:
            val_map[code] = item

    result_rows = []
    for code in STOCKS:
        stock_data = {"id": code}
        
        # 處理價格與成交量
        p_item = price_map.get(code, {})
        stock_data['close'] = safe_float(p_item.get('ClosingPrice') or p_item.get('Close'))
        stock_data['volumeShares'] = safe_float(p_item.get('TradeVolume') or p_item.get('TradingShares'))
        stock_data['change'] = safe_float(p_item.get('Change'))

        # 處理估值與殖利率
        v_item = val_map.get(code, {})
        stock_data['per'] = safe_float(v_item.get('PEratio'))
        stock_data['pbr'] = safe_float(v_item.get('PBratio'))
        stock_data['dividendYield'] = safe_float(v_item.get('DividendYield'))

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
