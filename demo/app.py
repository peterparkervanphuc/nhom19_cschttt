from pathlib import Path
import sys

import streamlit as st

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from research import ROOT, PROFILE, execute, inventory, load, paths
from observatory import optical_scene, findings
from views import STAGES, compare, distribution, heatmap, prediction, provenance, sequence
from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.pipeline import file_hash


@st.cache_resource(max_entries=1, show_spinner="Đang kiểm tra dữ liệu và checkpoint…")
def resources(dataset, version):
    return load(dataset)


def overview():
    st.title("Giải thích dự đoán hoạt động tiếp theo")
    st.markdown("**Explaining Transformer-Based Next Activity Prediction Using Attention Scores**")
    st.subheader("Trọng số attention giải thích được bao nhiêu về một dự đoán?")
    st.write("ProcessTransformer đọc chuỗi sự kiện đã xảy ra và ước tính xác suất của từng hoạt động tiếp theo. Một vị trí có thể nhận nhiều attention. Để biết dự đoán nhạy đến mức nào với vị trí ấy, ta có thể che nó và đo lại toàn bộ phân phối.")
    st.divider()
    for title,desc in [
        ("E1 · Thứ hạng hoạt động","Đối chiếu thứ hạng theo attention với thứ hạng thu được khi thay đổi đầu vào bằng hệ số Kendall."),
        ("E2 · Thay đổi tham số","So sánh độ phân kỳ attention và độ lệch dự đoán khi thay đổi điều kiện huấn luyện."),
        ("E3 · Hai phép che","Giữ nguyên checkpoint, che một sự kiện ở đầu vào hoặc che hàng và cột tương ứng trong attention. So sánh xác suất bằng TVD.")]:
        st.markdown(f"**{title}**　{desc}")
    st.caption("Một tiền tố minh họa độ nhạy cục bộ. Đánh giá độ trung thực của đồ thị BE/AE và mức phù hợp với quy trình cần bằng chứng trên nhiều tiền tố.")


def lab(r):
    st.subheader("Hai phép can thiệp trên cùng vị trí")
    left,right=st.columns(2)
    for col,arm,title in [(left,1,"Che đầu vào"),(right,2,"Che attention")]:
        with col:
            st.markdown(f"**{title}**")
            sequence(r,masked=arm==1)
            st.caption("Thay sự kiện bằng PAD, giữ nguyên chỉ số vị trí." if arm==1 else "Giữ chuỗi gốc. Đặt hàng và cột tương ứng về 0 sau softmax.")
            p=r["probabilities"][arm]
            st.write(f"→ **{r['classes'][p.index(max(p))]}** · {max(p):.2%}")
    compare(r)
    heatmap(r)
    st.caption("Attention mô tả cách head phân bổ trọng số. TVD đo độ nhạy của dự đoán với can thiệp. Cả hai phép đo đều phụ thuộc vào tiền tố và checkpoint.")


def live(explain=False):
    st.title("Phòng giải thích" if explain else "Suy luận trực tiếp")
    names=inventory()
    if not names:
        st.warning("Chưa tìm thấy cặp dữ liệu và checkpoint. Chọn Ví dụ dẫn giải để trình diễn ngoại tuyến.")
        return
    dataset=st.selectbox("Nhật ký sự kiện",names,index=names.index("helpdesk-v1") if "helpdesk-v1" in names else 0)
    try:
        version=tuple((p.stat().st_size,p.stat().st_mtime_ns) for p in paths(dataset))
        model,cases,init=resources(dataset,version)
    except Exception as error:
        st.error(f"Không thể nạp {dataset}: {error}. Có thể mở Ví dụ dẫn giải từ thanh điều hướng.")
        return
    left,mid=st.columns(2)
    case=left.selectbox("Hồ sơ kiểm thử",list(cases),key=f"case-{dataset}")
    lengths=sorted(cases[case])
    length=mid.selectbox("Độ dài tiền tố",lengths,index=lengths.index(3) if 3 in lengths else 0,key=f"length-{dataset}-{case}")
    row=cases[case][length]
    pos=st.segmented_control("Chọn sự kiện để che",range(length),default=length-1,
                             format_func=lambda i:f"{i+1} · {row['activities'][i]}",key=row["prefix_id"])
    if pos is None:
        st.caption("Chọn một vị trí trong tiền tố để tiếp tục.")
        return
    key=(dataset,version,model.checkpoint_id,row["prefix_id"],pos,PROFILE)
    cache=st.session_state.setdefault("results",{})
    run=st.button("Chạy dự đoán",type="primary")
    fresh=False
    if run and key not in cache:
        try:
            with st.spinner("Đang suy luận và đối chiếu hai phép che…"):
                result=execute(model,dataset,row,pos)
            if len(cache)>=8:
                del cache[next(iter(cache))]
            cache[key]=result
            fresh=True
        except Exception as error:
            st.error(f"Suy luận gặp lỗi: {error}. Ví dụ dẫn giải vẫn dùng được.")
    if key not in cache:
        st.caption("Bấm Chạy dự đoán để xem kết quả của tiền tố và vị trí đã chọn.")
        return
    r=cache[key]
    st.caption(("Vừa chạy trực tiếp" if fresh else "Kết quả đã lưu trong phiên")+" · "+r["device"].upper()+" · "+dataset)
    prediction(r)
    if explain:
        lab(r)
        provenance(r)
        return
    with st.expander("Phân phối gốc và thời gian thực thi"):
        distribution(r,[0])
        st.write(f"Nạp dữ liệu và mô hình: {init:.1f} ms")
        for name,field in [("Suy luận gốc (gồm attention)","base"),("Che đầu vào","input"),("Che attention","score"),("Xuất hai tensor attention sang danh sách","attention_export"),("Toàn bộ phép so sánh","total")]:
            st.text(f"{name} · {r['ms'][field]:.3f} ms")
    with st.expander("Phòng giải thích · attention và masking",on_change="rerun") as panel:
        if panel.open:
            lab(r)
    with st.expander("Đồ thị BE / AE đã lưu",on_change="rerun") as graphs:
        if graphs.open:
            st.caption("Đồ thị tổng hợp qua nhiều tiền tố trong lần chạy nghiên cứu.")
            for col,method in zip(st.columns(2),("BE","AE")):
                path=ROOT/"artifacts"/dataset/"graphs"/method/"graph.svg"
                if not path.exists():
                    col.info(f"Chưa có đồ thị {method} cho nhật ký này.")
                    continue
                manifest=read_sealed(path.with_name("manifest.json"))
                if file_hash(path)!=manifest["files"]["graph.svg"]:
                    col.error(f"Đồ thị {method} sai checksum.")
                else:
                    col.image(path.read_text("utf8"),caption=method,alt=f"Đồ thị {method}")
    provenance(r)


