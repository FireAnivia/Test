# backend/ai_model.py
import numpy as np
from sklearn.linear_model import LinearRegression

class Predictor:
    def __init__(self):
        self.model = LinearRegression()

    def predict_next(self, history_data):
        """
        Dự đoán giá trị tiếp theo.
        history_data: List các dict [{'value': '25', ...}]
        """
        # Cần ít nhất 3 điểm dữ liệu để dự đoán
        if not history_data or len(history_data) < 3:
            return None

        try:
            # 1. Tiền xử lý dữ liệu
            # Đảo ngược list vì Adafruit trả về Mới nhất -> Cũ nhất
            values = [float(item.value) for item in history_data][::-1]
            y = np.array(values)
            
            # X là trục thời gian (0, 1, 2, ...)
            X = np.array(range(len(y))).reshape(-1, 1)

            # 2. Huấn luyện model
            self.model.fit(X, y)

            # 3. Dự đoán bước tiếp theo (index = len(y))
            next_index = np.array([[len(y)]])
            prediction = self.model.predict(next_index)
            
            return round(prediction[0], 2)
            
        except Exception as e:
            print(f"Lỗi dự đoán AI: {e}")
            return None