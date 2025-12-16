def cause_error():
    # This will raise a TypeError
    x = "hello"
    y = 5
    print(x + y)

if __name__ == "__main__":
    print("Running error scenario...")
    cause_error()
