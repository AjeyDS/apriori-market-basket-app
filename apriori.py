import streamlit as st
import pandas as pd


# ---------- Helper Functions ----------
def get_support(itemset, transactions):
    count = 0
    for t in transactions:
        if set(itemset).issubset(set(t)):
            count += 1
    return count / len(transactions)


def generate_candidates(prev_frequent, k):
    candidates = []
    for i in range(len(prev_frequent)):
        for j in range(i + 1, len(prev_frequent)):
            set1 = set(prev_frequent[i])
            set2 = set(prev_frequent[j])
            union = list(set1 | set2)
            union.sort()
            if len(union) == k and union not in candidates:
                candidates.append(union)
    return candidates


def apriori(transactions, min_support):
    all_items = sorted(set(item for t in transactions for item in t))
    current_frequent = [[item] for item in all_items if get_support([item], transactions) >= min_support]

    all_frequent = [(itemset, get_support(itemset, transactions)) for itemset in current_frequent]

    k = 2
    while current_frequent:
        candidates = generate_candidates(current_frequent, k)
        new_frequent = []
        for c in candidates:
            support = get_support(c, transactions)
            if support >= min_support:
                new_frequent.append(c)
                all_frequent.append((c, support))
        current_frequent = new_frequent
        k += 1

    return all_frequent


def generate_rules(frequent_itemsets, transactions, min_confidence):
    rules = []
    for itemset, _ in frequent_itemsets:
        if len(itemset) < 2:
            continue
        for i in range(1, len(itemset)):
            from itertools import combinations
            for antecedent in combinations(itemset, i):
                consequent = list(set(itemset) - set(antecedent))
                if not consequent:
                    continue

                support_all = get_support(itemset, transactions)
                support_ante = get_support(antecedent, transactions)
                support_cons = get_support(consequent, transactions)

                if support_ante > 0 and support_cons > 0:
                    confidence = support_all / support_ante
                    lift = confidence / support_cons
                    if confidence >= min_confidence:
                        rules.append({
                            'antecedents': antecedent,
                            'consequents': consequent,
                            'support': round(support_all, 4),
                            'confidence': round(confidence, 4),
                            'lift': round(lift, 4)
                        })

    return sorted(rules, key=lambda x: x['lift'], reverse=True)


# ---------- Streamlit UI ----------
st.title(" Market Basket Analysis with Apriori Algorithm")

with st.expander("📄 Click here to view required file format"):
    st.markdown("""
    Your CSV should contain **one transaction per row**, with each item separated by a comma.
    
    **Example:**
    ```
    milk,bread,butter
    bread,butter
    milk
    bread,butter,jam
    ```
    - No header row is required.
    - Blank cells are allowed and will be ignored.
    """)

    # Example data as a CSV download
    example_data = "milk,bread,butter\nbread,butter\nmilk\nbread,butter,jam"
    st.download_button(
        label="📥 Download Example CSV",
        data=example_data,
        file_name="example_transactions.csv",
        mime="text/csv"
    )

uploaded_file = st.file_uploader("Upload CSV file with transactional data", type=["csv"])

min_support = st.slider("Minimum Support", 0.01, 1.0, 0.1, step=0.01)
min_confidence = st.slider("Minimum Confidence", 0.01, 1.0, 0.3, step=0.01)

if uploaded_file is not None:
    transactions = [line.decode('utf-8').strip().split(',') for line in uploaded_file if line.strip()]

    transactions = [[item for item in row if item != ''] for row in transactions]

    frequent_itemsets = apriori(transactions, min_support)
    frequent_itemsets.sort(key=lambda x: x[1], reverse=True)

    rules = generate_rules(frequent_itemsets, transactions, min_confidence)

    st.subheader("✅ Frequent Itemsets")
    df_freq = pd.DataFrame(frequent_itemsets, columns=["Itemset", "Support"])
    st.dataframe(df_freq)

    st.subheader("📋 Association Rules")
    if rules:
        df_rules = pd.DataFrame(rules)
        st.dataframe(df_rules)
    else:
        st.warning("No rules found with the selected thresholds.")
else:
    st.info("Please upload a transactional CSV file to get started.")