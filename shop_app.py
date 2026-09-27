import streamlit as st
import pandas as pd
import datetime
import sqlite3
import urllib.parse

# Page configuration optimized for mobile view
st.set_page_config(page_title="Navrang Vyapar Manager", page_icon="logo1.png", layout="centered")

# Custom Styling & Mobile-Friendly CSS Design
st.markdown("""
    <style>
        /* Mobile-First Responsive Adjustments */
        .main {
            background-color: var(--background-color);
            padding: 5px !important;
        }
        .sub-title {
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 20px;
            font-weight: 500;
        }
        /* Mobile friendly metrics & cards */
        [data-testid="stMetricValue"] {
            color: #D35400 !important;
            font-weight: 800 !important;
            font-size: 22px !important;
        }
        [data-testid="stMetricLabel"] {
            font-weight: 600 !important;
            font-size: 13px !important;
        }
        .stMetric {
            background: linear-gradient(135deg, rgba(211, 84, 0, 0.08) 0%, rgba(128, 128, 128, 0.05) 100%);
            padding: 12px;
            border-radius: 10px;
            border-left: 4px solid #D35400;
            box-shadow: 1px 3px 6px rgba(0,0,0,0.08);
            margin-bottom: 10px;
        }
        .custom-card {
            background-color: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.2);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 1px 2px 6px rgba(0,0,0,0.08);
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            width: 100%;
        }
        /* Clean and compact sidebar styling for mobile */
        [data-testid="stSidebar"] {
            background-color: var(--secondary-background-color);
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Top Header / Title with Custom Logo (Compact for Mobile)
col_logo, col_title = st.columns([1, 4])

with col_logo:
    try:
        st.image("logo1.png", width=65)
    except:
        st.write("🌿")

with col_title:
    st.markdown('<div style="font-size: 24px; font-weight: 800; color: #D35400; font-family: sans-serif; padding-top: 10px;">Navrang Vyapar</div>', unsafe_allow_html=True)

st.markdown('<div class="sub-title">Smart Business Manager & WhatsApp Hub</div>', unsafe_allow_html=True)

# Fresh Database setup
DB_FILE = "shop_database_v7.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, 
            suraj_dana_chana REAL, 
            durga_trading_company REAL, 
            bharat_general REAL, 
            jain_traders REAL, 
            kk_traders REAL, 
            jalaram_papad REAL, 
            gulab_panipuri REAL, 
            rais_ponga_wala REAL, 
            delux_suppliers REAL, 
            suhana_spices REAL, 
            ram_bandhu_spices REAL, 
            others REAL, 
            total_purchase REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, shop_sale REAL, cart_sale REAL, online_collection REAL, total_sale REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, electricity_bill REAL, shop_rent REAL, cart_rent REAL, 
            other_expense REAL, other_expense_desc TEXT, total_expense REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS supplier_udhaar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, supplier_name TEXT, amount REAL, status TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_udhaar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, customer_name TEXT, phone_number TEXT, amount REAL, status TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_directory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT, phone_number TEXT UNIQUE, customer_type TEXT, address TEXT, notes TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df_p = pd.read_sql_query("SELECT * FROM purchases", conn)
    df_s = pd.read_sql_query("SELECT * FROM sales", conn)
    df_e = pd.read_sql_query("SELECT * FROM expenses", conn)
    df_u = pd.read_sql_query("SELECT * FROM supplier_udhaar", conn)
    df_cu = pd.read_sql_query("SELECT * FROM customer_udhaar", conn)
    df_cd = pd.read_sql_query("SELECT * FROM customer_directory", conn)
    conn.close()
    
    for df in [df_p, df_s, df_e]:
        if not df.empty and "date" in df.columns:
            df["dt"] = pd.to_datetime(df["date"])
            df["Year"] = df["dt"].dt.year.astype(str)
            df["Month"] = df["dt"].dt.to_period("M").astype(str)
            
    for df_item in [df_u, df_cu]:
        if not df_item.empty and "date" in df_item.columns:
            df_item["dt"] = pd.to_datetime(df_item["date"])
        
    return df_p, df_s, df_e, df_u, df_cu, df_cd

df_p, df_s, df_e, df_u, df_cu, df_cd = load_data()

# Clean Sidebar Navigation Bar optimized for Mobile
st.sidebar.markdown("### 🧭 Menu")
menu = st.sidebar.radio(
    "Select Option",
    [
        "🏠 Home", 
        "➕ Data Entry", 
        "📒 Supplier Khata", 
        "👥 Customer Khata", 
        "📇 Directory & WA", 
        "📅 Reports", 
        "📂 Export"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("💡 Tip: Use WhatsApp broadcast for instant marketing.")

if menu == "🏠 Home":
    st.subheader("📊 Business Snapshot")
    
    total_p_val = df_p["total_purchase"].sum() if not df_p.empty and "total_purchase" in df_p.columns else 0.0
    total_s_val = df_s["total_sale"].sum() if not df_s.empty and "total_sale" in df_s.columns else 0.0
    total_e_val = df_e["total_expense"].sum() if not df_e.empty and "total_expense" in df_e.columns else 0.0
    
    pending_supplier_udhaar = df_u[df_u["status"] == "Pending"]["amount"].sum() if not df_u.empty and "status" in df_u.columns else 0.0
    pending_customer_udhaar = df_cu[df_cu["status"] == "Pending"]["amount"].sum() if not df_cu.empty and "status" in df_cu.columns else 0.0
    
    net_bachat_val = total_s_val - (total_p_val + total_e_val)
    
    # 2-column layout for mobile friendly metric cards
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🛒 Purchase", value=f"₹ {total_p_val:,.0f}")
        st.metric(label="🧾 Expenses", value=f"₹ {total_e_val:,.0f}")
        st.metric(label="👥 Cust. Pending", value=f"₹ {pending_customer_udhaar:,.0f}")
    with col2:
        st.metric(label="💰 Sales", value=f"₹ {total_s_val:,.0f}")
        st.metric(label="📒 Supp. Pending", value=f"₹ {pending_supplier_udhaar:,.0f}")
        st.metric(label="💎 Net Profit", value=f"₹ {net_bachat_val:,.0f}")
        
    st.markdown("---")
    
    st.markdown("### 📊 Sales vs Purchases Chart")
    if not df_s.empty or not df_p.empty:
        chart_sales = df_s.set_index("dt")["total_sale"] if not df_s.empty else pd.Series(dtype=float)
        chart_purchases = df_p.set_index("dt")["total_purchase"] if not df_p.empty else pd.Series(dtype=float)
        
        home_chart_data = pd.DataFrame({
            "💰 Sales": chart_sales,
            "🛒 Purchases": chart_purchases
        }).fillna(0).sort_index()
        
        st.bar_chart(home_chart_data)
    else:
        st.info("No data available yet to display chart.")

elif menu == "➕ Data Entry":
    st.subheader("📝 Quick Entry Panel")
    tab1, tab2, tab3 = st.tabs(["🛒 Purchase", "💰 Sales", "🧾 Expenses"])
    
    with tab1:
        with st.form("purchase_form"):
            p_date = st.date_input("Date", datetime.date.today(), key="p_date")
            suraj_dana_chana = st.number_input("Suraj Dana Chana (₹)", min_value=0.0, step=1.0)
            durga_trading_company = st.number_input("Durga Trading Company (₹)", min_value=0.0, step=1.0)
            bharat_general = st.number_input("Bharat General (₹)", min_value=0.0, step=1.0)
            jain_traders = st.number_input("Jain Traders (₹)", min_value=0.0, step=1.0)
            kk_traders = st.number_input("KK Traders (₹)", min_value=0.0, step=1.0)
            jalaram_papad = st.number_input("Jalaram Papad (₹)", min_value=0.0, step=1.0)
            gulab_panipuri = st.number_input("Gulab Panipuri (₹)", min_value=0.0, step=1.0)
            rais_ponga_wala = st.number_input("Rais Ponga Wala (₹)", min_value=0.0, step=1.0)
            delux_suppliers = st.number_input("Delux Suppliers (₹)", min_value=0.0, step=1.0)
            suhana_spices = st.number_input("Suhana Spices (₹)", min_value=0.0, step=1.0)
            ram_bandhu_spices = st.number_input("Ram Bandhu Spices (₹)", min_value=0.0, step=1.0)
            others = st.number_input("Others (₹)", min_value=0.0, step=1.0)
                
            submit_purchase = st.form_submit_button("💾 Save Purchase")
            if submit_purchase:
                total_p = suraj_dana_chana + durga_trading_company + bharat_general + jain_traders + kk_traders + jalaram_papad + gulab_panipuri + rais_ponga_wala + delux_suppliers + suhana_spices + ram_bandhu_spices + others
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO purchases (date, suraj_dana_chana, durga_trading_company, bharat_general, jain_traders, kk_traders, jalaram_papad, gulab_panipuri, rais_ponga_wala, delux_suppliers, suhana_spices, ram_bandhu_spices, others, total_purchase)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (str(p_date), suraj_dana_chana, durga_trading_company, bharat_general, jain_traders, kk_traders, jalaram_papad, gulab_panipuri, rais_ponga_wala, delux_suppliers, suhana_spices, ram_bandhu_spices, others, total_p))
                conn.commit()
                conn.close()
                st.success(f"🎉 Saved successfully! Total: ₹{total_p:,.2f}")

    with tab2:
        with st.form("sales_form"):
            s_date = st.date_input("Date", datetime.date.today(), key="s_date")
            shop_sale = st.number_input("Shop Sale (₹)", min_value=0.0, step=1.0)
            cart_sale = st.number_input("Cart Sale (₹)", min_value=0.0, step=1.0)
            online_collection = st.number_input("Online Collection (₹)", min_value=0.0, step=1.0)
            
            submit_sales = st.form_submit_button("💾 Save Sales")
            if submit_sales:
                total_s = shop_sale + cart_sale + online_collection
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sales (date, shop_sale, cart_sale, online_collection, total_sale)
                    VALUES (?, ?, ?, ?, ?)
                ''', (str(s_date), shop_sale, cart_sale, online_collection, total_s))
                conn.commit()
                conn.close()
                st.success(f"🎉 Saved successfully! Total: ₹{total_s:,.2f}")

    with tab3:
        with st.form("expense_form"):
            e_date = st.date_input("Date", datetime.date.today(), key="e_date")
            electricity = st.number_input("Electricity Bill (₹)", min_value=0.0, step=1.0)
            shop_rent = st.number_input("Shop Rent (₹)", min_value=0.0, step=1.0)
            cart_rent = st.number_input("Cart Rent (₹)", min_value=0.0, step=1.0)
            other_exp = st.number_input("Other Expenses (₹)", min_value=0.0, step=1.0)
            other_desc = st.text_input("Description")
            
            submit_expense = st.form_submit_button("💾 Save Expense")
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
                st.success(f"🎉 Saved successfully! Total: ₹{total_e:,.2f}")

elif menu == "📒 Supplier Khata":
    st.subheader("📒 Supplier Credit Khata")
    
    with st.form("udhaar_entry_form"):
        st.markdown("#### ➕ Add Supplier Credit")
        u_date = st.date_input("Date", datetime.date.today(), key="s_u_date")
        supplier_choice = st.selectbox("Supplier Name", ["Suraj Dana Chana", "Durga Trading Company", "Bharat General", "Jain Traders", "KK Traders", "Jalaram Papad", "Gulab Panipuri", "Rais Ponga Wala", "Delux Suppliers", "Suhana Spices", "Ram Bandhu Spices", "Other"])
        u_amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0, key="s_u_amt")
            
        custom_supplier = ""
        if supplier_choice == "Other":
            custom_supplier = st.text_input("Enter Supplier Name")
            
        submit_udhaar = st.form_submit_button("💾 Save Credit")
        if submit_udhaar:
            final_supp_name = custom_supplier if supplier_choice == "Other" else supplier_choice
            if final_supp_name.strip() == "":
                st.error("Please enter supplier name.")
            else:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO supplier_udhaar (date, supplier_name, amount, status)
                    VALUES (?, ?, ?, ?)
                ''', (str(u_date), final_supp_name, u_amount, "Pending"))
                conn.commit()
                conn.close()
                st.success(f"🎉 Saved successfully!")

    st.markdown("---")
    st.subheader("📋 Supplier Records")
    
    if not df_u.empty:
        status_filter = st.radio("Status", ["All", "Pending", "Paid"], horizontal=True, key="s_status_filter")
        view_df = df_u[df_u["status"] == status_filter] if status_filter != "All" else df_u
            
        for index, row in view_df.iterrows():
            st.markdown(f"""
                <div class="custom-card">
                    <b>📅 {row['date']}</b><br>
                    👤 <b>{row['supplier_name']}</b><br>
                    💰 ₹ {row['amount']:,.2f} &nbsp;|&nbsp; Status: <b>{row['status']}</b>
                </div>
            """, unsafe_allow_html=True)
            if row['status'] == "Pending":
                if st.button("✅ Mark Paid", key=f"paid_supp_{row['id']}"):
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE supplier_udhaar SET status = 'Paid' WHERE id = ?", (row['id'],))
                    conn.commit()
                    conn.close()
                    st.success("Updated to Paid!")
                    st.rerun()
    else:
        st.info("No records found.")

elif menu == "👥 Customer Khata":
    st.subheader("👥 Customer Credit Khata")
    
    with st.form("customer_udhaar_form"):
        st.markdown("#### ➕ Add Customer Credit")
        cu_date = st.date_input("Date", datetime.date.today(), key="c_u_date")
        cu_type = st.selectbox("Type", ["Retail", "Wholesale"], key="cu_type_in")
        cu_name = st.text_input("Customer Name")
        cu_phone = st.text_input("Mobile (10 digits)")
        cu_amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0, key="c_u_amt")
            
        submit_cu = st.form_submit_button("💾 Save Credit")
        if submit_cu:
            cleaned_phone = cu_phone.strip()
            if cu_name.strip() == "":
                st.error("Enter customer name.")
            elif not cleaned_phone.isdigit() or len(cleaned_phone) != 10:
                st.error("⚠️ Enter exact 10-digit mobile number.")
            else:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO customer_directory (customer_name, phone_number, customer_type, address, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (cu_name.strip(), cleaned_phone, cu_type, "", "Added via Khata"))
                
                cursor.execute('''
                    INSERT INTO customer_udhaar (date, customer_name, phone_number, amount, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (str(cu_date), cu_name.strip(), cleaned_phone, cu_amount, "Pending"))
                
                conn.commit()
                conn.close()
                st.success("🎉 Saved successfully!")
                st.rerun()

    st.markdown("---")
    search_query = st.text_input("🔍 Search Customer Name/Mobile", placeholder="Type here...")

    conn = sqlite3.connect(DB_FILE)
    df_cu_fresh = pd.read_sql_query("SELECT * FROM customer_udhaar", conn)
    conn.close()

    if not df_cu_fresh.empty:
        if "phone_number" not in df_cu_fresh.columns:
            df_cu_fresh["phone_number"] = ""

        if search_query.strip() != "":
            q = search_query.strip().lower()
            df_cu_fresh = df_cu_fresh[
                df_cu_fresh["customer_name"].str.lower().str.contains(q, na=False) | 
                df_cu_fresh["phone_number"].astype(str).str.contains(q, na=False)
            ]

        unique_customers = df_cu_fresh[["customer_name", "phone_number"]].drop_duplicates().values

        for cust_name, cust_phone in unique_customers:
            cust_df = df_cu_fresh[(df_cu_fresh["customer_name"] == cust_name) & (df_cu_fresh["phone_number"] == cust_phone)]
            total_cust_udhaar = cust_df[cust_df["status"] == "Pending"]["amount"].sum()
            
            wa_msg = f"Namaste {cust_name} ji, Navrang Vyapar se aapka ₹{total_cust_udhaar:,.2f} ka pending udhaar baki hai. Kripya bhugtan karein."
            wa_link = f"https://wa.me/91{cust_phone}?text={urllib.parse.quote(wa_msg)}"

            st.markdown(f"""
                <div class="custom-card">
                    <h4 style="margin: 0; color: #D35400;">👤 {cust_name}</h4>
                    <p style="margin: 5px 0;">📞 {cust_phone} | 🔴 Due: ₹ {total_cust_udhaar:,.2f}</p>
            """, unsafe_allow_html=True)
            
            if total_cust_udhaar > 0 and cust_phone and len(str(cust_phone)) == 10:
                st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:6px 12px; border-radius:6px; font-weight:bold; cursor:pointer;">💬 WhatsApp Reminder</button></a>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No customer credit records.")

elif menu == "📇 Directory & WA":
    st.subheader("📇 Customer Directory & WhatsApp Hub")
    
    with st.form("new_dir_customer"):
        st.markdown("#### ➕ Add Customer")
        d_type = st.selectbox("Category", ["Retail", "Wholesale"], key="dir_type_add")
        d_name = st.text_input("Full Name")
        d_phone = st.text_input("Mobile (10 digits)")
        d_address = st.text_input("Address/City")
        d_notes = st.text_area("Notes")
            
        submit_dir = st.form_submit_button("💾 Save Customer")
        if submit_dir:
            clean_p = d_phone.strip()
            if d_name.strip() == "":
                st.error("Name required.")
            elif not clean_p.isdigit() or len(clean_p) != 10:
                st.error("⚠️ Enter 10-digit mobile number.")
            else:
                try:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO customer_directory (customer_name, phone_number, customer_type, address, notes)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (d_name.strip(), clean_p, d_type, d_address.strip(), d_notes.strip()))
                    conn.commit()
                    conn.close()
                    st.success("🎉 Saved!")
                    st.rerun()
                except:
                    st.error("⚠️ Mobile number already registered.")

    st.markdown("---")
    conn = sqlite3.connect(DB_FILE)
    df_dir_fresh = pd.read_sql_query("SELECT * FROM customer_directory", conn)
    conn.close()

    if "customer_type" not in df_dir_fresh.columns:
        df_dir_fresh["customer_type"] = "Retail"

    df_retail = df_dir_fresh[df_dir_fresh["customer_type"] == "Retail"]
    df_wholesale = df_dir_fresh[df_dir_fresh["customer_type"] == "Wholesale"]

    msg_template = st.text_area("💬 WhatsApp Broadcast Template:", value="Namaste {name} ji, Navrang Vyapar se naye Khandeshi masale aur papad uplabdh hain!")

    tab_r, tab_w = st.tabs(["🛍️ Retail", "📦 Wholesale"])
    with tab_r:
        for _, row in df_retail.iterrows():
            link = f"https://wa.me/91{row['phone_number']}?text={urllib.parse.quote(msg_template.replace('{name}', row['customer_name']))}"
            st.markdown(f"""
                <div class="custom-card">
                    <b>👤 {row['customer_name']}</b><br>📞 {row['phone_number']}<br>
                    <a href="{link}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:5px 10px; border-radius:5px; margin-top:5px;">💬 WhatsApp</button></a>
                </div>
            """, unsafe_allow_html=True)

    with tab_w:
        for _, row in df_wholesale.iterrows():
            link = f"https://wa.me/91{row['phone_number']}?text={urllib.parse.quote(msg_template.replace('{name}', row['customer_name']))}"
            st.markdown(f"""
                <div class="custom-card">
                    <b>👤 {row['customer_name']}</b><br>📞 {row['phone_number']}<br>
                    <a href="{link}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:5px 10px; border-radius:5px; margin-top:5px;">💬 WhatsApp</button></a>
                </div>
            """, unsafe_allow_html=True)

elif menu == "📅 Reports":
    st.subheader("📈 Reports & Supplier Purchase Check")
    
    if not df_p.empty or not df_s.empty or not df_e.empty:
        filter_mode = st.selectbox("Filter Type", ["All Time", "Specific Date", "Specific Month", "Specific Year"], key="main_filter")
        
        def filter_dataset(df, prefix):
            if df.empty or "dt" not in df.columns:
                return df
            if filter_mode == "Specific Date":
                chosen_date = st.date_input(f"Date ({prefix})", datetime.date.today(), key=f"d_{prefix}")
                return df[df["dt"].dt.date == chosen_date]
            elif filter_mode == "Specific Month":
                c1, c2 = st.columns(2)
                with c1:
                    sel_year = st.selectbox(f"Year ({prefix})", options=sorted(df["Year"].unique(), reverse=True), key=f"my_{prefix}")
                with c2:
                    sel_month = st.selectbox(f"Month ({prefix})", options=sorted(df[df["Year"] == sel_year]["Month"].unique()), key=f"mm_{prefix}")
                return df[df["Month"] == sel_month]
            elif filter_mode == "Specific Year":
                sel_year = st.selectbox(f"Year ({prefix})", options=sorted(df["Year"].unique(), reverse=True), key=f"y_{prefix}")
                return df[df["Year"] == sel_year]
            return df

        f_p = filter_dataset(df_p, "purchases")
        f_s = filter_dataset(df_s, "sales")
        f_e = filter_dataset(df_e, "expenses")

        st.markdown("---")
        st.markdown("### 🏢 Supplier Purchase Check")
        supplier_columns = {
            "Suraj Dana Chana": "suraj_dana_chana",
            "Durga Trading Company": "durga_trading_company",
            "Bharat General": "bharat_general",
            "Jain Traders": "jain_traders",
            "KK Traders": "kk_traders",
            "Jalaram Papad": "jalaram_papad",
            "Gulab Panipuri": "gulab_panipuri",
            "Rais Ponga Wala": "rais_ponga_wala",
            "Delux Suppliers": "delux_suppliers",
            "Suhana Spices": "suhana_spices",
            "Ram Bandhu Spices": "ram_bandhu_spices",
            "Others": "others"
        }
        selected_supp = st.selectbox("Select Supplier", list(supplier_columns.keys()), key="chk_sup")
        col_name = supplier_columns[selected_supp]

        if not f_p.empty and col_name in f_p.columns:
            spent = f_p[col_name].sum()
            st.success(f"📦 Total purchase from **{selected_supp}**: **₹ {spent:,.2f}**")

        st.markdown("---")
        r_sales = f_s["total_sale"].sum() if not f_s.empty and "total_sale" in f_s.columns else 0.0
        r_purchase = f_p["total_purchase"].sum() if not f_p.empty and "total_purchase" in f_p.columns else 0.0
        r_expenses = f_e["total_expense"].sum() if not f_e.empty and "total_expense" in f_e.columns else 0.0
        r_net = r_sales - (r_purchase + r_expenses)

        st.markdown("### 📌 Summary")
        c1, c2 = st.columns(2)
        c1.metric("🛒 Purchases", f"₹ {r_purchase:,.2f}")
        c1.metric("🧾 Expenses", f"₹ {r_expenses:,.2f}")
        c2.metric("💰 Sales", f"₹ {r_sales:,.2f}")
        c2.metric("💎 Net Profit", f"₹ {r_net:,.2f}")
    else:
        st.info("No data available.")

elif menu == "📂 Export":
    st.subheader("📂 Data Export & Backup")
    conn = sqlite3.connect(DB_FILE)
    df_p = pd.read_sql_query("SELECT * FROM purchases", conn)
    df_s = pd.read_sql_query("SELECT * FROM sales", conn)
    df_e = pd.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()

    if not df_s.empty:
        st.download_button("📥 Download Sales CSV", df_s.to_csv(index=False).encode('utf-8'), "sales.csv", "text/csv")
    if not df_p.empty:
        st.download_button("📥 Download Purchases CSV", df_p.to_csv(index=False).encode('utf-8'), "purchases.csv", "text/csv")
    if not df_e.empty:
        st.download_button("📥 Download Expenses CSV", df_e.to_csv(index=False).encode('utf-8'), "expenses.csv", "text/csv")
