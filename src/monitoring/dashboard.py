"""Streamlit-based real-time fraud monitoring dashboard for Techcombank."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.logger import get_logger

logger = get_logger(__name__)


class FraudDashboard:
    """Interactive dashboard for transaction monitoring and fraud analysis."""

    @staticmethod
    def run(transactions_path: str, alerts_path: str) -> None:
        """Launch the Streamlit dashboard application."""
        st.set_page_config(
            page_title="Techcombank Fraud Detection Dashboard",
            page_icon="🏦",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        st.title("🏦 Techcombank Fraud Detection Pipeline")
        st.markdown("Real-time transaction monitoring and fraud intelligence platform")

        try:
            transactions = pd.read_csv(transactions_path)
            alerts = pd.read_csv(alerts_path)
        except FileNotFoundError:
            st.warning("No data found. Run the pipeline first to generate data.")
            return

        transactions["timestamp"] = pd.to_datetime(transactions["timestamp"])
        alerts["timestamp"] = pd.to_datetime(alerts["timestamp"])

        # Sidebar metrics
        st.sidebar.header("📊 Pipeline Metrics")
        st.sidebar.metric("Total Transactions", f"{len(transactions):,}")
        st.sidebar.metric("Fraud Alerts", f"{len(alerts):,}")
        st.sidebar.metric(
            "Fraud Rate",
            f"{(len(alerts) / len(transactions) * 100):.2f}%"
            if len(transactions) > 0
            else "0%",
        )
        st.sidebar.metric(
            "Total Volume (USD)",
            f"${transactions['amount_usd'].sum():,.2f}",
        )

        # Main content columns
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Transaction Volume Over Time")
            daily_volume = (
                transactions.groupby(transactions["timestamp"].dt.date)
                .agg(volume=("amount_usd", "sum"), count=("transaction_id", "count"))
                .reset_index()
            )
            fig = px.line(
                daily_volume,
                x="timestamp",
                y="volume",
                title="Daily Transaction Volume (USD)",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🚨 Fraud Alerts by Type")
            if not alerts.empty and "rule_type" in alerts.columns:
                alert_counts = alerts["rule_type"].value_counts()
                fig = px.pie(
                    values=alert_counts.values,
                    names=alert_counts.index,
                    title="Alert Distribution",
                )
                st.plotly_chart(fig, use_container_width=True)

        # Transaction type distribution
        st.subheader("🔄 Transaction Type Distribution")
        tx_type_counts = transactions["transaction_type"].value_counts()
        fig = px.bar(
            x=tx_type_counts.index,
            y=tx_type_counts.values,
            title="Transactions by Type",
            labels={"x": "Transaction Type", "y": "Count"},
        )
        st.plotly_chart(fig, use_container_width=True)

        # Recent alerts table
        st.subheader("⚠️ Recent Fraud Alerts")
        if not alerts.empty:
            display_cols = [
                "transaction_id",
                "account_id",
                "amount",
                "rule_name",
                "description",
            ]
            display_cols = [c for c in display_cols if c in alerts.columns]
            st.dataframe(
                alerts.sort_values("timestamp", ascending=False)
                .head(50)[display_cols],
                use_container_width=True,
            )

        # Data quality metrics
        st.subheader("✅ Data Quality Metrics")
        quality_col1, quality_col2, quality_col3 = st.columns(3)
        with quality_col1:
            st.metric("Null Values", transactions.isnull().sum().sum())
        with quality_col2:
            st.metric("Unique Accounts", transactions["account_id"].nunique())
        with quality_col3:
            st.metric("Date Range", f"{transactions['timestamp'].min().date()} - {transactions['timestamp'].max().date()}")

        logger.info("dashboard_rendered", transactions=len(transactions), alerts=len(alerts))


if __name__ == "__main__":
    FraudDashboard.run("data/processed_transactions.csv", "data/fraud_alerts.csv")