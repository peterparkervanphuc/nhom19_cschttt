"""Descriptive views over the report's exported evidence tables."""
from html import escape
import re
from pathlib import Path

import pandas as pd
import streamlit as st

TABLES = Path(__file__).resolve().parents[1] / "reports/final-academic-v6.1-style/tables"
SCHEMAS = {
    "e1.csv": ["Log", "Tiền tố", "Lượt sửa", "Tau hữu hạn", "Tau trung bình", "Độ lệch chuẩn", "Trung vị", "Nguồn"],
    "e2.csv": ["Log", "Giao thức", "Nhánh", "Số cặp", "JSD", "TVD", "Nguồn"],
    "e3.csv": ["Log", "Tiền tố", "TVD theo tiền tố", "Độ lệch chuẩn", "Lần xuất hiện", "TVD theo vị trí", "Trung vị theo vị trí", "Nguồn"],
}


def paired(path):
    pattern = r"^([^&]+?) & ([\d\\,]+) & ([\d,]+) / ([\d,]+) & ([\d,]+) / ([\d,]+) & ([\d,]+) / ([\d,]+)\\\\"
    rows = []
    for line in path.read_text("utf8").splitlines():
        match = re.match(pattern, line.strip())
        if match:
            log, count, *metrics = match.groups()
            for i, method in enumerate(("BE", "AE")):
                values = [float(s.replace(",", ".")) for s in metrics[i::2]]
                rows.append([log, method, int(count.replace(r"\,", "")), *values])
    if not rows:
        raise ValueError("Bảng ghép cặp không có hàng đọc được.")
    return pd.DataFrame(rows, columns=["Log", "Phương pháp", "Tiền tố ghép cặp", "Precision", "Recall", "F1"])


def findings():
    st.html('<header class="work-title"><small>Đánh giá thực nghiệm</small><h1>Kết quả nghiên cứu</h1><p>Đối chiếu độ ổn định của attention, độ nhạy của dự đoán và chất lượng đồ thị giải thích.</p></header>')
    choice = st.radio("Phép đối chiếu", ["E1", "E2", "E3", "BE / AE"], horizontal=True)
    filename = {"E1":"e1.csv", "E2":"e2.csv", "E3":"e3.csv", "BE / AE":"paired-main.tex"}[choice]
    try:
        frame = (paired(TABLES / filename) if choice == "BE / AE" else
                 pd.read_csv(TABLES / filename, header=None, names=SCHEMAS[filename]))
    except (OSError, ValueError) as error:
        st.error(f"Không đọc được bảng {filename}. {error}")
        return
    if choice == "E1":
        st.subheader("Thứ hạng attention so với độ quan trọng đầu vào")
        st.write("Tau-b được tính trên từng tiền tố. Cột “Tau hữu hạn” là mẫu số khi lấy trung bình các hệ số xác định được.")
        subset = frame[frame["Log"] == "BPIC12_WC"]
        if not subset.empty:
            row = subset.iloc[0]
            st.write(f"Trên BPIC12_WC, trung vị bằng {row['Trung vị']:g}. Chỉ {row['Tau hữu hạn']:,} trong {row['Tiền tố']:,} tiền tố có hệ số hữu hạn, nên trung vị này mô tả nhóm có thể xếp hạng.")
        measures = ["Tau trung bình", "Trung vị"]
        domain = [-1, 1]
    elif choice == "E2":
        protocol = st.selectbox("Giao thức", list(frame["Giao thức"].unique()))
        frame = frame[frame["Giao thức"] == protocol]
        branch = st.radio("Nhánh mô hình", list(frame["Nhánh"].unique()), horizontal=True)
        frame = frame[frame["Nhánh"] == branch]
        st.subheader("Độ lệch attention và độ lệch dự đoán")
        st.write("JSD mô tả hai phân phối attention. TVD mô tả hai phân phối xác suất đầu ra. So sánh hai đại lượng trên cùng cohort không xác lập quan hệ nhân quả.")
        subset = frame[frame["Log"] == "Helpdesk"]
        if not subset.empty:
            row = subset.iloc[0]
            st.write(f"Trên Helpdesk, nhánh {branch} có JSD trung bình {row['JSD']:.4f} và TVD trung bình {row['TVD']:.4f} trên {row['Số cặp']:,} cặp. Các giá trị này mô tả hai khía cạnh khác nhau của cùng phép can thiệp.")
        measures, domain = ["JSD", "TVD"], [0, 1]
    elif choice == "E3":
        st.subheader("Hai cách tính trọng số cho cùng phép che")
        st.write("Mỗi tiền tố có một phiếu khi lấy trung bình theo tiền tố. Khi lấy trung bình theo vị trí, chuỗi dài đóng góp nhiều lần hơn.")
        row = frame.loc[frame["TVD theo tiền tố"].idxmax()]
        st.write(f"{row['Log']} có TVD theo tiền tố cao nhất trong bảng ({row['TVD theo tiền tố']:.4f}). Khi tính theo từng lần xuất hiện trên cùng nhật ký, trung bình là {row['TVD theo vị trí']:.4f}.")
        measures, domain = ["TVD theo tiền tố", "TVD theo vị trí"], [0, 1]
    else:
        log = st.selectbox("Nhật ký", list(frame["Log"].unique()))
        frame = frame[frame["Log"] == log]
        st.subheader(f"Độ bao phủ và tính chọn lọc trên {log}")
        st.write("Precision và recall được đối chiếu trên cùng tập tiền tố. F1 là trung bình các F1 theo tiền tố. So sánh ở đây mang tính mô tả.")
        metrics = frame.set_index("Phương pháp")
        st.write(f"Recall của AE là {metrics.at['AE','Recall']:.4f}, so với {metrics.at['BE','Recall']:.4f} của BE. Precision tương ứng là {metrics.at['AE','Precision']:.4f} và {metrics.at['BE','Precision']:.4f}.")
        measures, domain = ["Precision", "Recall", "F1"], [0, 1]
    group = "Phương pháp" if choice == "BE / AE" else "Log"
    counts = {"E1":["Tiền tố","Tau hữu hạn"], "E2":["Số cặp"], "E3":["Tiền tố","Lần xuất hiện"], "BE / AE":["Tiền tố ghép cặp"]}[choice]
    low, high = domain
    origin = 100 * (0 - low) / (high - low)
    groups = []
    for _, record in frame.iterrows():
        bars = []
        for n, metric in enumerate(measures):
            value = float(record[metric])
            endpoint = 100 * (value - low) / (high - low)
            bars.append(f'<div class="measure"><span>{escape(metric)}</span><i style="--origin:{origin}%;--left:{min(origin,endpoint)}%;--width:{abs(endpoint-origin)}%;--color:{("#176553","#78934e","#526d83")[n]}"><b></b></i><code>{value:.4f}</code></div>')
        denominator = " · ".join(f"{name}: {int(record[name]):,}" for name in counts)
        groups.append(f'<section><strong>{escape(str(record[group]))}</strong> <small>{escape(denominator)}</small>{"".join(bars)}</section>')
    st.html(f'<figure class="evidence-chart"><figcaption>Thang đo từ {low} đến {high}</figcaption>{"".join(groups)}</figure>')
    st.caption(f"Tổng hợp từ kết quả độc lập đã lưu · báo cáo V6.1 · {filename}. Bảng dưới ghi mẫu số theo từng cohort.")
    st.dataframe(frame, hide_index=True, width="stretch")

