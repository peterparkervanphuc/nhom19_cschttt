"""Offline-capable presentation components for ProcessTransformer."""
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

CONDITIONS = ["Tiền tố gốc", "Che đầu vào", "Che attention"]
STAGES = [
    ("Embedding", "Cộng vector hoạt động và vector vị trí tại từng sự kiện.", "n × 36"),
    ("Self-attention", "Mỗi head chiếu Q, K, V sang 9 chiều. Softmax theo key sau khi chia tích vô hướng cho √9. Ghép bốn head rồi chiếu về 36 chiều.", "4 × n × n"),
    ("Residual + Norm", "Cộng đầu ra attention với embedding ban đầu rồi chuẩn hóa từng vị trí.", "n × 36"),
    ("Feed-forward", "Hai phép chiếu 36 → 64 → 36 xen giữa bởi ReLU. Cộng đường dư và chuẩn hóa lần hai.", "n × 36"),
    ("Mean pooling", "Lấy trung bình biểu diễn của các vị trí hợp lệ. Mỗi hồ sơ còn một vector.", "36"),
    ("Phân loại", "Chiếu 36 → 64, ReLU, chiếu sang các lớp đầu ra rồi softmax. Dropout tắt khi suy luận.", "P(y | prefix)"),
]


def sequence(r, masked=False):
    chips = []
    for i,a in enumerate(r["activities"]):
        active = i == r["pos"]
        name = (f'<span class="swap"><del>{escape(a)}</del><ins>PAD</ins></span>' if active and masked else escape(a))
        chips.append(f'<li class="{("sel" if active else "")}"><small>{i+1:02}</small> {name}</li>')
    st.html('<ol class="trace" aria-label="Tiền tố quan sát">'+"".join(chips)+'</ol>')


def prediction(r, arm=0):
    p = r["probabilities"][arm]
    ranks = sorted(range(len(p)),key=p.__getitem__,reverse=True)
    y = r["classes"][ranks[0]]
    left,right = st.columns([1,1.3])
    with left:
        st.html(f'<div class="result"><small>{CONDITIONS[arm]}</small><h3>{escape(y)}</h3><b>{p[ranks[0]]:.2%}</b></div>')
        st.write(f"Nhãn thực tế · **{r['target']}**")
        if arm==0:
            st.caption("Dự đoán đúng" if y==r["target"] else "Dự đoán khác nhãn thực tế")
    with right:
        st.markdown("**Ba hoạt động có xác suất cao nhất**")
        for j in ranks[:3]:
            st.progress(float(min(1,p[j])),text=f"{r['classes'][j]} · {p[j]:.2%}")


def distribution(r, arms):
    frame = pd.DataFrame({CONDITIONS[i]: r["probabilities"][i] for i in arms},index=r["classes"])
    frame.index.name="Hoạt động"
    st.dataframe(frame.style.format("{:.2%}"),width="stretch",height="content")


def probability_chart(r):
    probs = r["probabilities"]
    classes = sorted(range(len(r["classes"])), key=lambda j:max(p[j] for p in probs), reverse=True)
    colors = ["#176553", "#78934e", "#526d83"]

    def render(indices):
        groups = []
        for j in indices:
            bars = []
            for condition, p, color in zip(CONDITIONS, probs, colors):
                bars.append(f'<div class="measure"><span>{condition}</span>'
                            f'<i style="--origin:0%;--left:0%;--width:{p[j]:.6%};--color:{color}"><b></b></i>'
                            f'<code>{p[j]:.2%}</code></div>')
            groups.append(f'<section><strong>{escape(r["classes"][j])}</strong>{"".join(bars)}</section>')
        st.html('<figure class="evidence-chart"><figcaption>Xác suất dự đoán · 0–100%</figcaption>'
                + "".join(groups) + '</figure>')

    st.markdown("**Ba phân phối xác suất theo hoạt động**")
    render(classes[:5])
    if len(classes) > 5:
        with st.expander(f"Xem {len(classes)-5} hoạt động còn lại"):
            render(classes[5:])


def compare_positions(results):
    first = results[0][0]
    base = first["probabilities"][0]
    st.write(f"Dự đoán gốc · **{first['classes'][base.index(max(base))]}** · {max(base):.2%}")
    records = [r for r, fresh in results]
    for col, (r, fresh) in zip(st.columns(2), results):
        with col:
            pos = r["pos"]
            st.markdown(f"**{pos+1} · {r['activities'][pos]}**")
            st.caption("Suy luận trực tiếp" if fresh else "Kết quả đã lưu trong phiên")
            for arm in (1, 2):
                p = r["probabilities"][arm]
                label = r["classes"][p.index(max(p))]
                st.metric(f"{CONDITIONS[arm]} · TVD so với gốc", f"{r['tvd'][arm-1]:.4f}")
                st.write(f"{label} · {max(p):.2%}")
    selected = st.radio("Xem phân phối khi che vị trí", [0, 1], horizontal=True,
                        format_func=lambda i:f"{records[i]['pos']+1} · {records[i]['activities'][records[i]['pos']]}")
    probability_chart(records[selected])
    provenance(records[selected])


