import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Genomic Variants Dashboard",
    layout="wide"
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    chrom = pd.read_csv("data/gold_chromosome.csv")
    cond = pd.read_csv("data/gold_condition.csv")
    gene = pd.read_csv("data/gold_pathogenic.csv")
    sig = pd.read_csv("data/gold_significance.csv")
    return chrom, cond, gene, sig

chrom_df, cond_df, gene_df, sig_df = load_data()

# Chromosomes are strings, must sort alphabetically: 1, 10, 11, 12... 
chrom_order = [str(i) for i in range(1, 23)] + ["X", "Y", "MT", "Un"]
chrom_df["Chromosome"] = pd.Categorical(
    chrom_df["Chromosome"], categories=chrom_order, ordered=True
)
chrom_df = chrom_df.sort_values("Chromosome")
chrom_df = chrom_df[chrom_df["Chromosome"] != "Un"]

# -----------------------------
# TITLE
# -----------------------------
st.title("🧬 Genomic Variants Analytics Dashboard")
st.markdown("Exploring pathogenic variants across chromosomes, genes, conditions, and clinical significance.")

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

top_n_conditions = st.sidebar.slider("Top Conditions", 5, 50, 15)
top_n_genes = st.sidebar.slider("Top Genes", 5, 30, 10)

gene_search = st.sidebar.text_input("Search Gene", "")
if gene_search:
    gene_df = gene_df[gene_df["GeneSymbol"].str.contains(gene_search, case=False)]

# -----------------------------
# KPIs
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Chromosomes", chrom_df.shape[0])
col2.metric("Conditions", cond_df.shape[0])
col3.metric("Genes", gene_df.shape[0])
col4.metric("Total Variants", f"{sig_df['variant_count'].sum():,}")

st.divider()

# -----------------------------
# 1. CHROMOSOME ANALYSIS
# -----------------------------
st.header("📊 Chromosome-Level Analysis")

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(
        chrom_df,
        x="Chromosome",
        y="pathogenic_pct",
        title="Pathogenic % by Chromosome"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(
        chrom_df,
        x="Chromosome",
        y="pathogenic_count",
        title="Pathogenic Variant Count"
    )
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 2. DISEASE CONDITIONS
# -----------------------------
st.header("🧬 Disease Conditions")

top_conditions = cond_df.sort_values(
    "pathogenic_variant_count",
    ascending=False
).head(top_n_conditions)


fig3 = px.bar(
    top_conditions.sort_values("pathogenic_variant_count", ascending=True),  # ascending for plotly horizontal
    x="pathogenic_variant_count",
    y="condition",
    orientation="h",
    title=f"Top {top_n_conditions} Conditions by Pathogenic Variants"
)

st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# 3. GENE ANALYSIS
# -----------------------------
st.header("🧪 Gene-Level Pathogenicity")

top_genes = gene_df.sort_values(
    "pathogenic_variant_count",
    ascending=False
).head(top_n_genes)

fig4 = px.bar(
    top_genes.sort_values("pathogenic_variant_count", ascending=True),  # ascending for plotly horizontal,
    x="pathogenic_variant_count",
    y="GeneSymbol",
    orientation="h",
    title=f"Top {top_n_genes} Pathogenic Genes by Pathogenic Variants"
)

st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# 4. CLINICAL SIGNIFICANCE
# -----------------------------
st.header("📌 Clinical Significance Distribution")

# fig5 = px.pie(
#     sig_df,
#     names="ClinicalSignificance_clean",
#     values="variant_count",
#     title="Variant Distribution by Clinical Significance"
# )

fig5 = px.bar(
    sig_df.sort_values("variant_count", ascending=True),
    x="variant_count",
    y="ClinicalSignificance_clean",
    orientation="h",
    title="Variant Distribution by Clinical Significance"
)

st.plotly_chart(fig5, use_container_width=True)

# -----------------------------
# RAW DATA EXPANDERS
# -----------------------------
st.header("📄 Raw Data")

with st.expander("Chromosome Data"):
    st.dataframe(chrom_df)

with st.expander("Condition Data"):
    st.dataframe(cond_df)

with st.expander("Gene Data"):
    st.dataframe(gene_df)

with st.expander("Significance Data"):
    st.dataframe(sig_df)