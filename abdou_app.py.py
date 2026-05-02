import streamlit as st

st.set_page_config(page_title="حاسبة الكهرباء - Abdou", layout="centered")

st.title("⚡ حاسبة كهرباء المنازل (نسخة العمل العادي)")

# إعدادات الأسعار في القائمة الجانبية
with st.sidebar:
    st.header("⚙️ إعدادات الأسعار")
    p_lamp = st.number_input("سعر اللمبة (دج)", value=500)
    p_socket = st.number_input("سعر المقبس/العلبة (دج)", value=500)
    p_tab = st.number_input("سعر الطابلو (دج)", value=3000)

# إدخال بيانات الغرف
st.subheader("🏠 إدخال بيانات الغرف")
num_areas = st.number_input("كم عدد المناطق في المنزل؟", min_value=1, value=5, step=1)

all_data = []
total_s = 0
total_l = 0

for i in range(int(num_areas)):
    with st.expander(f"بيانات المنطقة {i+1}", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            s = st.number_input(f"عدد المقابس", min_value=0, step=1, key=f"s{i}")
        with col2:
            l = st.number_input(f"عدد اللمبات", min_value=0, step=1, key=f"l{i}")
        total_s += s
        total_l += l

# الحسابات بناءً على منطق الورقة
total_jb = num_areas  # علبة تفريع لكل غرفة
labor_cost = (total_l * p_lamp) + (total_s * p_socket) + (total_jb * p_socket) + p_tab
breaker_slots = num_areas + 4 # 4 هي القواطع الإضافية والحماية

# عرض النتائج
if st.button("إصدار التقرير النهائي"):
    st.markdown("---")
    st.success(f"### إجمالي اليد العاملة: {labor_cost:,} دج")
    
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.info("📦 قائمة المشتريات:")
        st.write(f"- سلك 2.5 ملم: 2 لفة")
        st.write(f"- سلك 1.5 ملم: 2 لفة")
        st.write(f"- خراطيم 16 ملم: 1 لفة")
        st.write(f"- خراطيم 12 ملم: 1 لفة")
        st.write(f"- علب تثبيت (Pot): {int(total_s + total_l + total_jb)} قطعة")
    
    with col_res2:
        st.warning("🔌 تفاصيل اللوحة:")
        st.write(f"- لوحة التوزيع: {int(breaker_slots)}P")
        st.write(f"- إجمالي المقابس: {int(total_s)}")
        st.write(f"- إجمالي اللمبات: {int(total_l)}")