import streamlit as st
from app.router import route_query

st.set_page_config(page_title="Employee Contract & Renewal Risk Assistant")

st.title("Employee Contract & Renewal Risk Assistant")
st.write("Ask a question about contracts, renewals, or policy rules.")

if "response" not in st.session_state:
    st.session_state.response = None

if "loading" not in st.session_state:
    st.session_state.loading = False

def submit_query():
    st.session_state.loading = True
    st.session_state.response = None

with st.form("query_form"):
    st.text_input("Enter your question:", key="user_query")
    submitted = st.form_submit_button("Submit", on_click=submit_query)

answer_placeholder = st.empty()

# Step 1: Show Thinking immediately
if st.session_state.loading and st.session_state.response is None:
    answer_placeholder.markdown("### Answer\n\n**Thinking...**")
    # Now actually execute the query
    st.session_state.response = route_query(st.session_state.user_query)
    st.session_state.loading = False
    st.rerun()

# Step 2: Show final response
if st.session_state.response:
    response = st.session_state.response

    with answer_placeholder.container():
        st.subheader("Answer")
        st.write(response["answer"])

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.write("Source")
            st.code(response["source"])

        with col2:
            st.write("Confidence")
            st.code(response["confidence"])

        if response.get("generated_sql"):
            with st.expander("View Generated SQL"):
                st.code(response["generated_sql"], language="sql")

        if response.get("retrieved_context"):
            with st.expander("View Retrieved Policy Context"):
                for doc, section, content, distance in response["retrieved_context"]:
                    st.markdown(f"**Document:** {doc}")
                    st.markdown(f"**Section:** {section}")
                    st.markdown(content)
                    st.markdown("---")
