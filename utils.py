def format_data(data):
    if type(data) != float:
        return str(data)
    elif data < 1:
        return "{:.1f}%".format(data * 100)
    else:
        return "{:.2f}".format(data)