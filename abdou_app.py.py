import streamlit as st
import requests

# ─────────────────────────────────────────────
# 1. إعدادات الصفحة
# ─────────────────────────────────────────────
st.set_page_config(page_title="Abdou Electric Calc", layout="centered")

# ─────────────────────────────────────────────
# 2. بيانات التدريب لحساب السلك (من جدول الكميات)
# ─────────────────────────────────────────────
TRAINING_DATA = [
    {"area": 20,   "rooms": 1, "wire15": 0.30, "wire25": 0.01, "boxes": 1},
    {"area": 25,   "rooms": 1, "wire15": 0.11, "wire25": 0.50, "boxes": 1},
    {"area": 21.6, "rooms": 1, "wire15": 0.30, "wire25": 0.00, "boxes": 0},
    {"area": 100,  "rooms": 4, "wire15": 3.00, "wire25": 3.00, "boxes": 5},
    {"area": 88,   "rooms": 5, "wire15": 2.00, "wire25": 0.20, "boxes": 5},
]

def get_coefficients():
    """استخراج معاملات الحساب من بيانات التدريب"""
    sum_area  = sum(d["area"]   for d in TRAINING_DATA)
    sum_rooms = sum(d["rooms"]  for d in TRAINING_DATA)
    sum_w15   = sum(d["wire15"] for d in TRAINING_DATA)
    sum_w25   = sum(d["wire25"] for d in TRAINING_DATA)
    return {
        "w15_per_m2":   sum_w15 / sum_area,
        "w25_per_m2":   sum_w25 / sum_area,
        "w15_per_room": sum_w15 / sum_rooms,
        "w25_per_room": sum_w25 / sum_rooms,
    }

