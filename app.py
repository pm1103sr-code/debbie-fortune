from datetime import date, time, datetime
import streamlit as st
from config import APP_NAME, DISCLAIMER, GEMINI_MODEL
from fortune import calculate_bazi, calculate_ziwei
from ai import analyze

st.set_page_config(page_title=APP_NAME, page_icon="🔮", layout="wide")
st.title(f"🔮 {APP_NAME}")
st.caption("紫微斗數 × 八字 × 面相 × 手相｜傳統文化娛樂體驗")
st.info(DISCLAIMER)

with st.sidebar:
    st.header("基本資料")
    name = st.text_input("姓名 / 暱稱")
    gender = st.selectbox("性別（供傳統排盤規則使用）", ["女", "男"])
    birth_date = st.date_input("出生日期", value=date(2000, 1, 1), min_value=date(1900,1,1), max_value=date.today())
    birth_time = st.time_input("出生時間", value=time(12, 0))
    birthplace = st.text_input("出生地（城市）", placeholder="例如：台北市")
    st.caption("V1 先以輸入的當地民用時間計算八字；紫微正式版會再加入時區/真太陽時選項。")
    consent = st.checkbox("我同意將本次輸入與照片傳送至 AI 進行本次分析")

st.subheader("📷 照片（選填）")
c1, c2, c3 = st.columns(3)
with c1:
    face = st.file_uploader("面相正面照", type=["jpg","jpeg","png"], key="face")
with c2:
    left = st.file_uploader("左手掌", type=["jpg","jpeg","png"], key="left")
with c3:
    right = st.file_uploader("右手掌", type=["jpg","jpeg","png"], key="right")

api_key = st.secrets.get("GEMINI_API_KEY", "")
if st.button("✨ 開始 DEBBIE 分析", type="primary", use_container_width=True):
    if not name:
        st.error("請先輸入姓名或暱稱。")
    elif not consent:
        st.error("請先確認照片與資料的本次 AI 分析同意。")
    elif not api_key:
        st.error("尚未設定 GEMINI_API_KEY。")
    else:
        dt = datetime.combine(birth_date, birth_time)
        with st.spinner("正在排八字並進行 AI 綜合解讀…"):
            try:
                bazi = calculate_bazi(dt)
                ziwei = calculate_ziwei(dt, gender)
                user = {"name": name, "gender": gender, "birthplace": birthplace, "birth_datetime": dt.isoformat(sep=" ", timespec="minutes")}
                report = analyze(api_key, user, bazi, ziwei, face, left, right)
                st.session_state["bazi"] = bazi
                st.session_state["ziwei"] = ziwei
                st.session_state["report"] = report
            except Exception as e:
                st.exception(e)

if "report" in st.session_state:
    tab1, tab2, tab3 = st.tabs(["DEBBIE綜合報告", "八字命盤", "紫微斗數"])
    with tab1:
        st.markdown(st.session_state["report"])
    with tab2:
        b = st.session_state["bazi"]
        cols = st.columns(4)
        for col, label, key in zip(cols, ["年柱","月柱","日柱","時柱"], ["year_pillar","month_pillar","day_pillar","time_pillar"]):
            col.metric(label, b[key])
        st.json(b)
    with tab3:
        z = st.session_state["ziwei"]
        a,b,c,d = st.columns(4)
        a.metric("命主", z["soul_star"])
        b.metric("身主", z["body_star"])
        c.metric("五行局", z["five_elements_class"])
        d.metric("農曆", z["lunar_date"])
        st.caption(z["rules_note"])

        st.subheader("🌌 十二宮命盤")
        cols = st.columns(4)
        for i, p in enumerate(z["palaces"]):
            with cols[i % 4]:
                body = "｜身宮" if p["is_body_palace"] else ""
                st.markdown(f"### {p['name']}{body}")
                if p["stem_branch"]:
                    st.caption(p["stem_branch"])
                st.write("**主星：** " + ("、".join(p["major_stars"]) or "—"))
                if p["minor_stars"]:
                    st.write("**輔星：** " + "、".join(p["minor_stars"]))
                if p["adjective_stars"]:
                    with st.expander("其他星曜"):
                        st.write("、".join(p["adjective_stars"]))

        st.subheader("✨ 格局判定")
        if z["patterns"]:
            for hit in z["patterns"]:
                flags = []
                if hit["variant"]: flags.append(f"口徑：{hit['variant']}")
                if hit["broken"]: flags.append("破格/受制標記")
                suffix = f"（{'；'.join(flags)}）" if flags else ""
                st.markdown(f"- **{hit['name']}**｜{hit['palace']}{suffix}")
        else:
            st.info("目前規則下未命中已收錄的命名格局。")

        with st.expander("查看排盤引擎語義資料（供驗證）"):
            st.text(z["semantic_text"])

st.divider()
st.caption(f"AI 模型：{GEMINI_MODEL}｜{DISCLAIMER}")
