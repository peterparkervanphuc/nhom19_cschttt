import json
from pathlib import Path
from html import escape

import streamlit as st

from views import STAGES

HERE=Path(__file__).resolve().parent


def optical_scene(stage=None):
    if stage is None:
        title="Explaining next activity prediction"
        desc="Một phòng thí nghiệm tương tác về cách Transformer dự đoán hoạt động tiếp theo từ nhật ký sự kiện."
        shape="Transformer attention scores"
    else:
        title,desc,shape=STAGES[stage]
    config=json.dumps(dict(stage=stage,title=title,desc=desc,shape=shape),ensure_ascii=True)
    st.iframe((HERE/"scene.html").read_text("utf8").replace("__CONFIG__",config),
              height=540,alt="Cảnh hạt ba chiều minh họa khái niệm, có thể xoay và tạm dừng")


def findings():
    st.title("Kết quả nghiên cứu")
    st.caption("Helpdesk · kết quả đã ghi trong báo cáo V6.1")
    selected=st.segmented_control("Thí nghiệm",["E1","E2","E3","BE / AE"],default="E1")
    records={
        "E1":("Thứ hạng attention và độ quan trọng đầu vào","0,9031","Kendall τ-b trung bình",
              "Trong 4.983 tiền tố, 3.497 tiền tố có hệ số hữu hạn. Giá trị trung bình mô tả mức đồng biến thứ hạng trong nhóm này.","e1.csv"),
        "E2":("Can thiệp tham số attention","0,04360","TVD trung bình · nhánh E2-FC",
              "Trên 24.915 cặp của E2-FC, JSD trung bình là 0,07843. Hai đại lượng mô tả hai phân phối khác nhau: attention và dự đoán.","e2.csv"),
        "E3":("Hai cách tổng hợp độ nhạy","0,3106","TVD trung bình theo tiền tố",
              "Cho mỗi tiền tố trọng số bằng nhau thu được 0,3106 trên 4.983 tiền tố. Cho mỗi lần xuất hiện trọng số bằng nhau thu được 0,2056 trên 12.547 vị trí.","e3.csv"),
        "BE / AE":("Độ bao phủ và tính chọn lọc","3.986","Cặp tiền tố hợp lệ",
              "Trên cùng cohort, recall của BE / AE là 0,8680 / 0,9999; precision là 0,4813 / 0,3134. AE bao phủ rộng hơn trong phép so sánh này.","paired-main.tex"),
    }
    title,value,label,note,source=records[selected or "E1"]
    st.subheader(title)
    st.metric(label,value)
    st.write(note)
    st.caption("Nguồn · reports/final-academic-v6.1-style/tables/"+source)
    st.caption("Các kết quả mô tả hành vi của checkpoint và cohort tương ứng. Mức attention cao tự nó chưa đủ để kết luận một sự kiện là nguyên nhân của dự đoán.")

