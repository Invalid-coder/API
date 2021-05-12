from flask import Flask, request, jsonify, url_for
import pandas as pd
import time


weekly_diff = 604800
bi_weekly_diff = weekly_diff * 2
monthly_diff = weekly_diff * 4

app = Flask(__name__)
data = pd.read_csv("data.csv")


def group_by(df, dt):
    startDate = df.timestamp.min()
    res = {}
    arr = []
    i = 1
    for index, row in df.iterrows():
        if row['timestamp'] <= startDate + dt:
            arr.append(dict(row))
        else:
            res['week_{}'.format(i)] = arr
            arr = [dict(row)]
            i += 1
    if arr:
        res['week_{}'.format(i)] = arr
    return res


@app.route('/api/info', methods=['GET'])
def get_info():
    res = {attr:list(set(data[attr])) for attr in data if not attr in ['id', 'timestamp']}
    res['attributes'] = list(data.columns)
    return jsonify(res)


@app.route('/api/timeline', methods=['GET'])
def get_timeline():
    startDate = request.args.get('startDate', None)
    endDate = request.args.get('endDate', None)
    type = request.args.get('Type', None)
    grouping = request.args.get('Grouping', None)
    asin = request.args.get('asin', None)
    brand = request.args.get('brand', None)
    source = request.args.get('source', None)
    stars = request.args.get('stars', None)
    if startDate:
        startDate = time.mktime(time.strptime(startDate, "%Y-%m-%d"))
    if endDate:
        endDate = time.mktime(time.strptime(endDate, "%Y-%m-%d"))
    subset = data[(startDate <= data.timestamp) & (data.timestamp <= endDate)]
    if asin:
        subset = subset[subset.asin == asin]
    if brand:
        subset = subset[subset.brand == brand]
    if source:
        subset = subset[subset.source == source]
    if stars:
        subset = subset[subset.stars == int(stars)]
    subset = subset.sort_values(['timestamp'], ascending=[True])
    res = []
    if grouping == 'weekly':
        res = group_by(subset, weekly_diff)
    elif grouping == 'bi - weekly':
        res = group_by(subset, bi_weekly_diff)
    elif grouping == 'monthly':
        res = group_by(subset, monthly_diff)
    return jsonify({'timeline' : res})


if __name__ == '__main__':
    app.run(debug=True)
