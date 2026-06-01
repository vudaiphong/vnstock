import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Import vnstock - Sử dụng theo cấu trúc Class-based API
from vnstock.api.quote import Quote
from vnstock import Reference

def calculate_atr(df, period=14):
    """
    Tính toán chỉ báo Normalized ATR (NATR) để đo lường biến động tương đối
    của các mã có thị giá khác nhau.
    """
    df = df.copy()
    df['prev_close'] = df['close'].shift(1)
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['prev_close'])
    df['tr3'] = abs(df['low'] - df['prev_close'])
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    df['atr'] = df['tr'].rolling(window=period).mean()
    # Normalized ATR (NATR) tính bằng % so với giá đóng cửa
    df['natr'] = (df['atr'] / df['close']) * 100
    return df['natr'].mean()

def main():
    print("Đang lấy danh sách mã cổ phiếu VN30...")
    try:
        # Lấy danh sách thành viên VN30
        vn30_df = Reference().index.members('VN30')
        symbols = vn30_df['symbol'].tolist()
    except Exception as e:
        print(f"Không lấy được bằng index.members: {e}. Đang dùng danh sách tĩnh...")
        symbols = [
            "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG", 
            "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB", 
            "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
        ]

    print(f"Danh sách VN30 ({len(symbols)} mã): {', '.join(symbols)}")

    start_date = "2026-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")

    results = []

    for sym in symbols:
        print(f"Đang tải dữ liệu cho {sym}...")
        try:
            # Lấy dữ liệu OHLC sử dụng Quote
            quote = Quote(symbol=sym)
            df = quote.history(start=start_date, end=end_date, interval='1D')
            if df is not None and not df.empty and len(df) > 1:
                # Tính toán % Thay đổi từ đầu năm 2026 đến nay
                first_close = df.iloc[0]['close']
                last_close = df.iloc[-1]['close']
                pct_change = ((last_close - first_close) / first_close) * 100
                
                # Tính biến động giá (ATR trung bình)
                avg_natr = calculate_atr(df)
                
                results.append({
                    'Symbol': sym,
                    'Change (%)': pct_change,
                    'Avg NATR (%)': avg_natr
                })
        except Exception as e:
            print(f"Lỗi ở mã {sym}: {e}")

    if not results:
        print("Không có dữ liệu nào được tải thành công!")
        return

    # Sắp xếp kết quả theo mức độ tăng trưởng
    res_df = pd.DataFrame(results).dropna()
    res_df = res_df.sort_values(by='Change (%)', ascending=False).reset_index(drop=True)
    
    # Tìm mã tăng mạnh nhất và biến động nhiều nhất
    best_stock = res_df.iloc[0]
    most_volatile = res_df.sort_values(by='Avg NATR (%)', ascending=False).iloc[0]
    
    print("\n" + "="*50)
    print("TỔNG KẾT TỪ 01/01/2026 ĐẾN NAY")
    print(f"🚀 MÃ TĂNG MẠNH NHẤT: {best_stock['Symbol']} (Tăng {best_stock['Change (%)']:.2f}%)")
    print(f"📈 MÃ BIẾN ĐỘNG NHIỀU NHẤT: {most_volatile['Symbol']} (NATR trung bình {most_volatile['Avg NATR (%)']:.2f}%)")
    print("="*50 + "\n")

    # Vẽ biểu đồ
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Cột hiển thị % thay đổi giá
    colors = ['green' if val > 0 else 'red' for val in res_df['Change (%)']]
    bars = ax1.bar(res_df['Symbol'], res_df['Change (%)'], color=colors, alpha=0.7, label='Mức tăng/giảm (%)')
    ax1.set_xlabel('Mã cổ phiếu (VN30)', fontsize=12)
    ax1.set_ylabel('Mức tăng/giảm (%)', fontsize=12)
    ax1.set_title('Hiệu suất và Biến động giá (ATR) của VN30 từ đầu năm 2026', fontsize=14, weight='bold')
    ax1.tick_params(axis='x', rotation=45)
    
    # Vẽ đường hiển thị NATR
    ax2 = ax1.twinx()
    line = ax2.plot(res_df['Symbol'], res_df['Avg NATR (%)'], color='blue', marker='o', 
                    linewidth=2, label='Biến động NATR (%)')
    ax2.set_ylabel('Chỉ báo NATR trung bình (%)', color='blue', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='blue')
    
    # Tạo bảng chú giải (Legend)
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    fig.tight_layout()
    
    # Lưu file ảnh
    chart_filename = 'vn30_analysis.png'
    plt.savefig(chart_filename)
    print(f"Đã lưu biểu đồ thành file: {chart_filename}")

if __name__ == "__main__":
    main()
