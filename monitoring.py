import streamlit as st
from datetime import date, timedelta
import base64
import os
import pickle

st.set_page_config(layout="wide")
tab1, tab2 = st.tabs(['Klaim Promo', "FlowChart"])
with tab1:
    st.title("📊 Monitoring Timeline Klaim Promo")

    # Fungsi untuk konversi dan penyimpanan data

    def file_to_base64(file):
        return base64.b64encode(file).decode("utf-8")

    def save_data_pickle(data, filename="data_monitoring.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(data, f)

    def load_data_pickle(filename="data_monitoring.pkl"):
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                return pickle.load(f)
        return []

    # Inisialisasi session state
    if "data" not in st.session_state:
        st.session_state.data = load_data_pickle()

    # Menyimpan data jika ada update
    def save_data():
        save_data_pickle(st.session_state.data)

    # Form input
    st.subheader("📝 Submit Data Klaim Promo")

    col1, col2, col3 = st.columns(3)
    distributor = col1.selectbox("Pilih Distributor", ["", "SND", "WOI", "HCO", "Surdon (ex WOI)"])
    tipe_promo = col2.selectbox("Tipe Promo", ["", "Rafraksi", "NOO", "Bundling"])
    deadline = col3.date_input("Tanggal Deadline", value=date.today())

    col4, col5, col6 = st.columns(3)
    pic = col4.text_input("Nama PIC")
    tanggal_submit = col5.date_input("Tanggal Submit", value=date.today())
    file_submit = col6.file_uploader("Upload File Submit", type=["pdf", "xlsx", "xls", "docx"])

    if st.button("➕ Tambahkan Data"):
        if distributor and tipe_promo and file_submit:
            st.session_state.data.append({
                "Distributor": distributor,
                "Tipe Promo": tipe_promo,
                "Nama PIC" : pic,
                "Tanggal Submit": tanggal_submit,
                "Tanggal Deadline": deadline,
                "File Submit Name": file_submit.name,
                "File Submit Data": file_to_base64(file_submit.read()),
                "Tarikan Record": "",
                "Nama Validasi": "",
                "Tanggal Validasi": "",
                "File Validasi Name": "",
                "File Validasi Data": None
            })
            save_data()
            st.success("Data berhasil ditambahkan!")
        else:
            st.warning("Lengkapi semua isian terlebih dahulu!")

    st.markdown("---")

    # Tampilkan data
    if st.session_state.data:
        st.subheader("📋 Monitoring Progress Klaim Promo")

        headers = [
            "No", "Distributor", "Tipe Promo", "Nama PIC", "Tanggal Submit", "Nama File",
            "Download Submit", "Tarikan Record", "Nama Validasi", "Tanggal Validasi",
            "Upload File Validasi", "Nama File Validasi", "Download Validasi", "Keterangan", "Selesai", "Delete"
        ]

        cols = st.columns([0.3, 1.2, 1.2, 1.2,1.2, 1.5, 1, 1.2, 1.5, 1.5, 2, 1.5, 1, 1, 1, 1])
        for col, header in zip(cols, headers):
            col.markdown(f"**{header}**")

        for i, row in enumerate(st.session_state.data):
            row.setdefault("File Submit Name", "")
            row.setdefault("File Submit Data", None)
            row.setdefault("Tarikan Record", "")
            row.setdefault("Nama Validasi", "")
            row.setdefault("Tanggal Validasi", "")
            row.setdefault("File Validasi Name", "")
            row.setdefault("File Validasi Data", None)
            row.setdefault("Is Done", False)

            col = st.columns([0.3, 1.2, 1.2, 1.2,1.2, 1.5, 1, 1.2, 1.5, 1.5, 2, 1.5, 1, 1, 1, 1])

            col[0].markdown(f"{i+1}")
            col[1].markdown(row["Distributor"])
            col[2].markdown(row["Tipe Promo"])
            col[3].markdown(row["Nama PIC"])
            col[4].markdown(str(row["Tanggal Submit"]))
            col[5].markdown(row["File Submit Name"])

            file_submit_data = base64.b64decode(row["File Submit Data"])
            if col[6].download_button(
                label="⬇️", data=file_submit_data,
                file_name=row["File Submit Name"],
                key=f"dl_submit_{i}", help="Download Submit"
            ):
                row["Tarikan Record"] = date.today()
                save_data()

            col[7].markdown(str(row["Tarikan Record"]) or "-")

            # Cek apakah lebih dari 2 minggu
            try:
                tgl_val = row["Tanggal Validasi"]
                tgl_val = date.fromisoformat(str(tgl_val)) if tgl_val else None
            except:
                tgl_val = None

            is_locked = (
                row.get("Is Done", False) or (
                    bool(row["Nama Validasi"]) and
                    bool(tgl_val) and
                    bool(row["File Validasi Data"]) and
                    (tgl_val - row["Tanggal Submit"]) > timedelta(weeks=2)
                )
            )

            # Text input
            nama_validasi = col[8].text_input("", value=row["Nama Validasi"], key=f"nama_val_{i}", disabled=is_locked, placeholder="Isi Nama")

            # Date input
            tgl_input = col[9].date_input("", value=tgl_val or date.today(), key=f"tgl_val_{i}", disabled=is_locked)

            # File uploader
            if not is_locked:
                file_val = col[10].file_uploader("", key=f"file_val_{i}", type=["pdf", "xlsx", "xls", "docx"])
                if file_val:
                    row["File Validasi Name"] = file_val.name
                    row["File Validasi Data"] = file_to_base64(file_val.read())
                    save_data()
                    col[10].success("✅")
            else:
                col[10].markdown("🔒 <i>Terkunci</i>", unsafe_allow_html=True)

            # Nama file tetap ditampilkan, nggak pakai disabled
            col[11].markdown(row["File Validasi Name"] or "-")

            # Tombol download tetap bisa jalan
            if row["File Validasi Data"]:
                file_val_data = base64.b64decode(row["File Validasi Data"])
                col[12].download_button(
                    label="⬇️", data=file_val_data,
                    file_name=row["File Validasi Name"],
                    key=f"dl_val_{i}", help="Download Validasi"
                )

            if row["Nama Validasi"] and tgl_val and row["File Validasi Data"]:
                delta = tgl_val - row["Tanggal Submit"]
                if delta > timedelta(weeks=2):
                    keterangan = "Terlambat"
                    style = "background-color: red;"
                else:
                    keterangan = "On Target"
                    style = "background-color: green;"
            else:
                keterangan = "-"
                style = "background-color: gray;"

            box_style = f"{style} color: white; padding: 5px; border-radius: 5px; text-align: center;"
            col[13].markdown(f"<div style='{box_style}'>{keterangan}</div>", unsafe_allow_html=True)

            # Inisialisasi state konfirmasi delete
            if f"confirm_delete_{i}" not in st.session_state:
                st.session_state[f"confirm_delete_{i}"] = False

            if not st.session_state[f"confirm_delete_{i}"]:
                if col[14].button("❌ Delete", key=f"delete_{i}"):
                    st.session_state[f"confirm_delete_{i}"] = True
                    st.rerun()
            else:
                col[14].warning("Yakin ingin menghapus?")
                confirm_col1, confirm_col2 = col[14].columns(2)
                if confirm_col1.button("✅ Ya", key=f"confirm_yes_{i}"):
                    del st.session_state.data[i]
                    save_data()
                    st.success(f"Data pada baris {i+1} berhasil dihapus.")
                    st.rerun()
                if confirm_col2.button("❌ Batal", key=f"confirm_no_{i}"):
                    st.session_state[f"confirm_delete_{i}"] = False
                    st.rerun()

            if not row["Is Done"]:
                if col[15].button("✅ Selesai", key=f"done_{i}"):
                    row["Is Done"] = True
                    save_data()
                    st.rerun()
            else:
                col[15].markdown("✅ <i>Sudah Selesai</i>", unsafe_allow_html=True)

    else:
        st.info("Belum ada data yang dimasukkan.")

with tab2:
    None
