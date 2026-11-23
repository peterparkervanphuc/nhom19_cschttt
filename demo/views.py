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


def compare(r):
    st.markdown("**Khoảng cách giữa các phân phối (TVD)**")
    for c,title,v in zip(st.columns(3),["Gốc / đầu vào","Gốc / attention","Giữa hai cách che"],r["tvd"]):
        c.metric(title,f"{v:.4f}")
    st.caption("TVD bằng một nửa tổng sai khác tuyệt đối giữa xác suất các lớp. Giá trị 0 tương ứng với hai phân phối trùng nhau.")
    distribution(r,[0,1,2])


def heatmap(r):
    a,b=st.columns(2)
    head=a.selectbox("Attention head",range(len(r["attention"][0])),format_func=lambda h:f"Head {h+1}")
    arm=b.selectbox("Ma trận", [0,1],format_func=lambda i:["Gốc","Sau khi che attention"][i])
    matrix=r["attention"][arm][head]
    axis=[str(i+1) for i in range(len(matrix))]
    cells=[{"query":axis[i],"key":axis[j],"weight":v,"source":r["activities"][i],"destination":r["activities"][j]}
           for i,row in enumerate(matrix) for j,v in enumerate(row)]
    st.vega_lite_chart(pd.DataFrame(cells),{"height":min(520,max(150,20*len(matrix))),"mark":"rect",
        "encoding":{"x":{"field":"key","type":"ordinal","sort":axis,"title":"Vị trí key"},
        "y":{"field":"query","type":"ordinal","sort":axis,"title":"Vị trí query"},
        "color":{"field":"weight","type":"quantitative","title":"Trọng số","scale":{"domain":[0,1],"scheme":"tealblues"}},
        "tooltip":[{"field":f,"title":n} for f,n in [("query","Vị trí query"),("source","Hoạt động query"),("key","Vị trí key"),("destination","Hoạt động key"),("weight","Trọng số")]]}},alt="Trọng số attention theo cặp vị trí")


    with st.expander("Liên kết từ một vị trí truy vấn",on_change="rerun") as links:
        if links.open:
            q=st.selectbox("Vị trí truy vấn",range(len(matrix)),index=r["pos"],
                           format_func=lambda i:f"{i+1} · {r['activities'][i]}")
            links_svg=[]
            height=max(70,32*len(matrix))
            for j,value in enumerate(matrix[q]):
                y=16+32*j
                label=escape(r["activities"][j])
                links_svg.append(f'<path d="M68 {height/2} C140 {height/2} 150 {y} 220 {y}" stroke="#318471" fill="none" stroke-width="{8*value}"/><circle cx="220" cy="{y}" r="3" fill="#183e36"/><text x="230" y="{y+4}">{j+1}. {label} · {value:.4f}</text>')
            svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="{height}" font-family="sans-serif" font-size="13"><text x="4" y="{height/2+4}">Query {q+1}</text>'+''.join(links_svg)+'</svg>')
            st.image(svg,width=640,alt="Liên kết attention của query đã chọn với các vị trí key")
            st.caption("Độ dày của mỗi đường bằng 8 × trọng số attention. Giá trị bằng 0 không tạo đường nối.")


def provenance(r):
    with st.expander("Nguồn dữ liệu và cấu hình"):
        st.write(f"{r['dataset']} · {r['case']} · {len(r['activities'])} sự kiện · vị trí {r['pos']+1} · {r['profile']} · {r['device'].upper()}")
        st.code(f"checkpoint SHA-256: {r['checkpoint']}\ndataset SHA-256: {r['dataset_hash']}\nprefix: {r['prefix']}",wrap_lines=True)
