st.subheader("Industry Distribution")

industry_count = data["industry"].value_counts().reset_index()
industry_count.columns = ["industry","count"]

fig = px.pie(
    industry_count,
    values="count",
    names="industry",
    title="",
)

fig.update_layout(
    legend=dict(
        orientation="v",
        y=0.5,
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)
