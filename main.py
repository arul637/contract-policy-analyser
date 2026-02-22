import streamlit as st
import os
import time
from typing import List

from data_cleanising import DataCleanising
from embedding_model import EmbeddingModel

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import chromadb


# ==================================
# SESSION STATE INITIALIZATION
# ==================================

def init_session():
    defaults = {
        "uploaded": False,
        "cleaned": False,
        "embedded": False,
        "analysis_done": False,
        "policy_path": None,
        "contract_path": None,
        "policy_data": None,
        "contract_data": None,
        "risk_results": {}
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session()

os.makedirs("output_files", exist_ok=True)


# ==================================
# 1️⃣ FILE UPLOAD
# ==================================

def upload_section():

    st.title("📂 Upload Documents")

    policy_file = st.file_uploader("Upload Business Policy PDF", type=["pdf"])
    contract_file = st.file_uploader("Upload Employee Contract PDF", type=["pdf"])

    if st.button("Save Files"):

        if not policy_file or not contract_file:
            st.error("Please upload both files.")
            return

        policy_path = os.path.join("output_files", "business_policy.pdf")
        contract_path = os.path.join("output_files", "employee_contract.pdf")

        with open(policy_path, "wb") as f:
            f.write(policy_file.getbuffer())

        with open(contract_path, "wb") as f:
            f.write(contract_file.getbuffer())

        st.session_state.policy_path = policy_path
        st.session_state.contract_path = contract_path
        st.session_state.uploaded = True

        st.success("Files saved successfully ✅")
        time.sleep(1)
        st.rerun()


# ==================================
# 2️⃣ DATA CLEANING
# ==================================

def data_cleaning_section():

    st.title("🧹 Data Cleaning")

    if st.button("Start Data Cleaning"):

        with st.spinner("Cleaning documents..."):

            try:
                policy_cleaner = DataCleanising(st.session_state.policy_path)
                policy_clauses = policy_cleaner.split_clause()
                structured_policy = policy_cleaner.structured_policy(policy_clauses)

                contract_cleaner = DataCleanising(st.session_state.contract_path)
                contract_clauses = contract_cleaner.split_clause()
                structured_contract = contract_cleaner.structured_policy(contract_clauses)

                st.session_state.policy_data = structured_policy
                st.session_state.contract_data = structured_contract
                st.session_state.cleaned = True

                st.success("Data cleaned successfully ✅")
                time.sleep(1)
                st.rerun()

            except Exception as e:
                st.error(f"Cleaning Error: {e}")


# ==================================
# 3️⃣ VECTOR STORE
# ==================================

def vector_store():

    st.title("🧠 Creating Vector Databases")

    if st.button("Generate Embeddings"):

        with st.spinner("Embedding and storing clauses..."):

            try:
                # Business Policy DB
                policy_vector_db = EmbeddingModel(
                    embedding_model='qwen3-embedding:8b',
                    vector_database_path='business-policy-db'
                )

                policy_vector_db.vector_store(
                    structured_policy=st.session_state.policy_data
                )

                # Employee Contract DB
                contract_vector_db = EmbeddingModel(
                    embedding_model='qwen3-embedding:8b',
                    vector_database_path='employee-contract-db'
                )

                contract_vector_db.vector_store(
                    structured_policy=st.session_state.contract_data
                )

                st.session_state.embedded = True
                st.success("Vector Databases Created Successfully ✅")

                time.sleep(1)
                st.rerun()

            except Exception as e:
                st.error(f"Vector Store Error: {e}")


# ==================================
# 4️⃣ RISK ANALYSIS
# ==================================

def risk_analysis_section():

    st.title("⚠ Contract Risk Analysis")

    if st.button("Run Risk Analysis"):

        with st.spinner("Analyzing risks..."):

            llm = ChatOllama(model='llama3.1:8b', temperature=0.6)

            categories = [
                'prohibited',
                'mandatory',
                'conditional',
                'optional',
                'uncategorized'
            ]

            db_paths = {
                'business-policy-db': 'business_policy',
                'employee-contract-db': 'employee_contract'
            }

            aggregator_name = 'business-policy-aggregator'

            results = {}

            for category in categories:

                severity_map = {
                    "prohibited": "critical",
                    "mandatory": "high",
                    "conditional": "medium",
                    "optional": "low",
                    "uncategorized": "info"
                }

                results[category] = {
                    "business_policy": "",
                    "employee_contract": "",
                    "severity": severity_map.get(category, "info")
                }

                for db_path, field_name in db_paths.items():

                    try:
                        client = chromadb.PersistentClient(path=db_path)
                        collection = client.get_collection(aggregator_name)

                        query_results = collection.get(where={"category": category})

                        if query_results and query_results["documents"]:
                            results[category][field_name] = " ".join(query_results["documents"])

                    except:
                        pass

            # Load Prompt
            with open("prompts/policy-risk-analyser.txt", "r") as f:
                prompt_text = f.read()

            prompt_template = ChatPromptTemplate.from_messages([
                ("human", prompt_text)
            ])

            final_results = {}

            for category, data in results.items():

                formatted_prompt = prompt_template.format_messages(
                    business_policy=data["business_policy"],
                    employee_contract_policy=data["employee_contract"],
                    category=category,
                    severity=data["severity"]
                )

                try:
                    response = llm.invoke(formatted_prompt)
                    final_results[category] = {
                        "severity": data["severity"],
                        "analysis": response.content
                    }
                except Exception as e:
                    final_results[category] = {
                        "severity": data["severity"],
                        "analysis": f"Error: {e}"
                    }

            st.session_state.risk_results = final_results
            st.session_state.analysis_done = True
            st.rerun()


# ==================================
# 5️⃣ DISPLAY RESULTS
# ==================================

def display_results():

    st.title("📊 Risk Assessment Report")

    for category, result in st.session_state.risk_results.items():

        severity = result["severity"]
        analysis = result["analysis"]

        if severity == "critical":
            st.error(f"🚨 {category.upper()} (CRITICAL)")
        elif severity == "high":
            st.warning(f"⚠ {category.upper()} (HIGH)")
        else:
            st.info(f"{category.upper()} ({severity.upper()})")

        st.markdown(analysis)
        st.divider()


# ==================================
# FLOW CONTROLLER
# ==================================

if not st.session_state.uploaded:
    upload_section()

elif not st.session_state.cleaned:
    data_cleaning_section()

elif not st.session_state.embedded:
    vector_store()

elif not st.session_state.analysis_done:
    risk_analysis_section()

else:
    display_results()
