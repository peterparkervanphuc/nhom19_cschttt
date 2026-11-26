import json
from pathlib import Path

import streamlit as st

from views import STAGES

HERE = Path(__file__).resolve().parent


def opening(model_page, architecture_page):
    with st.container(key="opening"):
        intro, visual = st.columns([1, 1.15], gap="medium", vertical_alignment="center")
        with intro:
            st.html("""<header class="intro"><small>Predictive Process Monitoring</small>
            <h1>Explaining Next<br><em>Activity Prediction</em></h1>
            <p>Từ chuỗi sự kiện đã quan sát, Transformer dự đoán hoạt động nào tiếp theo?
            Chọn một tiền tố và che một sự kiện để xem xác suất thay đổi ra sao.</p></header>""")
            with st.container(horizontal=True, gap="small"):
                if st.button("Khám phá mô hình →", type="primary"):
                    st.switch_page(model_page)
                if st.button("Tìm hiểu kiến trúc"):
                    st.switch_page(architecture_page)
        with visual:
            st.iframe((HERE/"scene.html").read_text("utf8"), height="content",
                      alt="Dòng thông tin từ bốn vị trí sự kiện đến dự đoán")
    st.html("""<section class="research-index"><header><small>Nghiên cứu gốc</small><h2>Explaining Transformer-Based Next Activity Prediction Using Attention Scores</h2></header>
    <div><h3>Đọc chuỗi sự kiện</h3><p>Embedding biểu diễn hoạt động và vị trí. Bốn head phân bổ attention giữa các vị trí trước khi mô hình tổng hợp tiền tố.</p></div>
    <div><h3>Kiểm tra lời giải thích</h3><p>E1 đối chiếu thứ hạng, E2 thay đổi tham số, E3 so sánh hai cách che. Đồ thị BE và AE tổng hợp các quan hệ qua nhiều tiền tố.</p></div></section>""")


def architecture():
    scene = (HERE/"architecture.html").read_text("utf8")
    st.iframe(scene.replace("__STAGES__", json.dumps(STAGES, ensure_ascii=True)),
              height="content", alt="Khám phá sáu tầng xử lý của ProcessTransformer")

