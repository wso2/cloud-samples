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

package org.wso2.carbon.mss.sample;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import java.sql.*;
import java.util.HashMap;
import java.util.Map;


/**
 * This class is the main class that handles the business logic of the
 * Micro Service. This does all the HTTP request processing and retrieve the
 * requested data from the database
 */

@Path("/buzzword")
public class BuzzWordManager {

    private static final Logger log = LoggerFactory.getLogger(BuzzWordManager.class);

    public static final String WORD = "Word";
    public static final String POPULARITY = "Popularity";

    /**
     * Add a new buzzword.
     *
     * @param word the new buzzword.
     */
    @POST
    @Path("/{word}")
    public void addBuzzWords(@PathParam("word") String word) throws SQLException {
        Connection conn=null;
        PreparedStatement preparedStatement=null;
        try{
            conn = DBUtil.getDBConnection();
            String sql = "INSERT INTO Buzzwords (" + POPULARITY + " , " + WORD + ") VALUES (1,?) ON DUPLICATE KEY UPDATE "+POPULARITY+" = "+POPULARITY+" + 1";

            preparedStatement = conn.prepareStatement(sql);
            preparedStatement.setString(1, word);
            preparedStatement.executeUpdate();
            log.info("Popularity of buzzword:"+word +" is successfully updated.");
        }catch (Exception e){
            log.error("Failed to add buzzword:" + word, e);
        }finally {
            DBUtil.closePreparedStatement(preparedStatement);
            DBUtil.closeConnection(conn);
        }
    }

    /**
     * Retrieve all buzzwords with their popularity ranking.
     * curl -v http://localhost:8080/buzzword/Eclipse
     *
     * @returnall buzzwords which match with the given regex string,
     * with their popularity ranking will be sent to the client as Json/xml
     * according to the Accept header of the request.
     */
    @GET
    @Path("/{regex}")
    public Map getBuzzWords(@PathParam("regex") String regex) throws SQLException {
        Map buzzWordList = new HashMap();
        Connection conn = null;
        PreparedStatement preparedStatement = null;
        ResultSet resultSet = null;
        try {
            conn = DBUtil.getDBConnection();
            String sql = "select * from Buzzwords where " + WORD + " like ?";
            preparedStatement = conn.prepareStatement(sql);
            preparedStatement.setString(1, "%" + regex + "%");

            resultSet = preparedStatement.executeQuery();

            while (resultSet.next()) {
                String word = resultSet.getString(WORD);
                String ranking = resultSet.getString(POPULARITY);
                buzzWordList.put(word, ranking);
            }
            log.info("Popularity of buzzword:"+regex+" is requested.");
        }catch (Exception e){
            log.error("Failed to get buzzwords with regex:" + regex, e);
        }finally {
            DBUtil.closeResultSet(resultSet);
            DBUtil.closePreparedStatement(preparedStatement);
            DBUtil.closeConnection(conn);
        }

        return buzzWordList;
    }

    /**
     * Retrieve all buzzwords with their popularity ranking.
     * curl -v http://localhost:8080/buzzword/all
     *
     * @returnall buzzwords with their popularity ranking will be sent to the client as Json/xml
     * according to the Accept header of the request.
     */
    @GET
    @Path("/all")
    public Map getAllBuzzWords() throws SQLException {
        Map buzzWordList = new HashMap();
        Connection conn = null;
        PreparedStatement preparedStatement = null;
        ResultSet resultSet = null;
        try {
            conn = DBUtil.getDBConnection();

            String sql = "select * from Buzzwords";
            preparedStatement = conn.prepareStatement(sql);

            resultSet = preparedStatement.executeQuery();

            while (resultSet.next()) {
                String word = resultSet.getString(WORD);
                String ranking = resultSet.getString(POPULARITY);
                buzzWordList.put(word, ranking);
            }
            log.info("Popularity of all buzzwords is requested.");
        } catch (Exception e) {
            log.error("Failed to get all buzzwords.", e);
        } finally {
            DBUtil.closeResultSet(resultSet);
            DBUtil.closePreparedStatement(preparedStatement);
            DBUtil.closeConnection(conn);
        }

        return buzzWordList;
    }


    /**
     * Retrieve all buzzwords with their popularity ranking.
     * curl -v http://localhost:8080/buzzword/mostPopular
     *
     * @returnall buzzwords with their popularity ranking will be sent to the client as Json/xml
     * according to the Accept header of the request.
     */
    @GET
    @Path("/mostPopular")
    public Map getMostPopularBuzzWords() throws SQLException {
        Map buzzWordList = new HashMap();
        Connection conn = null;
        PreparedStatement preparedStatement = null;
        ResultSet resultSet = null;
        try {
            conn = DBUtil.getDBConnection();
            int mostPopularCount = 10;

            String sql = "select * from Buzzwords order by " + POPULARITY + " desc limit ?";

            preparedStatement = conn.prepareStatement(sql);
            preparedStatement.setInt(1, mostPopularCount);

            resultSet = preparedStatement.executeQuery();

            while (resultSet.next()) {
                String word = resultSet.getString(WORD);
                String ranking = resultSet.getString(POPULARITY);
                buzzWordList.put(word, ranking);
            }
            log.info("Popularity of most popular buzzwords is requested.");
        } catch (Exception e) {
            log.error("Failed to get most popular buzzwords.", e);
        } finally {
            DBUtil.closeResultSet(resultSet);
            DBUtil.closePreparedStatement(preparedStatement);
            DBUtil.closeConnection(conn);
        }
        return buzzWordList;
    }
}
