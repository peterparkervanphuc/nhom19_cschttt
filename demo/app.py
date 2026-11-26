from pathlib import Path
import sys

import streamlit as st

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from findings import findings
from observatory import opening, architecture
from research import ROOT, PROFILE, execute, inventory, load, paths
from views import compare, compare_positions, distribution, heatmap, prediction, provenance, sequence
from nhom19_process_xai.artifacts import read_sealed
from nhom19_process_xai.data.pipeline import file_hash


@st.cache_resource(max_entries=1, show_spinner="Đang kiểm tra dữ liệu và checkpoint…")
def resources(dataset, version):
    return load(dataset)


def inference_result(model, dataset, version, row, pos, *, run=True):
    key = (dataset, version, model.checkpoint_id, row["prefix_id"], pos, PROFILE)
    cache = st.session_state.setdefault("results", {})
    fresh = key not in cache
    if fresh:
        if not run:
            return None, False
        result = execute(model, dataset, row, pos)
        if len(cache) >= 8:
            del cache[next(iter(cache))]
        cache[key] = result
    return cache[key], fresh


def keep_latest_pair(key):
    # Widget order can follow trace order. Track click order for replacing the oldest.
    selected = st.session_state[key]
    prior = st.session_state.get("pair_order", [])
    ordered = [i for i in prior if i in selected] + [i for i in selected if i not in prior]
    st.session_state.pair_order = ordered[-2:]
    if len(ordered) > 2:
        st.session_state[key] = ordered[-2:]


def pair_explorer(model, dataset, version, row):
    key = f"pair-{dataset}-{row['prefix_id']}"
    positions = st.pills("Chọn hai sự kiện trong chuỗi", range(len(row["activities"])),
                         selection_mode="multi", key=key, on_change=keep_latest_pair, args=(key,),
                         format_func=lambda i: f"{i+1} · {row['activities'][i]}")
    if len(positions) != 2:
        st.caption("Chọn thêm một vị trí để so sánh." if positions else "Bấm hai vị trí để chạy hai phép che riêng biệt trên cùng tiền tố.")
        return
    try:
        with st.spinner("Đang đối chiếu hai vị trí…"):
            results = [inference_result(model, dataset, version, row, pos) for pos in sorted(positions)]
    except Exception as error:
        st.error(f"Không thể hoàn tất phép so sánh. {error}")
        return
    compare_positions(results)


def lab(r):
    st.subheader("Hai phép che trên cùng tiền tố")
    for col, arm, title in zip(st.columns(2), [1, 2], ["Che đầu vào", "Che attention"]):
        with col:
            st.markdown(f"**{title}**")
            sequence(r, masked=arm == 1)
            st.caption("Thay sự kiện bằng PAD, giữ nguyên vị trí." if arm == 1 else
                       "Giữ chuỗi gốc, đặt hàng và cột đã chọn về 0 sau softmax.")
            probs = r["probabilities"][arm]
            st.write(f"**{r['classes'][probs.index(max(probs))]}** · {max(probs):.2%}")
    compare(r)
    st.caption("Trọng số attention mô tả cách head kết hợp các vị trí. Xác suất thuộc về lớp dự đoán. TVD đo độ nhạy với phép che. Một phép che trên một tiền tố chưa xác lập độ trung thực của lời giải thích.")


