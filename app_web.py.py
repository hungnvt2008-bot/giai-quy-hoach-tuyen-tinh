import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

# Cấu hình trang web
st.set_page_config(
    page_title="Phần mềm Quy hoạch Tuyến tính Lớp 10",
    page_icon="📐",
    layout="centered"
)

# Khởi tạo trạng thái Session State cho nút Làm mới
if "reset_trigger" not in st.session_state:
    st.session_state.reset_trigger = 0

def reset_app():
    st.session_state.num_rows = 2
    st.session_state.reset_trigger += 1

st.title("📐 Phần mềm Quy hoạch Tuyến tính Lớp 10")
st.markdown("**Hệ thống giải toán & Vẽ đồ thị miền nghiệm chuẩn sách giáo khoa (KHKT Edition)**")
st.markdown("---")

# Nút giải bài toán khác / làm mới
if st.button("🔄 Giải bài toán khác (Làm mới trang)", use_container_width=True):
    reset_app()
    st.rerun()

# 1. Nhập hàm mục tiêu (Mặc định để trống / giá trị None)
st.subheader("1. Cấu hình Hàm mục tiêu F(x, y)")
col_a1, col_a2, col_a3 = st.columns([3, 3, 2])
with col_a1:
    coef_a_input = st.text_input("Hệ số a (của x)", value="", placeholder="Nhập số...")
with col_a2:
    coef_b_input = st.text_input("Hệ số b (của y)", value="", placeholder="Nhập số...")
with col_a3:
    mode = st.selectbox("Yêu cầu", ["Max", "Min"])

# 2. Nhập hệ bất phương trình
st.subheader("2. Hệ bất phương trình ràng buộc (a*x + b*y <= c)")

if "num_rows" not in st.session_state:
    st.session_state.num_rows = 2

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("➕ Thêm Bất phương trình"):
        st.session_state.num_rows += 1
with col_btn2:
    if st.button("➖ Xóa dòng cuối") and st.session_state.num_rows > 1:
        st.session_state.num_rows -= 1

constraints_input = []

for i in range(st.session_state.num_rows):
    c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
    
    with c1:
        a_str = st.text_input(f"a_{i+1}", value="", placeholder="0", key=f"a_{i}_{st.session_state.reset_trigger}")
    with c2:
        b_str = st.text_input(f"b_{i+1}", value="", placeholder="0", key=f"b_{i}_{st.session_state.reset_trigger}")
    with c3:
        op = st.selectbox(f"op_{i+1}", ["<=", ">=", "<", ">"], key=f"op_{i}_{st.session_state.reset_trigger}")
    with c4:
        c_str = st.text_input(f"c_{i+1}", value="", placeholder="0", key=f"c_{i}_{st.session_state.reset_trigger}")
        
    constraints_input.append((a_str, b_str, op, c_str))

st.markdown("---")

