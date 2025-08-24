import streamlit as st
import requests
import json
import time

# Backend API URL (assume local; update for deployment)
API_BASE = "http://localhost:8000"

# Sidebar navigation (multi-page like)
page = st.sidebar.selectbox("Navigate", ["Home", "Upload Document", "Process Query", "Manage Documents", "System Stats"])

if page == "Home":
    st.title("IntelliClaim Streamlit Frontend")
    st.markdown("""
    Welcome to the Streamlit version of IntelliClaim!
    - Upload policy documents (files or URLs).
    - Query claims for AI-powered decisions.
    - Manage documents and view system stats.
    
    **Note**: Ensure the backend is running (e.g., `python app.py`).
    """)
    if st.button("Check Backend Health"):
        with st.spinner("Checking..."):
            try:
                response = requests.get(f"{API_BASE}/health")
                if response.status_code == 200:
                    st.success("Backend is healthy!")
                    st.json(response.json())
                else:
                    st.error(f"Health check failed: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

elif page == "Upload Document":
    st.header("Upload Document")
    tab1, tab2 = st.tabs(["Upload File", "Upload via URL"])
    
    with tab1:
        uploaded_file = st.file_uploader("Choose a PDF/DOCX/EML file", type=["pdf", "docx", "eml"])
        if uploaded_file and st.button("Upload File"):
            with st.spinner("Uploading..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    response = requests.post(f"{API_BASE}/upload-document", files=files)
                    if response.status_code == 200:
                        st.success("Document uploaded successfully!")
                        st.json(response.json())
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab2:
        url = st.text_input("Enter document URL")
        async_mode = st.checkbox("Process asynchronously")
        if url and st.button("Upload URL"):
            with st.spinner("Uploading..."):
                try:
                    payload = {"url": url, "async_mode": async_mode}
                    response = requests.post(f"{API_BASE}/upload-document-url", json=payload)
                    if response.status_code == 200:
                        st.success("Document URL processed!")
                        st.json(response.json())
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

elif page == "Process Query":
    st.header("Process Claim Query")
    query = st.text_area("Enter your query (e.g., 'Patient, 62M, cataract surgery in Pune; policy 14 months. Eligible?')")
    if st.button("Process Query"):
        if query:
            with st.spinner("Processing..."):
                try:
                    payload = {"query": query}
                    response = requests.post(f"{API_BASE}/query", json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        st.success("Query processed!")
                        
                        # Formatted display
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("Decision")
                            color = "green" if result["decision"] == "APPROVED" else "red" if result["decision"] == "REJECTED" else "orange"
                            st.markdown(f"<h3 style='color:{color};'>{result['decision']}</h3>", unsafe_allow_html=True)
                            st.subheader("Amount")
                            st.write(result.get("amount", "N/A"))
                        with col2:
                            st.subheader("Confidence Score")
                            st.progress(result["confidence_score"] / 100)
                            st.write(f"{result['confidence_score']}%")
                        
                        st.subheader("Justification")
                        st.write(result["justification"])
                        
                        st.subheader("Clause Mappings")
                        st.json(result.get("clause_mappings", []))
                        
                        st.subheader("Audit Trail")
                        for item in result.get("audit_trail", []):
                            st.write(f"- {item}")
                        
                        st.subheader("Full Response")
                        st.json(result)
                    else:
                        st.error(f"Query failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a query.")

elif page == "Manage Documents":
    st.header("Manage Documents")
    if st.button("List Documents"):
        with st.spinner("Fetching..."):
            try:
                response = requests.get(f"{API_BASE}/documents")
                if response.status_code == 200:
                    docs = response.json()
                    st.success("Documents loaded!")
                    st.json(docs)
                    # Display in table
                    if docs.get("document_sources"):
                        for source in docs["document_sources"]:
                            col1, col2 = st.columns([3, 1])
                            col1.write(source)
                            if col2.button(f"Delete {source}", key=source):
                                del_response = requests.delete(f"{API_BASE}/documents/{source}")
                                if del_response.status_code == 200:
                                    st.success(f"Deleted {source}")
                                else:
                                    st.error(f"Delete failed: {del_response.text}")
                else:
                    st.error(f"Failed to list documents: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

elif page == "System Stats":
    st.header("System Stats")
    if st.button("Get Stats"):
        with st.spinner("Fetching..."):
            try:
                response = requests.get(f"{API_BASE}/system-stats")
                if response.status_code == 200:
                    st.success("Stats loaded!")
                    stats = response.json()
                    st.metric("Total Documents", stats["total_documents"])
                    st.metric("Vector Store Size", stats["vector_store_size"])
                    st.write(f"Status: {stats['system_status']}")
                    st.write(f"Last Updated: {stats['last_updated']}")
                    st.write(f"API Version: {stats['api_version']}")
                else:
                    st.error(f"Failed to get stats: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