def live(explain=False):
    title = "Giải thích dự đoán" if explain else "Dự đoán hoạt động tiếp theo"
    description = ("Đối chiếu attention và hai phép che trên cùng một tiền tố kiểm thử." if explain else
                   "Chọn điểm dừng trong một hồ sơ kiểm thử và đối chiếu dự đoán với sự kiện kế tiếp.")
    st.html(f'<header class="work-title"><small>{"Attention Scores" if explain else "Model Explorer"}</small><h1>{title}</h1><p>{description}</p></header>')
    names = inventory()
    if not names:
        st.warning("Cần cặp dữ liệu và checkpoint để suy luận trực tiếp.")
        st.page_link(PAGES[4], label="Mở tình huống đã tính trước")
        return
    controls, output = st.columns([1, 2.15], gap="large")
    previous = st.session_state.get("selection", {})
    with controls, st.container(key="controls"):
        st.subheader("Tiền tố kiểm thử")
        default = previous.get("dataset")
        if default not in names:
            default = "helpdesk-v1" if "helpdesk-v1" in names else names[0]
        dataset = st.selectbox("Nhật ký sự kiện", names, index=names.index(default))
        try:
            version = tuple((p.stat().st_size, p.stat().st_mtime_ns) for p in paths(dataset))
            model, cases, init = resources(dataset, version)
        except Exception as error:
            st.error(f"Không thể nạp {dataset}. {error}")
            st.page_link(PAGES[4], label="Mở tình huống đã tính trước")
            return
        if previous.get("dataset") != dataset:
            previous = {}
        ids = list(cases)
        case = st.selectbox("Hồ sơ kiểm thử", ids, index=ids.index(previous.get("case")) if previous.get("case") in cases else 0, key=f"case-{dataset}")
        lengths = sorted(cases[case])
        saved_length = previous.get("length") if previous.get("case") == case else None
        default_length = saved_length if saved_length in lengths else 3 if 3 in lengths else lengths[0]
        length = st.selectbox("Độ dài tiền tố", lengths, index=lengths.index(default_length), key=f"len-{dataset}-{case}")
        row = cases[case][length]
        pair = length > 1 and st.toggle("So sánh hai vị trí", key=f"pair-mode-{dataset}")
        if pair:
            st.caption("Mỗi lần chỉ che một sự kiện. Bấm vị trí thứ ba để thay vị trí đã chọn đầu tiên.")
            with output, st.container(key="pair-output"):
                st.subheader("So sánh hai vị trí trong tiền tố")
                pair_explorer(model, dataset, version, row)
            return
        pos = st.selectbox("Vị trí cần che", range(length),
            index=previous["pos"] if previous.get("prefix")==row["prefix_id"] else length-1,
            format_func=lambda i:f"{i+1} · {row['activities'][i]}", key=f"pos-{row['prefix_id']}")
        st.session_state.selection = dict(dataset=dataset,case=case,length=length,pos=pos,prefix=row["prefix_id"])
        run = st.button("Chạy dự đoán", type="primary", width="stretch")
        st.caption("Checkpoint đã huấn luyện · CPU · " + PROFILE)
    with output, st.container(key="output"):
        st.subheader("Chuỗi sự kiện đã quan sát")
        sequence({"activities":row["activities"], "pos":pos})
        try:
            with st.spinner("Đang suy luận và so sánh hai can thiệp…"):
                r, fresh = inference_result(model, dataset, version, row, pos, run=run)
        except Exception as error:
            st.error(f"Lượt suy luận gặp lỗi. {error}")
            return
        if r is None:
            st.info("Chọn Chạy dự đoán để xem phân phối xác suất và tác động của vị trí đã chọn.")
            return
        st.caption(("Suy luận trực tiếp" if fresh else "Kết quả đã lưu trong phiên") + f" · {dataset} · {r['device'].upper()}")
        if explain:
            st.subheader("Attention theo vị trí")
            heatmap(r)
        else:
            prediction(r)
            st.page_link(PAGES[3], label="Xem attention và so sánh hai phép che →")
            with st.expander("Phân phối xác suất và thời gian thực thi"):
                distribution(r,[0])
                for name, value in [("Nạp dữ liệu và checkpoint",init),("Dự đoán gốc, gồm attention",r["ms"]["base"]),("Che đầu vào",r["ms"]["input"]),("Che attention",r["ms"]["score"]),("Xuất tensor attention",r["ms"]["attention_export"]),("Toàn bộ phép so sánh",r["ms"]["total"])]:
                    st.text(f"{name} · {value:.2f} ms")
            with st.expander("Đồ thị BE và AE đã lưu",on_change="rerun") as graphs:
                if graphs.open:
                    st.caption("Đồ thị tổng hợp qua nhiều tiền tố của nhật ký.")
                    for col, method in zip(st.columns(2),("BE","AE")):
                        path=ROOT/"artifacts"/dataset/"graphs"/method/"graph.svg"
                        if not path.is_file():
                            col.info(f"Chưa có đồ thị {method} cho nhật ký này.")
                            continue
                        manifest=read_sealed(path.with_name("manifest.json"))
                        if file_hash(path)!=manifest["files"]["graph.svg"]:
                            col.error(f"Đồ thị {method} sai checksum.")
                        else:
                            col.image(path.read_text("utf8"),caption=method,alt=f"Đồ thị {method}")
            provenance(r)
    if explain:
        lab(r)
        provenance(r)


def move(step):
    st.session_state.step=step


