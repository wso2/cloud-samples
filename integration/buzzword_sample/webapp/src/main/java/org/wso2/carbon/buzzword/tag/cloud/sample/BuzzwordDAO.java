/*
 * Copyright (c) 2016, WSO2 Inc. (http://www.wso2.org) All Rights Reserved.
 *
 * WSO2 Inc. licenses this file to you under the Apache License,
 * Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

package org.wso2.carbon.buzzword.tag.cloud.sample;

import org.apache.http.HttpException;
import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.NameValuePair;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.CookieStore;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.protocol.ClientContext;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.conn.ssl.TrustSelfSignedStrategy;
import org.apache.http.impl.client.BasicCookieStore;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.protocol.BasicHttpContext;
import org.apache.http.protocol.HttpContext;
import org.apache.http.ssl.SSLContextBuilder;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import sun.misc.BASE64Encoder;

import java.io.*;
import java.security.KeyManagementException;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

public class BuzzwordDAO {
    private static final Logger logger = Logger.getLogger(BuzzwordDAO.class.getName());

    public Buzzword[] getBuzzWordList() throws Exception {
        String apiEndpointUrl = System.getenv("API_ENDPOINT_URL");
        logger.info("API_ENDPOINT_URL : " + apiEndpointUrl);

        try {
            HttpClient client = getHttpClient();
            HttpGet apiMethod = new HttpGet(apiEndpointUrl);
            apiMethod.addHeader("Authorization", "Bearer " + getAccessToken());

            HttpResponse response = client.execute(apiMethod);
            if (HttpStatus.SC_OK == response.getStatusLine().getStatusCode()) {
                return formatDataToBuzzWords(getStringFromInputStream(response.getEntity().getContent()));
            } else {
                logger.log(Level.SEVERE, "Error occurred invoking the api endpoint. Http Status : " + response.getStatusLine().getStatusCode());
                throw new Exception("Failed to get Buzzwords from backend API:" + apiEndpointUrl);
            }

        } catch (HttpException e) {
            logger.log(Level.SEVERE, "Error occurred while invoking API endpoint.", e);
            throw new Exception("Failed to get Buzzwords from backend API:" + apiEndpointUrl);
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Error occurred while invoking API endpoint.", e);
            throw new Exception("Failed to get Buzzwords from backend API:" + apiEndpointUrl);
        }

    }

    private String getAccessToken()
            throws NoSuchAlgorithmException, KeyStoreException, KeyManagementException, UnsupportedEncodingException {
        String apiManagerUrl = System.getenv("API_MANAGER_URL");
        String apiEndpointUrl = System.getenv("API_ENDPOINT_URL");
        String apiConsumerKey = System.getenv("API_CONSUMER_KEY");
        String apiConsumerSecret = System.getenv("API_CONSUMER_SECRET");

        logger.info("API_MANAGER_URL: " + apiManagerUrl);
        logger.info("API_ENDPOINT_URL: " + apiEndpointUrl);
        logger.info("API_CONSUMER_KEY: " + apiConsumerKey);
        logger.info("API_CONSUMER_SECRET: " + apiConsumerSecret);

        String submitUrl = apiManagerUrl.trim() + "/token";
        String applicationToken = apiConsumerKey + ":" + apiConsumerSecret;

        BASE64Encoder base64Encoder = new BASE64Encoder();
        applicationToken = "Bearer " + base64Encoder.encode(applicationToken.getBytes()).trim();
        logger.info("applicationToken after encoding: " + applicationToken);
        HttpClient client = getHttpClient();

        HttpPost postMethod = new HttpPost(submitUrl);
        postMethod.addHeader("Authorization", applicationToken);
        postMethod.addHeader("Content-Type", "application/x-www-form-urlencoded");

        List<NameValuePair> params = new ArrayList<NameValuePair>(3);

        params.add(new BasicNameValuePair("grant_type", "client_credentials"));
        postMethod.setEntity(new UrlEncodedFormEntity(params, "UTF-8"));

        String accessToken = null;
        try {
            HttpResponse response= client.execute(postMethod);
            logger.info("Http status code after invoking token endpoint : " + response.getStatusLine().getStatusCode());

            if (HttpStatus.SC_OK == response.getStatusLine().getStatusCode()) {
                String accessTokenJson = getStringFromInputStream(response.getEntity().getContent());
                JSONParser parser = new JSONParser();
                Object obj = parser.parse(accessTokenJson);
                JSONObject jsonObject = (JSONObject) obj;
                accessToken = (String) jsonObject.get("access_token");
            } else {
                logger.log(Level.SEVERE,
                        "Error occurred invoking the token endpoint \n Http status : " + response.getStatusLine().getStatusCode() + " response: "
                                + getStringFromInputStream(response.getEntity().getContent()));
            }
        } catch (Exception ex) {
            logger.log(Level.SEVERE, "Error occurred while invoking token endpoint.", ex);
        }
        logger.info("Access Token - " + accessToken);
        return accessToken;
    }

    private Buzzword[] formatDataToBuzzWords(String values) {
        if (values != null) {
            values = values.replaceAll("\\{", "").replaceAll("}", "");
        } else {
            return new Buzzword[0];
        }

        List<Buzzword> list = new ArrayList<Buzzword>();
        String[] elements = values.split(",");
        for (String element : elements) {
            String[] wordRankSplits = element.split("=");
            String word = wordRankSplits[0].trim();
            String rank = wordRankSplits[1].trim();

            logger.info("word and rank: " + word + " " + rank);
            Buzzword buzzword = new Buzzword(word, Integer.parseInt(rank) * 5);
            list.add(buzzword);
        }

        return list.toArray(new Buzzword[list.size()]);
    }
    private HttpClient getHttpClient() throws KeyStoreException, NoSuchAlgorithmException, KeyManagementException {
        SSLContextBuilder builder = new SSLContextBuilder();
        builder.loadTrustMaterial(null, new TrustSelfSignedStrategy());
        SSLConnectionSocketFactory sslsf = new SSLConnectionSocketFactory(builder.build());

        // create a post request to addAPI.
        HttpClient httpclient = HttpClients.custom().setSSLSocketFactory(sslsf).build();
        return httpclient;
    }
    private static String getStringFromInputStream(InputStream is) {

        BufferedReader br = null;
        StringBuilder sb = new StringBuilder();

        String line;
        try {

            br = new BufferedReader(new InputStreamReader(is));
            while ((line = br.readLine()) != null) {
                sb.append(line);
            }

        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (br != null) {
                try {
                    br.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }

        return sb.toString();

    }
}
