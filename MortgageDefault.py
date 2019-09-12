# -*- coding: utf-8 -*-
"""
	Default Mortgage Predictions
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	An example web application for making predicions using a saved WLM model
	using Flask and the IBM WLM APIs.

	Created by Rich Tarro
	Updated by Sidney Phoon
	Sept 2019
"""

import os, urllib3, requests, json
from flask import Flask, request, session, g, redirect, url_for, abort, \
	 render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.update(dict(
	DEBUG=True,
	SECRET_KEY='development key',
))

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://admin:XZLNWWMRNZHWXOCK@bluemix-sandbox-dal-9-portal.8.dblayer.com:26360/MortgageDefault'
#postgres://admin:XZLNWWMRNZHWXOCK@bluemix-sandbox-dal-9-portal.8.dblayer.com:26360/mydb
#db = SQLAlchemy(app)



def predictDefault(ID, Income, AppliedOnline, Residence, YearCurrentAddress,
		YearsCurrentEmployer, NumberOfCards, CCDebt, Loans, LoanAmount, SalePrice, Location):
	
	apikey = 'TcEqt9DTURtLg5_ZR3-lLUA2gyehNu8TNtLaJNdrWPij'
	
	url     = "https://iam.bluemix.net/oidc/token"
	headers = { "Content-Type" : "application/x-www-form-urlencoded" }
	data    = "apikey=" + apikey + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"
	IBM_cloud_IAM_uid = "bx"
	IBM_cloud_IAM_pwd = "bx"
	response  = requests.post( url, headers=headers, data=data, auth=( IBM_cloud_IAM_uid, IBM_cloud_IAM_pwd ) )
	iam_token = response.json()["access_token"]
	
	ml_instance_id = '2d66a4d8-b28f-47c3-a667-8d7409861f75'
	
	header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + iam_token, 'ML-Instance-ID': ml_instance_id}


	scoring_endpoint = 'https://us-south.ml.cloud.ibm.com/v3/wml_instances/2d66a4d8-b28f-47c3-a667-8d7409861f75/deployments/26cb7bff-4da5-4639-bd44-dd7539048d0e/online'
	
	scoring_payload = {
    "fields": [
    "ID","Income","AppliedOnline","Residence","YearCurrentAddress","YearsCurrentEmployer","NumberOfCards","CCDebt","Loans","LoanAmount","SalePrice","Location"
    ],
    "values": [ [ID, Income, AppliedOnline, Residence, YearCurrentAddress, YearsCurrentEmployer, NumberOfCards, CCDebt, Loans, LoanAmount, SalePrice, Location] ]} 

	#sample_json = json.dumps(sample_data)
		
	response_scoring = requests.post(scoring_endpoint, json=scoring_payload, headers=header)
	
	result = response_scoring.text
	return response_scoring


@app.route('/',  methods=['GET', 'POST'])
def index():

	if request.method == 'POST':
		ID = 999
		#Income = 47422.0
		#AppliedOnline = 'YES'
		#Residence = 'Owner Occupier'
		#YearCurrentAddress = 11.0
		#YearsCurrentEmployer = 12.0
		#NumberOfCards = 2.0
		#CCDebt = 2010.0
		#Loans = 1.0
		#LoanAmount = 12315.0
		#SalePrice = 330000
		#Location = 100


		Income = int(request.form['Income'])
		AppliedOnline = request.form['AppliedOnline']
		Residence = request.form['Residence']
		YearCurrentAddress = int(request.form['YearCurrentAddress'])
		YearsCurrentEmployer = int(request.form['YearsCurrentEmployer'])
		NumberOfCards = int(request.form['NumberOfCards'])
		CCDebt = int(request.form['CCDebt'])
		Loans = int(request.form['Loans'])
		LoanAmount = int(request.form['LoanAmount'])
		SalePrice = int(request.form['SalePrice'])
		Location = int(request.form['Location'])

		session['Income'] = Income
		session['AppliedOnline'] = AppliedOnline
		session['Residence'] = Residence
		session['YearCurrentAddress'] = YearCurrentAddress
		session['YearsCurrentEmployer'] = YearsCurrentEmployer
		session['NumberOfCards'] = NumberOfCards
		session['CCDebt'] = CCDebt
		session['Loans'] = Loans
		session['LoanAmount'] = LoanAmount
		session['SalePrice'] = SalePrice
		session['Location'] = Location


		response_scoring = predictDefault(ID, Income, AppliedOnline, Residence, YearCurrentAddress,
		   YearsCurrentEmployer, NumberOfCards, CCDebt, Loans, LoanAmount, SalePrice, Location)

		print(response_scoring.text)
		
		prediction = response_scoring.json()["values"][0][19]
		probability= response_scoring.json()["values"][0][18][0]

		session['prediction'] = prediction
		session['probability'] = probability

		flash('Successful Prediction')
		return render_template('scoreSQL.html', response_scoring=response_scoring, request=request)


	else:
		return render_template('input.html')



#if __name__ == '__main__':
#   app.run()
port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
