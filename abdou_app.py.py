import streamlit as st
import requests
import datetime

# 1. إعدادات الواجهة
st.set_page_config(page_title="حاسبة الكهرباء - Abdou", layout="centered")
st.title("⚡ حاسبة كهرباء المنازل - النسخة الاحترافية")

# 2. القائمة الجانبية للأسعار
with st.sidebar:
    st.header("⚙️ إعدادات الأسعار")
    p_lamp = st.number_input("سعر اللمبة (دج)", value=600)
    p_socket = st.number_input("سعر المقبس (دج)", value=500)
    p_tab = st.number_input("سعر الطابلو (دج)", value=5000)

# 3. إدخال بيانات المشروع والولاية
wilayas = ["أدرار","الشلف","الأغواط","أم البواقي","باتنة","بجاية","بسكرة","بشار","البليدة","البويرة","تمنراست","تبسة","تلمسان","تيارت","تيزي وزو","الجزائر","الجلفة","جيجل","سطيف","سعيدة","سكيكدة","سيدي بلعباس","عنابة","قالمة","قسنطينة","المدية","مستغانم","المسيلة","معسكر","ورقلة","وهران","البيض","إليزي","برج بوعريريج","بومرداس","الطارف","تندوف","تيسمسيلت","الوادي","خنشلة","سوق أهراس","تيبازة","ميلة","عين الدفلى","النعامة","عين تموشنت","غرداية","غليزان","تميمون","برج باجي مختار","أولاد جلال","بني عباس","عين صالح","عين قزام","توقرت","جانت","المغير","المنيعة"]
selected_wilaya = st.selectbox("📍 اختر الولاية:", wilayas)
num_areas = st.number_input("كم عدد المناطق (الغرف)؟", min_value=1, value=3)

# 4. حساب الكميات (المقابس واللمبات)
total_s, total_l = 0, 0
for i in range(int(num_areas)):
    with st.expander(f"تفاصيل المنطقة {i+1}", expanded=True):
        col1, col2 = st.columns(2)
        total_s += col1.number_input(f"المقابس {i+1}", min_value=0, key=f"s{i}")
        total_l += col2.number_input(f"اللمبات {i+1}", min_value=0, key=f"l{i}")

extra_items = st.text_input("📦 إضافات أخرى (سبوت لايت، تأريض...):")

# 5. منطق الحساب المالي
labor_cost = (total_l * p_lamp) + (total_s * p_socket) + (num_areas * p_socket) + p_tab

# 6. دالة الحفظ السحرية (Google Form)
def send_to_google_form(wilaya, sockets, lamps, cost, extra, price):
    url = "https://docs.google.com/forms/d/e/1FAIpQLScqRucA9vRy51Vy6QEvKHJmNYNnauc0ES3pr3LGmOpVOvN4rw/formResponse"
    
    payload = {
        "entry.2021402897": wilaya,
        "entry.2023855562": str(sockets),
        "entry.528214977": str(lamps),
        "entry.1353071652": str(cost),
        "entry.1960991695": str(extra),
        "entry.675027177": str(price)
    }
    
    try:
        # أضفنا تحويل القيم إلى نصوص (str) لضمان قبولها
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            st.warning(f"تنبيه: كود الحالة هو {response.status_code}")
        return response.ok
    except Exception as e:
        st.error(f"خطأ تقني: {e}")
        return False
# 7. التنفيذ والنتائج
if st.button(" إصدار التقرير "):
    st.markdown("---")
    st.success(f"### إجمالي تكلفة اليد العاملة: {labor_cost:,} دج")
    
    if save_data():
        st.balloons()
        st.info("✅ تم تسجيل البيانات بنجاح في جدول جوجل!")
    else:
        st.error("❌ فشل التسجيل التلقائي، يرجى التحقق من الأرقام.")

    st.write(f"📦 المشتريات: أسلاك 2.5 ملم ({max(1, int(total_s/10))} لفة) | أسلاك 1.5 ملم ({max(1, int(total_l/12))} لفة)")