def move(step):
    st.session_state.step=step


def guided():
    st.title("Ví dụ dẫn giải")
    st.caption("Precomputed Research Result · Kết quả suy luận đã ghi từ checkpoint của dự án")
    samples=read_sealed(HERE/"examples.json")["examples"]
    index=st.selectbox("Chọn tình huống",range(len(samples)),index=None,placeholder="Chọn một ví dụ đã ghi",key="example",on_change=move,args=(0,),
                       format_func=lambda i:f"{samples[i]['dataset']} · {samples[i]['case']} · che vị trí {samples[i]['pos']+1}")
    if index is None:
        st.write("Hai ví dụ Helpdesk dùng cùng một tiền tố để khảo sát độ nhạy theo vị trí. Ví dụ Sequence cho phép đối chiếu với một chuỗi tuần tự.")
        return
    r=samples[index]
    step=st.session_state.get("step",0)
    titles=["Chuỗi quan sát","Dự đoán ban đầu","Attention theo vị trí","Che đầu vào","Che attention","Đối chiếu phân phối","Diễn giải"]
    st.html(f'<header class="guide"><small>Bước {step+1} / 7</small><h2>{titles[step]}</h2></header>')
    if step==0:
        sequence(r)
    elif step==1:
        prediction(r)
        distribution(r,[0])
    elif step==2:
        heatmap(r)
    elif step in (3,4):
        sequence(r,masked=step==3)
        st.caption("Vị trí che nhận PAD." if step==3 else "Giữ đầu vào, triệt hàng và cột attention sau softmax.")
        prediction(r,step-2)
        distribution(r,[step-2])
    elif step==5:
        compare(r)
    else:
        winners=[r["classes"][p.index(max(p))] for p in r["probabilities"]]
        st.write(f"Ở vị trí {r['pos']+1}, đầu vào gốc dự đoán **{winners[0]}**. Sau khi che đầu vào và che attention, hai nhãn đứng đầu lần lượt là **{winners[1]}** và **{winners[2]}**. Khoảng cách giữa hai phân phối sau can thiệp là **{r['tvd'][2]:.4f}**.")
        st.caption("Ngay cả khi nhãn đứng đầu trùng nhau, xác suất các lớp vẫn có thể thay đổi. Ví dụ này chỉ đo phản ứng của checkpoint trên tiền tố đang xem.")
    with st.container(horizontal=True):
        st.button("Trước",on_click=move,args=(step-1,),disabled=step==0)
        st.button("Tiếp",on_click=move,args=(step+1,),disabled=step==6,type="primary")
        st.button("Từ đầu",on_click=move,args=(0,))
        st.button("Chọn ví dụ khác",on_click=lambda:st.session_state.update(example=None,step=0))
    provenance(r)


st.set_page_config(page_title="Neural Observatory",layout="wide")
st.html((HERE/"style.html").read_text("utf8"))
pages=["Đài quan sát","Kiến trúc","Mô hình","Phòng giải thích","Dẫn giải","Kết quả"]
st.html('<div class="mast"><b>◉　Neural Observatory</b><span>ProcessTransformer　 /　 XAI Research</span></div>')
st.session_state.setdefault("page",pages[0])
page=st.segmented_control("Điều hướng",pages,key="page",label_visibility="collapsed")
if page in (None,pages[0]):
    optical_scene()
    st.button("Khám phá mô hình　→",type="primary",on_click=lambda:st.session_state.update(page="Mô hình"))
    with st.expander("Câu hỏi và phương pháp nghiên cứu"):
        overview()
elif page=="Kiến trúc":
    stage=st.selectbox("Tầng xử lý · từ đầu vào đến dự đoán",range(len(STAGES)),format_func=lambda i:f"{i+1} · {STAGES[i][0]}")
    optical_scene(stage)
    st.caption("Mỗi mặt phẳng là một tầng minh họa; mặt sáng là tầng đang chọn. Kéo chuột hoặc dùng phím mũi tên để xoay.")
elif page in ("Mô hình","Phòng giải thích"):
    live(explain=page=="Phòng giải thích")
elif page=="Dẫn giải":
    guided()
else:
    findings()
