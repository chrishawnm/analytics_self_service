import os
import re
import streamlit as st
import duckdb
from openai import OpenAI

# -------------------------------
# 🔧 PATH CONFIGURATION (dynamic)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "ecommerce.db")
SEMANTIC_YAML_PATH = os.path.join(
    BASE_DIR, "ecommerce_data_insights", "models", "semantic_models", "user_events_semantics.yml"
)


client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# -------------------------------
# 🏷️ STREAMLIT UI
# -------------------------------
st.title("💬 Text-to-SQL on dbt + DuckDB + Semantic Layer")
prompt = st.text_input("Ask a question about your data:")

# -------------------------------
# 🧩 HELPER FUNCTIONS
# -------------------------------
def get_db_schema(con):
    """Read live DuckDB schema and return formatted string."""
    tables = con.execute("SHOW TABLES").fetchall()
    if not tables:
        return "# No tables found in database."
    schema_str = "Tables:\n"
    for (table_name,) in tables:
        cols = con.execute(f"DESCRIBE {table_name}").fetchall()
        col_names = [col[0] for col in cols]
        schema_str += f"- {table_name}({', '.join(col_names)})\n"
    return schema_str


def get_semantic_yaml(path):
    """Read the semantic model YAML file."""
    if not os.path.exists(path):
        return "# No semantic YAML found at given path."
    with open(path) as f:
        return f.read()

# -------------------------------
# 🚀 MAIN LOGIC
# -------------------------------
if prompt:
    if not os.path.exists(DB_PATH):
        st.error(f"⚠️ Database not found at: {DB_PATH}")
        st.stop()

    # 1️⃣ Connect to DuckDB (read-only to prevent lock issues)
    con = duckdb.connect(DB_PATH, read_only=True)

    # 2️⃣ Gather schema + semantic model
    db_schema = get_db_schema(con)
    semantic_yaml = get_semantic_yaml(SEMANTIC_YAML_PATH)

    # 3️⃣ Compose the LLM query prompt
    query_prompt = f"""
You are a helpful SQL assistant.
Use the following database schema and semantic model to answer the user's question.

Schema from DuckDB:
{db_schema}

Semantic layer definition:
{semantic_yaml}

Now write a valid SQL query that answers:
"{prompt}"

Rules:
- Return only SQL, no explanations.
- Prefer the most relevant tables and measures.
- Use proper DuckDB syntax.
    """

    # 4️⃣ Generate SQL with OpenAI
    try:
        completion = client.responses.create(model="gpt-4o-mini", input=query_prompt)
        sql = completion.output_text.strip()

        # 🧹 Remove Markdown fences (```sql ... ```) before executing
        sql = re.sub(r"^```[a-zA-Z]*\n|```$", "", sql.strip(), flags=re.MULTILINE)

        st.subheader("🧠 Generated SQL")
        st.code(sql, language="sql")
    except Exception as e:
        st.error(f"⚠️ Error generating SQL: {e}")
        st.stop()

    # 5️⃣ Run query and display results
    try:
        df = con.execute(sql).fetchdf()
        st.subheader("📊 Query Results")
        st.dataframe(df)
    except Exception as e:
        st.error(f"⚠️ Error executing SQL: {e}")

    # 6️⃣ Clean up
    con.close()