# 3. Nút bấm tính toán
if st.button("🚀 Giải Toán & Vẽ Đồ Thị", type="primary", use_container_width=True):
    try:
        coef_a = float(coef_a_input) if coef_a_input.strip() else 0.0
        coef_b = float(coef_b_input) if coef_b_input.strip() else 0.0
    except ValueError:
        st.error("⚠️ Hệ số hàm mục tiêu phải là số thực hợp lệ!")
        st.stop()

    processed_constraints = []
    has_error = False

    for a_str, b_str, op, c_str in constraints_input:
        if not a_str.strip() and not b_str.strip() and not c_str.strip():
            continue
        try:
            a = float(a_str) if a_str.strip() else 0.0
            b = float(b_str) if b_str.strip() else 0.0
            c = float(c_str) if c_str.strip() else 0.0
            processed_constraints.append((a, b, op, c))
        except ValueError:
            has_error = True

    if has_error:
        st.error("⚠️ Các hệ số trong bất phương trình phải là số hợp lệ!")
        st.stop()

    # Thêm điều kiện mặc định x >= 0, y >= 0
    all_constraints = list(processed_constraints)
    all_constraints.append((1.0, 0.0, ">=", 0.0))
    all_constraints.append((0.0, 1.0, ">=", 0.0))

    # Thuật toán quét và tìm giao điểm
    A_list, B_list, C_list = [], [], []
    for a, b, op, c in all_constraints:
        A_list.append(a)
        B_list.append(b)
        C_list.append(c)

    n = len(A_list)
    points = []
    for i in range(n):
        for j in range(i + 1, n):
            a1, b1, c1 = A_list[i], B_list[i], C_list[i]
            a2, b2, c2 = A_list[j], B_list[j], C_list[j]
            det = a1 * b2 - a2 * b1
            if abs(det) > 1e-5:
                x = (c1 * b2 - c2 * b1) / det
                y = (a1 * c2 - a2 * c1) / det

                valid = True
                for a, b, op, c in all_constraints:
                    val = a * x + b * y
                    if op == '<=' and val > c + 1e-4: valid = False; break
                    elif op == '>=' and val < c - 1e-4: valid = False; break
                    elif op == '<' and val >= c - 1e-4: valid = False; break
                    elif op == '>' and val <= c - 1e-4: valid = False; break

                if x < -1e-4 or y < -1e-4: valid = False

                if valid:
                    points.append((round(x, 4), round(y, 4)))

    points = list(set(points))
    
    if len(points) < 3:
        st.error("⚠️ Miền nghiệm rỗng hoặc không bị chặn! Vui lòng kiểm tra lại hệ bất phương trình.")
    else:
        try:
            poly = Polygon(points).convex_hull
            if poly.geom_type == 'Polygon':
                x_poly, y_poly = poly.exterior.xy
                valid_vertices = list(zip(x_poly, y_poly))[:-1]
            else:
                valid_vertices = points
        except Exception:
            valid_vertices = points
            poly = None

        is_max = (mode == "Max")
        best_val = -float('inf') if is_max else float('inf')
        best_pt = None
        results = []

        for pt in valid_vertices:
            val = coef_a * pt[0] + coef_b * pt[1]
            results.append((pt, val))
            if is_max:
                if val > best_val:
                    best_val = val
                    best_pt = pt
            else:
                if val < best_val:
                    best_val = val
                    best_pt = pt

        # Hiển thị kết quả
        st.success("✨ GIẢI THÀNH CÔNG!")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.subheader("📊 Giá trị tại các đỉnh:")
            for idx, (pt, val) in enumerate(results, 1):
                st.write(f"- **Đỉnh {idx}**: $P({pt[0]}, {pt[1]})$ $\rightarrow F = {val}$")
                
        with col_res2:
            st.subheader(f"🎯 KẾT QUẢ {mode.upper()}:")
            st.markdown(f"### $F_{{max}} = {best_val}$" if is_max else f"### $F_{{min}} = {best_val}$")
            st.markdown(f"**Tại điểm:** $P({best_pt[0]}; {best_pt[1]})$")

        # Vẽ đồ thị Matplotlib chuẩn sách giáo khoa
        st.subheader("📈 Đồ thị Miền Nghiệm")
        fig, ax = plt.subplots(figsize=(7, 6))
        
        if poly and poly.geom_type == 'Polygon':
            xp, yp = poly.exterior.xy
            ax.fill(xp, yp, color='#1f77b4', alpha=0.25, label='Miền nghiệm')
            ax.plot(xp, yp, color='#1f77b4', linewidth=2.5)

        all_x = [pt[0] for pt in valid_vertices]
        max_x = max(all_x) if all_x else 10
        x_vals = np.linspace(-2, max_x * 1.3, 400)
        
        for a, b, op, c in processed_constraints:
            if abs(b) > 1e-5:
                y_vals = (c - a * x_vals) / b
                ax.plot(x_vals, y_vals, linestyle='--', linewidth=1.5, label=f"{a}x + {b}y {op} {c}")
            else:
                x_const = c / a if abs(a) > 1e-5 else 0
                ax.axvline(x=x_const, linestyle='--', linewidth=1.5, label=f"x {op} {x_const}")

        for idx, pt in enumerate(valid_vertices, 1):
            ax.plot(pt[0], pt[1], 'ro', markersize=6)
            ax.text(pt[0] + 0.3, pt[1] + 0.3, f"P{idx}({pt[0]},{pt[1]})", fontsize=9, fontweight='bold', color='darkred')

        ax.plot(best_pt[0], best_pt[1], marker='*', markersize=16, color='green', label='Điểm tối ưu')

        ax.axhline(0, color='black', linewidth=1.2)
        ax.axvline(0, color='black', linewidth=1.2)
        ax.grid(True, linestyle=':', alpha=0.7)
        ax.set_title("Đồ thị Miền Nghiệm Quy Hoạch Tuyến Tính", fontsize=12, fontweight='bold', pad=10)
        ax.legend(loc='upper right', fontsize=8)

        st.pyplot(fig)