def advance(delta):
    move(max(0, min(6, st.session_state.get("step", 0) + delta)))


def guided():
    st.html('<header class="work-title"><small>Kết quả đã tính trước</small><h1>Dẫn giải theo tình huống</h1><p>Theo dõi một tiền tố từ dự đoán ban đầu đến hai phép can thiệp.</p></header>')

    samples=read_sealed(HERE/"examples.json")["examples"]
    index=st.selectbox("Bước 1 · Chọn tình huống",range(len(samples)),index=None,placeholder="Chọn một ví dụ đã ghi",key="example",on_change=move,args=(0,),
                       format_func=lambda i: guided_question(samples[i]))
    if index is None:
        st.write("Hai ví dụ Helpdesk dùng cùng một tiền tố để khảo sát độ nhạy theo vị trí. Ví dụ Sequence cho phép đối chiếu với một chuỗi tuần tự.")
        return
    r=samples[index]
    st.caption(f"{r['dataset']} · {r['case']} · tiền tố dài {len(r['activities'])} · che vị trí {r['pos']+1}")
    step=st.session_state.get("step",0)
    titles=["Chuỗi quan sát","Dự đoán ban đầu","Attention theo vị trí","Che đầu vào","Che attention","Đối chiếu phân phối","Diễn giải"]
    st.html(f'<header class="guide"><small>Bước {step+2} / 8</small><h2>{titles[step]}</h2></header>')
    with st.container(horizontal=True):
        st.button("Trước",on_click=advance,args=(-1,),disabled=step==0)
        st.button("Tiếp",on_click=advance,args=(1,),disabled=step==6,type="primary")
        st.button("Từ đầu",on_click=move,args=(0,))
        st.button("Chọn ví dụ khác",on_click=lambda:st.session_state.update(example=None,step=0))
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
    provenance(r)


def guided_question(r):
    if r["dataset"] == "synthetic-sequence":
        return "Điều gì xảy ra trên một chuỗi tuần tự?"
    base, masked = r["probabilities"][:2]
    if base.index(max(base)) != masked.index(max(masked)):
        return "Che vị trí nào khiến mô hình đổi dự đoán?"
    return "Giữ nguyên nhãn thì xác suất có đổi không?"


def overview():
    opening(PAGES[2], PAGES[1])


def explanation():
    live(explain=True)


st.set_page_config(page_title="ProcessTransformer", layout="wide")
PAGES = [
    st.Page(overview, title="Tổng quan", default=True),
    st.Page(architecture, title="Kiến trúc", url_path="kien-truc"),
    st.Page(live, title="Mô hình", url_path="mo-hinh"),
    st.Page(explanation, title="Giải thích", url_path="giai-thich"),
    st.Page(guided, title="Dẫn giải", url_path="dan-giai"),
    st.Page(findings, title="Kết quả", url_path="ket-qua"),
]
active = st.navigation(PAGES, position="hidden")
st.set_page_config(page_title=f"{active.title} · ProcessTransformer")
st.html((HERE/"style.html").read_text("utf8"))
st.html(f'<style>.st-key-links a[href="{active.url_path}"] {{border-bottom:2px solid var(--teal)}}</style>')
with st.container(key="shell"):
    brand, nav = st.columns([1, 1.8], vertical_alignment="center")
    with brand:
        st.html("""<div class="brand"><img width="32" height="32" alt="" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGFyaWEtaGlkZGVuPSJ0cnVlIiB2aWV3Qm94PSIwIDAgNDAgMzIiPjxwYXRoIGQ9Ik00IDIzUTE2IC01IDM1IDEyTTQgMjNoMTVsMTYgLTExIiBmaWxsPSJub25lIiBzdHJva2U9IiMxNzY1NTMiIHN0cm9rZS13aWR0aD0iMS44Ii8+PGcgZmlsbD0iIzE3NjU1MyI+PGNpcmNsZSBjeD0iNCIgY3k9IjIzIiByPSIzIi8+PGNpcmNsZSBjeD0iMTkiIGN5PSIyMyIgcj0iMyIvPjxjaXJjbGUgY3g9IjM1IiBjeT0iMTIiIHI9IjMiLz48L2c+PC9zdmc+"><span>ProcessTransformer<small>Next Activity Prediction / XAI</small></span></div>""")
    with nav, st.container(horizontal=True, horizontal_alignment="right", gap="small", key="links"):
        for item in PAGES:
            st.page_link(item, label=item.title)
active.run()