def compare(r):
    st.markdown("**Khoảng cách giữa các phân phối (TVD)**")
    for c,title,v in zip(st.columns(3),["Gốc / đầu vào","Gốc / attention","Giữa hai cách che"],r["tvd"]):
        c.metric(title,f"{v:.4f}")
    st.caption("TVD bằng một nửa tổng sai khác tuyệt đối giữa xác suất các lớp. Giá trị 0 tương ứng với hai phân phối trùng nhau.")
    probability_chart(r)
    with st.expander("Bảng xác suất theo thứ tự lớp"):
        distribution(r,[0,1,2])


def heatmap(r):
    a, b = st.columns(2)
    head = a.selectbox("Attention head", range(len(r["attention"][0])), format_func=lambda h:f"Head {h+1}")
    arm = b.radio("Ma trận", [0,1], format_func=lambda i:["Gốc","Sau khi che attention"][i], horizontal=True)
    matrix = r["attention"][arm][head]
    names = r["activities"]
    blocks = list(range(0, len(names), 12))
    def window_label(start):
        return f"{start+1}–{min(start+12,len(names))}"
    row_start = col_start = 0
    if len(blocks) > 1:
        row_start = a.selectbox("Nhóm hàng query", blocks, format_func=window_label)
        col_start = b.selectbox("Nhóm cột key", blocks, format_func=window_label)
    keys = range(col_start, min(col_start+12,len(names)))
    queries = range(row_start, min(row_start+12,len(names)))
    def label(i):
        return f"{i+1} · {escape(names[i])}"
    header = "".join(f'<th scope="col" title="{label(j)}">K{j+1}</th>' for j in keys)
    rows = []
    for i in queries:
        cells = []
        for j in keys:
            weight = matrix[i][j]
            rgb = tuple(round(low + weight*(high-low)) for low,high in [(236,16),(244,91),(235,75)])
            color = "white" if weight > .62 else "#102b24"
            tip = f"Q{label(i)} → K{label(j)} · {weight:.6f}"
            focus = "marked" if r["pos"] in (i,j) else ""
            cells.append(f'<td class="{focus}" style="background:rgb{rgb};color:{color}" title="{tip}">{weight:.3f}</td>')
        rows.append(f'<tr><th scope="row" title="{label(i)}">Q{i+1}</th>{"".join(cells)}</tr>')
    st.html(f'<div class="matrix-scroll" tabindex="0" aria-label="Ma trận attention, có thể cuộn"><table class="matrix"><caption>Attention · Head {head+1} · hàng query × cột key</caption><thead><tr><td></td>{header}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    st.html('<div class="matrix-key">0 <i></i> 1　·　Trọng số attention</div>')
    st.caption(f"Viền đánh dấu hàng và cột của vị trí {r['pos']+1}. Chỉ số Q và K theo thứ tự sự kiện. Di chuột vào ô để đọc tên hoạt động và trọng số.")
    with st.expander("Liên kết từ một vị trí truy vấn",on_change="rerun") as links:
        if links.open:
            q = st.selectbox("Vị trí truy vấn",range(len(matrix)),index=r["pos"],format_func=lambda i:f"{i+1} · {names[i]}")
            height = 32*len(keys)+16
            paths = []
            for index,j in enumerate(keys):
                value = matrix[q][j]
                y = 20+32*index
                paths.append(f'<path d="M65 {height/2} C130 {height/2} 140 {y} 200 {y}" stroke="#318471" fill="none" stroke-width="{8*value}"/><circle cx="200" cy="{y}" r="3" fill="#183e36"/><text x="210" y="{y+4}">K{j+1} · {value:.4f}</text>')
            svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 {height}" width="340" height="{height}"><g font-family="sans-serif" font-size="13"><text x="4" y="{height/2+4}">Q{q+1}</text>{"".join(paths)}</g></svg>'
            st.image(svg,width="content",alt="Trọng số từ vị trí query đã chọn đến các key đang xem")
            st.caption("Độ dày cạnh bằng 8 × trọng số. Mỗi đích tương ứng với một cột trong cửa sổ ma trận.")


def provenance(r):
    with st.expander("Nguồn dữ liệu và cấu hình"):
        st.write(f"{r['dataset']} · {r['case']} · {len(r['activities'])} sự kiện · vị trí {r['pos']+1} · {r['profile']} · {r['device'].upper()}")
        st.code(f"checkpoint SHA-256: {r['checkpoint']}\ndataset SHA-256: {r['dataset_hash']}\nprefix: {r['prefix']}",wrap_lines=True)
