import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# إعداد الصفحة وتصميمها
st.set_page_config(page_title="حاسبة الكهرباء - ING BRAHIM", layout="centered")

# الربط مع قاعدة بيانات جوجل (الجدول الذي أرسلته)
# الرابط يتم سحبه تلقائياً من الـ Secrets التي وضعناها
conn = st.connection("gsheets", type=GSheetsConnection)

st.title(" حاسبة كهرباء المنازل (النسخة الشاملة)")

# --- القائمة الجانبية لإعدادات الأسعار ---
with st.sidebar:
    st.header("⚙️ إعدادات الأسعار")
    p_lamp = st.number_input("سعر اللمبة (دج)", value=600)
    p_socket = st.number_input("سعر المقبس/العلبة (دج)", value=500)
    p_tab = st.number_input("سعر الطابلو (دج)", value=5000)
    st.markdown("---")
    st.write("👤 المطور: **Abdou**")

# --- إدخال البيانات الأساسية ---
st.subheader("📍 معلومات المشروع")
wilayas = ["أدرار","الشلف","الأغواط","أم البواقي","باتنة","بجاية","بسكرة","بشار","البليدة","البويرة","تمنراست","تبسة","تلمسان","تيارت","تيزي وزو","الجزائر","الجلفة","جيجل","سطيف","سعيدة","سكيكدة","سيدي بلعباس","عنابة","قالمة","قسنطينة","المدية","مستغانم","المسيلة","معسكر","ورقلة","وهران","البيض","إليزي","برج بوعريريج","بومرداس","الطارف","تندوف","تيسمسيلت","الوادي","خنشلة","سوق أهراس","تيبازة","ميلة","عين الدفلى","النعامة","عين تموشنت","غرداية","غليزان","تميمون","برج باجي مختار","أولاد جلال","بني عباس","عين صالح","عين قزام","توقرت","جانت","المغير","المنيعة"]
selected_wilaya = st.selectbox("اختر الولاية:", wilayas)
num_areas = st.number_input("كم عدد المناطق (الغرف) في المنزل؟", min_value=1, value=5, step=1)

# --- حساب السلع والعمل ---
total_s = 0
total_l = 0

for i in range(int(num_areas)):
    with st.expander(f"تفاصيل المنطقة {i+1}", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            s = st.number_input(f"عدد المقابس", min_value=0, step=1, key=f"s{i}")
        with col2:
            l = st.number_input(f"عدد اللمبات", min_value=0, step=1, key=f"l{i}")
        total_s += s
        total_l += l

# قسم السلع الإضافية (بناءً على طلبك)
st.subheader("📦 تخصيص المشتريات")
custom_options = st.multiselect(
    "اختر إضافات للمشروع:",
    ["تأريض (Earth)", "أضواء سبوت لايت", "مفاتيح ذكية", "لوحة 24P", "أسلاك 4 ملم", "أشرطة LED"]
)
manual_input = st.text_input("هل تريد إضافة سلع أخرى؟ (اكتبها هنا)")

# --- منطق الحساب البرمجي ---
total_jb = num_areas 
labor_cost = (total_l * p_lamp) + (total_s * p_socket) + (total_jb * p_socket) + p_tab
extra_items_str = ", ".join(custom_options) + (f" | {manual_input}" if manual_input else "")

# --- عرض التقرير النهائي وحفظ البيانات ---
if st.button("إصدار التقرير وحفظ البيانات"):
    st.markdown("---")
    st.success(f"### إجمالي تكلفة اليد العاملة: {labor_cost:,} دج")
    
    # حفظ البيانات في جدول جوجل (Sheet1)
    try:
        new_row = pd.DataFrame([{
            "المنطقة": selected_wilaya,
            "عدد المقابس": int(total_s),
            "عدد اللمبات": int(total_l),
            "التكلفة الإجمالية": f"{labor_cost:,} دج",
            "السلع الإضافية": extra_items_str,
            "التاريخ": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "السعر": p_socket
        }])
        
        # جلب البيانات القديمة ودمج الجديدة
        existing_df = conn.read()
        updated_df = pd.concat([existing_df, new_row], ignore_index=True)
        conn.update(data=updated_df)
        st.info(f"✅ تم تسجيل البيانات بنجاح لولاية {selected_wilaya} في جدولك الخاص.")
    except Exception as e:
        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")

    # عرض قائمة المشتريات التقديرية
    st.info("📦 قائمة المشتريات المقترحة:")
    st.write(f"- سلك 2.5 ملم: {max(1, int(total_s/10))} لفة")
    st.write(f"- سلك 1.5 ملم: {max(1, int(total_l/12))} لفة")
    if extra_items_str:
        st.write(f"- إضافاتك: {extra_items_str}")
