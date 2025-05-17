import pandas as pd
from predictor import predict

test_data = pd.DataFrame([
    {"Отбор 1": "Лудогорец", "Отбор 2": "ЦСКА", "Лига": "Първа лига"},
    {"Отбор 1": "Арсенал", "Отбор 2": "Ман Сити", "Лига": "Висша лига"},
])

predictions = predict(test_data)

print("Вероятности за value bet:", predictions)
