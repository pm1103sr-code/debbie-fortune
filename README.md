# DEBBIE妹妹算命站 V1

Python + Streamlit + Gemini 3.8 Flash。

## 功能
- 姓名、生日、出生時間、出生地
- Python 計算四柱八字
- 面相正面照、左右手掌照片上傳
- Gemini 多模態娛樂性綜合解讀
- 紫微斗數 UI/資料介面已建立，但**正式排盤器尚未啟用**；在流派規則固定前，程式不會讓 AI 猜命盤或格局。

## Windows 安裝
```bash
py -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

複製 `.streamlit/secrets.toml.example` 為 `.streamlit/secrets.toml`，填入 API Key。

啟動：
```bash
streamlit run app.py
```

## 下一版：紫微斗數 deterministic engine
需先固定：
1. 曆法/農曆轉換規則
2. 子初換日或子正換日
3. 閏月處理
4. 真太陽時是否校正
5. 命宮/身宮與五行局規則
6. 十四主星、輔曜煞曜安星表
7. 生年四化表
8. 格局清單與判定條件
9. 大限/流年規則

完成後 `fortune.py::ziwei_placeholder()` 可直接替換為正式排盤器。