def calc_wire_and_boxes(total_area, total_rooms, pts_per_room=6, pts_per_box=5):
    """حساب لفات السلك وعلب التفريع"""
    c = get_coefficients()
    raw15 = (c["w15_per_m2"] * total_area + c["w15_per_room"] * total_rooms) / 2
    raw25 = (c["w25_per_m2"] * total_area + c["w25_per_room"] * total_rooms) / 2
    laps15 = round(raw15 * 10) / 10
    laps25 = round(raw25 * 10) / 10
    total_pts = total_rooms * pts_per_room
    boxes = -(-total_pts // pts_per_box)  # ceiling division
    return laps15, laps25, int(boxes), total_pts

# ─────────────────────────────────────────────
# 3. دالة الحفظ في Google Forms
# ─────────────────────────────────────────────
def save_data(wilaya, sockets, lamps, cost, extra, price):
    url = "https://docs.google.com/forms/d/e/1FAIpQLScqRucA9vRy51Vy6QEvKHJmNYNnauc0ES3pr3LGmOpVOvN4rw/formResponse"
    payload = {
        "entry.2021402897": str(wilaya),
        "entry.2023855562": str(sockets),
        "entry.528214977":  str(lamps),
        "entry.1353071652": str(cost),
        "entry.1960991695": str(extra),
        "entry.675027177":  str(price),
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        response = requests.post(url, data=payload, headers=headers)
        return response.ok
    except:
        return False

# ─────────────────────────────────────────────
# 4. الشريط الجانبي – الأسعار والإعدادات
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ إعدادات الأسعار")
    p_lamp   = st.number_input("سعر اللمبة (دج)",   value=600)
    p_socket = st.number_input("سعر المقبس (دج)",   value=500)
    p_tab    = st.number_input("سعر الطابلو (دج)",  value=5000)

    st.markdown("---")
    st.header("🧮 إعدادات حساب السلك")
    pts_per_room = st.number_input("نقاط لكل غرفة",       min_value=1, value=6)
    pts_per_box  = st.number_input("نقاط لكل علبة تفريع", min_value=1, value=5)

# ─────────────────────────────────────────────
# 5. واجهة المستخدم الرئيسية
# ─────────────────────────────────────────────
st.title("⚡ حاسبة كهرباء المنازل - Abdou")

wilayas = [
    "أدرار","الشلف","الأغواط","أم البواقي","باتنة","بجاية","بسكرة","بشار",
    "البليدة","البويرة","تمنراست","تبسة","تلمسان","تيارت","تيزي وزو","الجزائر",
    "الجلفة","جيجل","سطيف","سعيدة","سكيكدة","سيدي بلعباس","عنابة","قالمة",
    "قسنطينة","المدية","مستغانم","المسيلة","معسكر","ورقلة","وهران","البيض",
    "إليزي","برج بوعريريج","بومرداس","الطارف","تندوف","تيسمسيلت","الوادي",
    "خنشلة","سوق أهراس","تيبازة","ميلة","عين الدفلى","النعامة","عين تموشنت",
    "غرداية","غليزان","تميمون","برج باجي مختار","أولاد جلال","بني عباس",
    "عين صالح","عين قزام","توقرت","جانت","المغير","المنيعة",
]
selected_wilaya = st.selectbox("📍 اختر الولاية:", wilayas)

num_areas = st.number_input("كم عدد المناطق (الغرف)؟", min_value=1, value=3)

# ─── جمع بيانات كل غرفة ───
total_s, total_l, total_area_m2 = 0, 0, 0.0

for i in range(int(num_areas)):
    with st.expander(f"تفاصيل المنطقة {i+1}", expanded=True):
        col1, col2, col3 = st.columns(3)
        total_s      += col1.number_input(f"المقابس {i+1}",       min_value=0,   key=f"s{i}")
        total_l      += col2.number_input(f"اللمبات {i+1}",       min_value=0,   key=f"l{i}")
        total_area_m2 += col3.number_input(f"المساحة م² {i+1}", min_value=0.0, key=f"a{i}", step=1.0)

extra_items = st.text_input("📦 إضافات أخرى:")

# ─────────────────────────────────────────────
# 6. الحساب
# ─────────────────────────────────────────────
labor_cost = (total_l * p_lamp) + (total_s * p_socket) + (num_areas * p_socket) + p_tab

laps15, laps25, boxes, total_pts = calc_wire_and_boxes(
    total_area_m2, int(num_areas), int(pts_per_room), int(pts_per_box)
)

# ─── عرض مؤشرات السلك في الوقت الفعلي ───
st.markdown("---")
st.subheader("📦 تقدير المواد (يتحدث تلقائياً)")

c1, c2, c3, c4 = st.columns(4)
c1.metric("سلك 1.5",        f"{laps15:.1f} لفة",  f"≈ {int(laps15*100)} م")
c2.metric("سلك 2.5",        f"{laps25:.1f} لفة",  f"≈ {int(laps25*100)} م")
c3.metric("علب التفريع BD", f"{boxes} علبة")
c4.metric("إجمالي النقاط",  f"{total_pts} نقطة")

# ─────────────────────────────────────────────
# 7. إصدار التقرير والحفظ
# ─────────────────────────────────────────────
st.markdown("---")
if st.button("🚀 إصدار التقرير وحفظ البيانات"):
    st.success(f"### إجمالي تكلفة اليد العاملة: {labor_cost:,} دج")

    st.markdown("#### ملخص المواد المطلوبة")
    st.table({
        "المادة":    ["سلك 1.5 مم",          "سلك 2.5 مم",          "علب التفريع BD"],
        "الكمية":   [f"{laps15:.1f} لفة",    f"{laps25:.1f} لفة",   f"{boxes} علبة"],
        "بالمتر":   [f"{int(laps15*100)} م", f"{int(laps25*100)} م", "—"],
    })

    summary = (
        f"سلك1.5={laps15}لفة | سلك2.5={laps25}لفة | "
        f"علبتفريع={boxes} | نقاط={total_pts} | {extra_items}"
    )

    if save_data(selected_wilaya, total_s, total_l, labor_cost, summary, p_socket):
        st.balloons()
        st.info("✅ تم تسجيل البيانات بنجاح في جدول جوجل!")
    else:
        st.error("❌ فشل التسجيل، تأكد من تحديث التطبيق أو الاتصال.")
