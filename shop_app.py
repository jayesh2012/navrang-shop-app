import streamlit as st
import pandas as pd
import datetime
import sqlite3

# Page configuration
st.set_page_config(page_title="Navrang Masala Dashboard", page_icon="🌿", layout="wide")

# Custom Styling for Modern UI & Interactive Look
st.markdown("""
    <style>
        .main-title {
            font-size: 36px;
            font-weight: bold;
            color: #D35400;
            text-align: center;
            margin-bottom: 0px;
        }
        .sub-title {
            font-size: 16px;
            color: #666666;
            text-align: center;
            margin-bottom: 25px;
        }
        .stMetric {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# Top Header / Title
st.markdown('<div class="main-title">🌿 Navrang Masala Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Smart Business Management & Analytics Tool</div>', unsafe_allow_html=True)

# Database connection setup (SQLite)
DB_FILE = "shop_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Purchase table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            suraj REAL,
            delux REAL,
            bharat REAL,
            jain REAL,
            durga REAL,
            kk_traders REAL,
            others REAL,
            total_purchase REAL
        )
    ''')
    
    # Sales table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            shop_sale REAL,
            cart_sale REAL,
            online_collection REAL,
            total_sale REAL
        )
    ''')
    
    # Monthly Expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            electricity_bill REAL,
            shop_rent REAL,
            cart_rent REAL,
            other_expense REAL,
            other_expense_desc TEXT,
            total_expense REAL
        )
    ''')

    # Supplier Credit / Udhaar Khata Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS supplier_udhaar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            supplier_name TEXT,
            amount REAL,
            status TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Sidebar Navigation with Icons
st.sidebar.title("📌 Navigation")
menu = st.sidebar.selectbox("Choose Section", ["🏠 Home & Overview", "➕ Quick Data Entry", "📒 Supplier Udhaar Khata", "📅 Reports & Analytics", "📂 Manage Database"])

# Load all data for global use safely
def load_data():
    conn = sqlite3.connect(DB_FILE)
    df_p = pd.read_sql_query("SELECT * FROM purchases", conn)
    df_s = pd.read_sql_query("SELECT * FROM sales", conn)
    df_e = pd.read_sql_query("SELECT * FROM expenses", conn)
    df_u = pd.read_sql_query("SELECT * FROM supplier_udhaar", conn)
    conn.close()
    
    for df in [df_p, df_s, df_e]:
        if not df.empty and "date" in df.columns:
            df["dt"] = pd.to_datetime(df["date"])
            df["Year"] = df["dt"].dt.year.astype(str)
            df["Month"] = df["dt"].dt.to_period("M").astype(str)
            
    if not df_u.empty and "date" in df_u.columns:
        df_u["dt"] = pd.to_datetime(df_u["date"])
        
    return df_p, df_s, df_e, df_u

df_p, df_s, df_e, df_u = load_data()

if menu == "🏠 Home & Overview":
    st.subheader("📊 Business Quick Snapshot")
    
    total_p_val = df_p["total_purchase"].sum() if not df_p.empty and "total_purchase" in df_p.columns else 0.0
    total_s_val = df_s["total_sale"].sum() if not df_s.empty and "total_sale" in df_s.columns else 0.0
    total_e_val = df_e["total_expense"].sum() if not df_e.empty and "total_expense" in df_e.columns else 0.0
    
    # Calculate Pending Udhaar
    pending_udhaar = df_u[df_u["status"] == "Pending"]["amount"].sum() if not df_u.empty and "status" in df_u.columns else 0.0
    net_bachat_val = total_s_val - (total_p_val + total_e_val)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="🛒 Total Purchase", value=f"₹ {total_p_val:,.2f}")
    with col2:
        st.metric(label="💰 Total Sales", value=f"₹ {total_s_val:,.2f}")
    with col3:
        st.metric(label="🧾 Total Expenses", value=f"₹ {total_e_val:,.2f}")
    with col4:
        st.metric(label="📒 Pending Udhaar", value=f"₹ {pending_udhaar:,.2f}")
    with col5:
        st.metric(label="💎 Net Bachat", value=f"₹ {net_bachat_val:,.2f}")
        
    st.markdown("---")
    st.info("👈 Sidebar se **'Supplier Udhaar Khata'** mein jakar aap kis se kitna udhaar liya hai aur payment status manage kar sakte hain.")

elif menu == "➕ Quick Data Entry":
    st.subheader("📝 New Entry Panel")
    tab1, tab2, tab3 = st.tabs(["🛒 Purchase Entry", "💰 Sales Entry", "🧾 Monthly Expenses"])
    
    with tab1:
        with st.form("purchase_form"):
            p_date = st.date_input("Purchase Date", datetime.date.today(), key="p_date")
            col1, col2, col3 = st.columns(3)
            with col1:
                suraj = st.number_input("Suraj (₹)", min_value=0.0, step=1.0)
                delux = st.number_input("Delux (₹)", min_value=0.0, step=1.0)
                bharat = st.number_input("Bharat (₹)", min_value=0.0, step=1.0)
            with col2:
                jain = st.number_input("Jain (₹)", min_value=0.0, step=1.0)
                durga = st.number_input("Durga (₹)", min_value=0.0, step=1.0)
                kk = st.number_input("KK Traders (₹)", min_value=0.0, step=1.0)
            with col3:
                others = st.number_input("Others (₹)", min_value=0.0, step=1.0)
                
            submit_purchase = st.form_submit_button("💾 Save Purchase Entry")
            if submit_purchase:
                total_p = suraj + delux + bharat + jain + durga + kk + others
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO purchases (date, suraj, delux, bharat, jain, durga, kk_traders, others, total_purchase)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (str(p_date), suraj, delux, bharat, jain, durga, kk, others, total_p))
                conn.commit()
                conn.close()
                st.success(f"Purchase Saved Successfully! Total: ₹{total_p}")
                st.rerun()

    with tab2:
        with st.form("sales_form"):
            s_date = st.date_input("Sales Date", datetime.date.today(), key="s_date")
            shop_sale = st.number_input("Shop Sale Amount (₹)", min_value=0.0, step=1.0)
            cart_sale = st.number_input("Cart Sale Amount (₹)", min_value=0.0, step=1.0)
            online_collection = st.number_input("Online Collection Amount (₹)", min_value=0.0, step=1.0)
            
            submit_sales = st.form_submit_button("💾 Save Sales Entry")
            if submit_sales:
                total_s = shop_sale + cart_sale + online_collection
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sales (date, shop_sale, cart_sale, online_collection, total_sale)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (str(s_date), shop_sale, cart_sale, online_collection, total_s))
                conn.commit()
                conn.close()
                st.success(f"Sales Saved Successfully! Total: ₹{total_s}")
                st.rerun()

    with tab3:
        with st.form("expense_form"):
            e_date = st.date_input("Expense Date", datetime.date.today(), key="e_date")
            col1, col2 = st.columns(2)
            with col1:
                electricity = st.number_input("Electricity Bill (₹)", min_value=0.0, step=1.0)
                shop_rent = st.number_input("Shop Rent (₹)", min_value=0.0, step=1.0)
            with col2:
                cart_rent = st.number_input("Cart Rent (₹)", min_value=0.0, step=1.0)
                other_exp = st.number_input("Other Expenses Amount (₹)", min_value=0.0, step=1.0)
            other_desc = st.text_input("Other Expenses Description (Jaise: Maintenance, Chai, etc.)")
            
            submit_expense = st.form_submit_button("💾 Save Expense Entry")
            if submit_expense:
                total_e = electricity + shop_rent + cart_rent + other_exp
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO expenses (date, electricity_bill, shop_rent, cart_rent, other_expense, other_expense_desc, total_expense)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (str(e_date), electricity, shop_rent, cart_rent, other_exp, other_desc, total_e))
                conn.commit()
                conn.close()
                st.success(f"Expense Saved Successfully! Total: ₹{total_e}")
                st.rerun()

elif menu == "📒 Supplier Udhaar Khata":
    st.subheader("📒 Maal Wale (Supplier) ka Udhaar Khata")
    
    # Form to add New Udhaar Entry
    with st.form("udhaar_entry_form"):
        st.markdown("#### ➕ Naya Udhaar Jodein")
        col1, col2, col3 = st.columns(3)
        with col1:
            u_date = st.date_input("Date", datetime.date.today())
        with col2:
            # Supplier list including option for 'Others'
            supplier_choice = st.selectbox("Supplier / Maal Wala Name", ["Suraj", "Delux", "Bharat", "Jain", "Durga", "KK Traders", "Other (Custom Name)"])
        with col3:
            u_amount = st.number_input("Udhaar Amount (₹)", min_value=0.0, step=1.0)
            
        custom_supplier = ""
        if supplier_choice == "Other (Custom Name)":
            custom_supplier = st.text_input("Enter Other Supplier Name")
            
        submit_udhaar = st.form_submit_button("💾 Save Udhaar Entry")
        if submit_udhaar:
            final_supp_name = custom_supplier if supplier_choice == "Other (Custom Name)" else supplier_choice
            if final_supp_name.strip() == "":
                st.error("Kripya supplier ka naam thik se bharein.")
            else:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO supplier_udhaar (date, supplier_name, amount, status)
                    VALUES (?, ?, ?, ?)
                ''', (str(u_date), final_supp_name, u_amount, "Pending"))
                conn.commit()
                conn.close()
                st.success(f"{final_supp_name} ka ₹{u_amount} ka udhaar successfully save ho gaya!")
                st.rerun()

    st.markdown("---")
    st.subheader("📋 Pending & Paid Udhaar Records")
    
    if not df_u.empty:
        # Filter option (All, Pending, Paid)
        status_filter = st.radio("Filter Status", ["All", "Pending", "Paid"], horizontal=True)
        if status_filter != "All":
            view_df = df_u[df_u["status"] == status_filter]
        else:
            view_df = df_u
            
        for index, row in view_df.iterrows():
            col_a, col_b, col_c, col_d, col_e = st.columns([2, 3, 2, 2, 2])
            col_a.text(f"📅 {row['date']}")
            col_b.text(f"👤 {row['supplier_name']}")
            col_c.text(f"₹ {row['amount']:,.2f}")
            
            # Status Badge Look
            if row['status'] == "Pending":
                col_d.markdown("🔴 **Pending**")
                if col_e.button("✅ Mark Paid", key=f"paid_{row['id']}"):
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE supplier_udhaar SET status = 'Paid' WHERE id = ?", (row['id'],))
                    conn.commit()
                    conn.close()
                    st.success(f"Payment marked as PAID for {row['supplier_name']}!")
                    st.rerun()
            else:
                col_d.markdown("🟢 **Paid**")
                col_e.text("Settled")
        st.markdown("---")
    else:
        st.info("Abhi tak koi udhaar entry nahi ki gayi hai.")

elif menu == "📅 Reports & Analytics":
    st.subheader("📈 Time-wise Reports & Analytics")
    
    if not df_p.empty or not df_s.empty or not df_e.empty:
        time_filter = st.selectbox("📅 Select Time Range", ["All Time", "1 Day (Specific Date)", "Last 7 Days (1 Week)", "This Month"])
        
        def apply_time_filter(df, date_col="dt"):
            if df.empty or date_col not in df.columns:
                return df
            today = pd.Timestamp(datetime.date.today())
            if time_filter == "1 Day (Specific Date)":
                chosen_date = st.date_input("Select Date for Report", datetime.date.today(), key=f"rep_date_{date_col}")
                return df[df[date_col].dt.date == chosen_date]
            elif time_filter == "Last 7 Days (1 Week)":
                start_date = today - pd.Timedelta(days=7)
                return df[df[date_col] >= start_date]
            elif time_filter == "This Month":
                return df[(df[date_col].dt.year == today.year) & (df[date_col].dt.month == today.month)]
            return df

        f_p = apply_time_filter(df_p)
        f_s = apply_time_filter(df_s)
        f_e = apply_time_filter(df_e)

        r_purchase = f_p["total_purchase"].sum() if not f_p.empty and "total_purchase" in f_p.columns else 0.0
        r_sales = f_s["total_sale"].sum() if not f_s.empty and "total_sale" in f_s.columns else 0.0
        r_expenses = f_e["total_expense"].sum() if not f_e.empty and "total_expense" in f_e.columns else 0.0
        r_net = r_sales - (r_purchase + r_expenses)

        st.markdown("### 📌 Selected Period Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🛒 Purchases", f"₹ {r_purchase:,.2f}")
        c2.metric("💰 Sales", f"₹ {r_sales:,.2f}")
        c3.metric("🧾 Expenses", f"₹ {r_expenses:,.2f}")
        c4.metric("💎 Net Bachat", f"₹ {r_net:,.2f}")

        st.markdown("---")
        st.subheader("📋 Detailed Breakdown Table")
        
        tab_r1, tab_r2, tab_r3 = st.tabs(["💰 Sales Records", "🛒 Purchase Records", "🧾 Expense Records"])
        with tab_r1:
            st.dataframe(f_s.drop(columns=["dt", "Year", "Month"], errors="ignore"), use_container_width=True)
        with tab_r2:
            st.dataframe(f_p.drop(columns=["dt", "Year", "Month"], errors="ignore"), use_container_width=True)
        with tab_r3:
            st.dataframe(f_e.drop(columns=["dt", "Year", "Month"], errors="ignore"), use_container_width=True)
            
    else:
        st.info("Pehle 'Quick Data Entry' section se kuch entries add karein.")

elif menu == "📂 Manage Database":
    st.subheader("📂 Raw Database Explorer & Delete Option")
    
    conn = sqlite3.connect(DB_FILE)
    df_p = pd.read_sql_query("SELECT * FROM purchases", conn)
    df_s = pd.read_sql_query("SELECT * FROM sales", conn)
    df_e = pd.read_sql_query("SELECT * FROM expenses", conn)
    df_u = pd.read_sql_query("SELECT * FROM supplier_udhaar", conn)
    conn.close()
    
    tab1, tab2, tab3 = st.tabs(["🛒 Purchases Table", "💰 Sales Table", "🧾 Expenses & Udhaar Table"])
    
    with tab1:
        st.dataframe(df_p, use_container_width=True)
        st.markdown("#### 🗑️ Delete Purchase Entry by Date")
        with st.form("del_purchase_form"):
            del_p_date = st.date_input("Choose Date to Delete Purchase", datetime.date.today(), key="del_p")
            submit_del_p = st.form_submit_button("❌ Delete Entries for This Date")
            if submit_del_p:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM purchases WHERE date = ?", (str(del_p_date),))
                conn.commit()
                conn.close()
                st.success(f"Purchases for {del_p_date} deleted successfully!")
                st.rerun()

    with tab2:
        st.dataframe(df_s, use_container_width=True)
        st.markdown("#### 🗑️ Delete Sales Entry by Date")
        with st.form("del_sales_form"):
            del_s_date = st.date_input("Choose Date to Delete Sales", datetime.date.today(), key="del_s")
            submit_del_s = st.form_submit_button("❌ Delete Entries for This Date")
            if submit_del_s:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sales WHERE date = ?", (str(del_s_date),))
                conn.commit()
                conn.close()
                st.success(f"Sales for {del_s_date} deleted successfully!")
                st.rerun()

    with tab3:
        st.dataframe(df_e, use_container_width=True)
        st.markdown("---")
        st.dataframe(df_u, use_container_width=True)
        st.markdown("#### 🗑️ Delete Udhaar Entry by Date")
        with st.form("del_udhaar_form"):
            del_u_date = st.date_input("Choose Date to Delete Udhaar", datetime.date.today(), key="del_u")
            submit_del_u = st.form_submit_button("❌ Delete Udhaar for This Date")
            if submit_del_u:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM supplier_udhaar WHERE date = ?", (str(del_u_date),))
                conn.commit()
                conn.close()
                st.success(f"Udhaar records for {del_u_date} deleted successfully!")
                st.rerun()