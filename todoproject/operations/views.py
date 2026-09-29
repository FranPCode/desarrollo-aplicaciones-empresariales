from django.shortcuts import render


def sum(request, a, b):
  result = a + b
  return render(request, 'result.html', {'result': result, "a": a, "b": b, "symbol": "+"})


def substract(request, a, b):
  result = a - b
  return render(request, 'result.html', {'result': result, "a": a, "b": b, "symbol": "-"})


def multiply(request, a, b):
  result = a * b
  return render(request, 'result.html', {'result': result, "a": a, "b": b, "symbol": "X"})