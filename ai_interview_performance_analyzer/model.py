import numpy as np
from sklearn.ensemble import RandomForestRegressor


class CommunicationScorer:
    def __init__(self):
        self.model = self._train_model()

    def _train_model(self):
        random_state = 42
        rng = np.random.RandomState(random_state)
        X = []
        y = []

        for _ in range(1800):
            speech_confidence = rng.rand()
            filler_ratio = rng.rand()
            speaking_speed = rng.rand()
            facial_expression = rng.rand()
            eye_contact = rng.rand()
            sentiment = rng.rand()

            score = (
                0.25 * speech_confidence
                + 0.2 * (1.0 - filler_ratio)
                + 0.2 * speaking_speed
                + 0.15 * facial_expression
                + 0.1 * eye_contact
                + 0.1 * sentiment
            )
            score = np.clip(score + rng.normal(scale=0.05), 0.0, 1.0)
            X.append(
                [
                    speech_confidence,
                    filler_ratio,
                    speaking_speed,
                    facial_expression,
                    eye_contact,
                    sentiment,
                ]
            )
            y.append(score)

        model = RandomForestRegressor(n_estimators=60, random_state=random_state)
        model.fit(np.array(X), np.array(y))
        return model

    def predict(self, features: dict) -> float:
        feature_vector = np.array(
            [
                features["speech_confidence"],
                features["filler_ratio"],
                features["speaking_speed"],
                features["facial_expression"],
                features["eye_contact"],
                features["sentiment"],
            ]
        ).reshape(1, -1)
        raw_score = self.model.predict(feature_vector)[0]
        return float(np.clip(raw_score, 0.0, 1.0))
