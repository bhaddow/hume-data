d = read_csv("data.csv", converters={'id': str, 'parent' : str})
merged = d.merge(d, on = ["id", "sent", "lang"])
m = merged[merged["user_x"] != merged["user_y"]]

