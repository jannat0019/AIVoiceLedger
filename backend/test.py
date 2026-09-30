from schemas import ExpenseDraft

expense=ExpenseDraft(
    merchant="Kolachi",
    total=-1200,
    category="food",
    payment_method="card"
)

print(expense)