# from selenium import webdriver
# from selenium.webdriver.common.by import By

# # create a new Chrome browser instance
# browser = webdriver.Chrome()

# # navigate to the website that contains the link you want to find
# browser.get("https://www.inventwithpython.com/")

# # find the anchor element by its partial link text
# link_element = browser.find_element(By.PARTIAL_LINK_TEXT, "Read Online")

# # click the link
# link_element.click()

# # close the browser window
# browser.quit()

from datetime import datetime, timedelta
from flask import Flask, make_response, request, jsonify
import requests
import json
from flask_cors import CORS
from logzero import logger
import time
import schedule
import sqlite3
import jwt

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'yash shetty'


def get_credentials(username, password):
    return True

@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    print(auth)
    username, password = auth.get('username'), auth.get('password')
    res = get_credentials(username, password)
    seconds = 300
    if res:
        token = jwt.encode({
            'user': username,
            'exp': datetime.utcnow() + timedelta(seconds=seconds)
        }, app.config['SECRET_KEY'])
        return make_response(jsonify({'token': token, 'expiration_in_seconds': seconds}), 200)
    else:
        return {'status': 'auth failed'}, 400


@app.route('/manage_cluster', methods=['POST'])
def manage_cluster(payload):
    logger.info('Inside manage_cluster')
    api_url = 'http://xyz.com/namespace/manage_cluster'
    headers = {'Content-Type': 'application/json',
               'accept': 'application/json'}
    logger.info('Sending request')
    response = requests.post(
        api_url, data=json.dumps(payload), headers=headers)
    logger.info(response)


# def monitor_cluster():
#     logger.info('Monitoring cluster status...')

#     # Retrieve the list of clusters to monitor (you can modify this based on your implementation)
#     clusters = ['cluster1', 'cluster2', 'cluster3']

#     for cluster in clusters:
#         # Make an API request to get the status of each cluster
#         api_url = f'http://xyz.com/namespace/get_cluster_status'
#         headers = {'Content-Type': 'application/json', 'accept': 'application/json'}
#         payload = {'cluster_name': cluster}

#         response = requests.post(api_url, data=json.dumps(payload), headers=headers)

#         # Process the response and update the status accordingly (you can modify this based on your implementation)
#         if response.status_code == 200:
#             status = response.json().get('status')
#             logger.info(f'Cluster {cluster} status: {status}')
#         else:
#             logger.error(f'Failed to retrieve status for cluster {cluster}')

#     logger.info('Cluster monitoring complete.')

# # Schedule the monitoring function to run every 30 seconds
# schedule.every(30).seconds.do(monitor_cluster)

# # Start the scheduler
# while True:
#     schedule.run_pending()
#     time.sleep(1)


@app.route('/clusters', methods=['POST'])
def create_cluster():
    # Parse the request JSON data
    data = request.get_json()
    cluster_name = data['cluster_name']
    domain_name = data['domain_name']
    role_arn = data['role_arn']
    status = data['status']

    # Insert the cluster data into the database
    with sqlite3.connect('clusters.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clusters (cluster_name, domain_name, role_arn, status) VALUES (?, ?, ?, ?)",
            (cluster_name, domain_name, role_arn, status)
        )
        conn.commit()

    return jsonify({'message': 'Cluster created successfully'})


@app.route('/clusters', methods=['GET'])
def get_clusters():
    # Fetch all clusters from the database
    with sqlite3.connect('clusters.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clusters")
        clusters = cursor.fetchall()

    # Prepare the response
    cluster_list = []
    for cluster in clusters:
        cluster_dict = {
            'id': cluster[0],
            'cluster_name': cluster[1],
            'domain_name': cluster[2],
            'role_arn': cluster[3],
            'status': cluster[4]
        }
        cluster_list.append(cluster_dict)

    return jsonify(cluster_list)


@app.route('/api/cluster', methods=['POST'])
def add_cluster():
    data = request.json
    
    cluster_name = data['clusterName']
    domain_name = data['domainName']
    role_arn = data['roleARN']
    status = data['status']
    
    # Insert the cluster into the database
    conn = sqlite3.connect('clusters.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clusters (cluster_name, domain_name, role_arn, status) VALUES (?, ?, ?, ?)",
                   (cluster_name, domain_name, role_arn, status))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Cluster added successfully'}), 201


# def get_cluster(cluster_id):
#     try:
#         conn = sqlite3.connect('clusters.db')
#         cursor = conn.cursor()
#         query = "SELECT * FROM cluster WHERE id = ?"
#         cursor.execute(query, (cluster_id + 1,))
#         row = cursor.fetchone()

#         if row is None:
#             return jsonify({'message': 'Cluster not found'}), 404

#         cluster = {
#             'id': row[0],
#             'cluster_name': row[1],
#             'domain_name': row[2],
#             'role_arn': row[3],
#             'status': row[4]
#         }

#         print(cluster)

#         return jsonify(cluster), 200

#     except sqlite3.Error as e:
#         return jsonify({'message': 'Error retrieving cluster details'}), 500

#     finally:
#         cursor.close()
#         conn.close()


@app.route('/api/clusters/<int:cluster_id>', methods=['GET'])
def get_cluster_by_id(cluster_id):
    print(cluster_id)
    try:
        conn = sqlite3.connect('clusters.db')
        cursor = conn.cursor()
        query = "SELECT * FROM clusters WHERE id = ?"
        cursor.execute(query, (cluster_id,))
        row = cursor.fetchone()

        if row is None:
            return jsonify({'message': 'Cluster not found'}), 404

        cluster = {
            'id': row[0],
            'cluster_name': row[1],
            'domain_name': row[2],
            'role_arn': row[3],
            'status': row[4]
        }

        logger.info(cluster)

        return jsonify(cluster), 200

    except sqlite3.Error as e:
        print("Error")
        return jsonify({'message': 'Error retrieving cluster details'}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/api/clusters/<int:cluster_id>', methods=['PUT'])
def update_cluster(cluster_id):
    try:
        # Get the updated cluster data from the request body
        updated_cluster = request.json

        conn = sqlite3.connect('clusters.db')
        cursor = conn.cursor()

        # Update the cluster in the database
        query = "UPDATE clusters SET cluster_name=?, domain_name=?, role_arn=?, status=? WHERE id=?"
        cursor.execute(query, (updated_cluster['cluster_name'], updated_cluster['domain_name'], 
                               updated_cluster['role_arn'], updated_cluster['status'], cluster_id))
        conn.commit()

        return jsonify({'message': 'Cluster updated successfully'}), 200

    except sqlite3.Error as e:
        print("Error")
        return jsonify({'message': 'Error updating cluster'}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/api/clusters/<int:cluster_id>', methods=['DELETE'])
def delete_cluster(cluster_id):
    try:
        conn = sqlite3.connect('clusters.db')
        cursor = conn.cursor()

        # Delete the cluster from the database
        query = "DELETE FROM clusters WHERE id = ?"
        cursor.execute(query, (cluster_id,))
        conn.commit()

        return jsonify({'message': 'Cluster deleted successfully'}), 200

    except sqlite3.Error as e:
        print("Error")
        return jsonify({'message': 'Error deleting cluster'}), 500

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
  app.run(debug=True)