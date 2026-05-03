wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"

request = function()
  local body = [[
  {
    "age": 63.0,
    "sex": 1.0,
    "cp": 3.0,
    "trestbps": 145.0,
    "chol": 233.0,
    "fbs": 1.0,
    "restecg": 0.0,
    "thalach": 150.0,
    "exang": 0.0,
    "oldpeak": 2.3,
    "slope": 0.0,
    "ca": 0.0,
    "thal": 1.0
  }
  ]]
  return wrk.format("POST", "/predict", nil, body)
end
