import streamlit as st
from pinecone import Pinecone, ServerlessSpec

# Initialize Pinecone
import os
pinecone_api_key=st.secrets["api_keys"]["PINECONE_API_KEY"]
pc = Pinecone(api_key=pinecone_api_key)
index_name = "ugc-reg-vector-store"
index = pc.Index(index_name)

# Streamlit Application
def main():
    st.title("UGC Regulations - Analysis")

    # State management for selected ID and filter
    if "selected_id" not in st.session_state:
        st.session_state.selected_id = None
    if "selected_category" not in st.session_state:
        st.session_state.selected_category = "All"
    print(st.session_state.selected_id)
    # Function to reset state
    def reset_state():
        st.session_state.selected_id = None
        st.session_state.selected_category = "All"

    # First screen: Display table of unique IDs with filter

    # Sidebar: Category filter
    with st.sidebar:
        st.header("Regulation Impact Category")
        category_filter = st.selectbox(
            "Filter by Category",
            options=["All", "Academic", "Industry Partnership", "Admissions", "Student Support", "Events", "Other"],
            index=0
        )
        st.session_state.selected_category = category_filter

    if st.session_state.selected_id is None:
        st.header("Analyze Recent Notifications")

        # Fetch IDs and filter by category
        stats = index.describe_index_stats()
        vector_count = stats["namespaces"][""]["vector_count"]
        document_ids = []

        for doc_id in index.query(
            vector=[0] * stats["dimension"],  # Dummy query for metadata search
            top_k=vector_count,
            include_metadata=True
        )["matches"]:
            metadata = doc_id["metadata"]
            description = metadata["Description"]
            if st.session_state.selected_category == "All" or st.session_state.selected_category in metadata.get("category", []):
                document_ids.append((doc_id["id"], description))

        if not document_ids:
            st.write("No documents found for the selected category.")
            return

        st.write("Click on a Notification to analyze policy and assess impact")
        for doc_id, desc in document_ids:
            if st.button(f"{desc}", key=doc_id):
                st.session_state.selected_id = doc_id
                st.rerun()
                #print("HERE")


    # Second screen: Display document details
    else:
        st.header("Regulation Analysis Details")
        selected_id = st.session_state.selected_id

        # Fetch document details from Pinecone
        response = index.fetch(ids=[selected_id])
        vector_data = response.get("vectors", {}).get(selected_id, {})
        document_details = vector_data.get("metadata", {}).get("text", "No details available.")
        category = vector_data.get("metadata", {}).get("category", [])

        #st.write(f"**Document ID:** {selected_id}")
        st.write(f"**Title:** {document_details}")
        #st.write(f"**Category:** {', '.join(category)}")

        if st.button("Back to Document List"):
            print(st.session_state.selected_id)
            reset_state()
            st.rerun()


if __name__ == "__main__":
    main()
