        HOW TO RUN THE SAMPLE
=======================================

1. Create the Database
-----------------------
    a. Login to app cloud
    b. Create Database BuzzWordSampleDB
		    BuzzWordSampleDB
    c. Copy the generated DB_NAME , DB_USER_NAME and DB_PASSWORD
    d. Login to the database
	        mysql -h <mysql_hostname> -u <username> -p<password>
    e. Run the script to populate tables
        USE DATABASE <DB_NAME>;
        CREATE TABLE Buzzwords (Word VARCHAR(255) NOT NULL, Popularity INT, PRIMARY KEY (Word));
        +------------+--------------+------+-----+---------+-------+
        | Field      | Type         | Null | Key | Default | Extra |
        +------------+--------------+------+-----+---------+-------+
        | Word       | varchar(255) | NO   | PRI | NULL    |       |
        | Popularity | int(11)      | YES  |     | NULL    |       |
        +------------+--------------+------+-----+---------+-------+


2. Create the MSS App
----------------------------
    a. Get the jar from below and upload to the app
        https://svn.wso2.org/repos/wso2/people/manisha/con_2016/mss/Buzzword-Service-1.0-SNAPSHOT.jar
    b. Create the environment variables as below for the app
		    DB_URL = jdbc:mysql://mysql.storage.wso2.comt:3306/<DB_NAME>
       		DB_USERNAME = 7&lAp907jY
       		DB_PASSWORD = &ytaQY1Hha
    c. Once the application is created, you may run the below commands to test the MSS App
        Note that you can obtain the DEPLOYMENT_URL from the application home page
		    To insert the buzzwords:                            curl --data "Java" <DEPLOYMENT_URL>/buzzword
		        ex: curl --data "Java"  http://services.cloud.wso2.com/samithtest/webapps/ms444-r444/buzzword
            To get buzzwords similar or equal to a given word:  curl -v <DEPLOYMENT_URL>/buzzword/Eclipse
    	    To get all the buzzwords:                           curl -v <DEPLOYMENT_URL>/buzzword/all
    	    To get the  most popular 10 buzzwords:              curl -v <DEPLOYMENT_URL>/buzzword/mostPopular


3. View the logs of the MSS App
-------------------------------------

4. Create an API
--------------------
    a. Login to API Publisher and Create an API fronting the base MSS endpoint.
		    Base EP : <DEPLOYMENT_URL>/buzzword
    b. Login to API Store and Subscribe to the above created API.
            i.   Consumer Key
            ii.  Consumer Secret
            iii. Access Token
            iv.  Two grant types:  client_credentials and password
    c. Invoke the subscribed API using Curl
		    curl -k -d -v  -H "Authorization: Basic WWFCRndJZ3hmRVBEemljQ2drQzh6bHJjeUhzYTpRdUoyZEV2VHdkTGUzcTBjaVh0RDNFQ3UwTzRh" <PRODUCTION_API_URL>/all


5. Create Java Webapp
----------------------------
    a. Login again to App Cloud
    b. Create a new Java Webapp. Specify the environment variables as below:
		        API_MANAGER_URL     = https://gateway.api.cloud.wso2.com  (NOTE: this is for the token endpoint)
            	API_ENDPOINT_URL    = <PRODUCTION_API_URL>/all
            	API_CONSUMER_KEY    = YaBFwIgxfEPDzicCgkC8zlrcyHsa
            	API_CONSUMER_SECRET = QuJ2dEvTwdLe3q0ciXtD3ECu0O4a
    c. Once the app is deployed, you will be able to access the tag cloud app using the URL
            <PRODUCTION_APP_URL>/BuzzWordWebApp-1.0.0-SNAPSHOT/

6. View the logs of Java Web Application
-----------------------------------------