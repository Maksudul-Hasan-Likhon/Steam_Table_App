import streamlit as st
import numpy as np
import time  # সময় পরিমাপের জন্য নতুন মডিউল যোগ করা হলো

# ১. ব্যাকএন্ড ইঞ্জিন (Cubic Spline Calculations)
@st.cache_data 
def calculate_spline_coefficients():
    x = [0.01, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 295, 300, 305, 310, 315, 320, 325, 330, 335, 340, 345, 350, 355, 360, 365, 370]
    a = [0.6117, 0.8725, 1.2281, 1.7057, 2.3392, 3.1698, 4.2469, 5.6291, 7.3851, 9.5953, 12.352, 15.763, 19.947, 25.043, 31.202, 38.597, 47.416, 57.868, 70.183, 84.609, 101.42, 120.9, 143.38, 169.18, 198.67, 232.23, 270.28, 313.22, 361.53, 415.68, 476.16, 543.49, 618.23, 700.93, 792.18, 892.6, 1002.8, 1123.5, 1255.2, 1398.8, 1554.9, 1724.3, 1907.7, 2105.9, 2319.6, 2549.7, 2797.1, 3062.6, 3347.0, 3651.2, 3976.2, 4322.9, 4692.3, 5085.3, 5503.0, 5946.4, 6416.6, 6914.6, 7441.8, 7999.0, 8587.9, 9209.4, 9865.0, 10556, 11284, 12051, 12858, 13707, 14601, 15541, 16529, 17570, 18666, 19822, 21044]
    n = len(x)
    
    h = [x[i+1] - x[i] for i in range(n-1)]
    A_mat = np.zeros((n, n))
    b_mat = np.zeros((n, 1))
    A_mat[0, 0] = 1
    A_mat[n-1, n-1] = 1
    
    for i in range(1, n-1):
        A_mat[i, i-1] = h[i-1]
        A_mat[i, i] = 2 * (h[i-1] + h[i])
        A_mat[i, i+1] = h[i]
        b_mat[i, 0] = (3/h[i])*(a[i+1]-a[i]) - (3/h[i-1])*(a[i]-a[i-1])

    c = np.linalg.solve(A_mat, b_mat)
    
    b = np.zeros((n, 1))
    d = np.zeros((n, 1))
    for i in range(n-1):
        b[i, 0] = (1/h[i])*(a[i+1]-a[i]) - (h[i]/3)*(c[i+1, 0] + 2*c[i, 0])
        d[i, 0] = (1 / (3 * h[i])) * (c[i+1, 0] - c[i, 0])
        
    return x, a, b, c, d, n

# ২. সফটওয়্যার ইন্টারফেস (Frontend UI)
st.set_page_config(page_title="Cubic Spline Interpolator", layout="centered")

st.title("🌡️ Temperature to Pressure Converter")
st.write("Cubic Spline Interpolation ব্যবহার করে যেকোনো তাপমাত্রার সঠিক চাপ বের করুন।")
st.markdown("---")

# ডাটা লোড করা
x, a, b, c, d, n = calculate_spline_coefficients()

t_input = st.number_input(
    f"তাপমাত্রা ইনপুট দিন ({x[0]}°C থেকে {x[-1]}°C এর মধ্যে):", 
    min_value=float(x[0]), 
    max_value=float(x[-1]), 
    value=150.0, 
    step=0.1
)

# ক্যালকুলেশন বাটন
if st.button("চাপ নির্ণয় করুন (Predict)", type="primary"):
    
    # ⏱️ সময় গণনা শুরু
    start_time = time.perf_counter()
    
    # সঠিক ইন্টারভ্যাল খুঁজে বের করা
    idx = 0
    for i in range(n-1):
        if t_input >= x[i] and t_input <= x[i+1]:
            idx = i
            break
            
    # ইন্টারপোলেশন হিসাব
    dx = t_input - x[idx]
    predicted_p = a[idx] + b[idx, 0]*dx + c[idx, 0]*(dx**2) + d[idx, 0]*(dx**3)
    
    # ⏱️ সময় গণনা শেষ
    end_time = time.perf_counter()
    
    # মোট কত সময় লাগলো (সেকেন্ডে)
    execution_time = end_time - start_time
    
    # রেজাল্ট স্ক্রিনে দেখানো
    st.success(f"**ফলাফল:**")
    col1, col2 = st.columns(2)
    col1.metric("ইনপুট তাপমাত্রা (T)", f"{t_input} °C")
    col2.metric("নির্ণীত চাপ (P)", f"{predicted_p:.4f} kPa")
    
    # রান-টাইম স্ক্রিনে প্রদর্শন করা (মিলিসেকেন্ডে রূপান্তর করে দেখানো হলো যেন বুঝতে সুবিধা হয়)
    st.write(f"⏱️ **এই হিসাবটি করতে সফটওয়্যারের সময় লেগেছে:** `{execution_time * 1000:.4f}` মিলিসেকেন্ড (বা `{execution_time:.6f}` সেকেন্ড)")
    st.info(f"এই মানটি ইন্টারভ্যাল `[{x[idx]}, {x[idx+1]}]` এর কিউবিক স্প্লাইন সমীকরণ থেকে নেওয়া হয়েছে।")
