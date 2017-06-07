<%
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
  %>

<%@page import="org.wso2.carbon.buzzword.tag.cloud.sample.Buzzword" %>
<%@page import="org.wso2.carbon.buzzword.tag.cloud.sample.BuzzwordDAO" %>
<%@page import="java.util.*" %>
<%@page import="java.util.logging.Logger" %>

<html>
<head>
    <title>App Cloud Demo</title>
    <!--[if lt IE 9]><script type="text/javascript" src="excanvas.js"></script><![endif]-->
    <script src="tagcanvas.min.js" type="text/javascript"></script>
    <script type="text/javascript">
        window.onload = function() {
            try {
                TagCanvas.Start('myCanvas','tags',{
                    textColour: 'white',
                    outlineColour: '#ff00ff',
                    reverse: true,
                    weight: true,
                    depth: 0.8,
                    maxSpeed: 0.05
                });
            } catch(e) {
                // something went wrong, hide the canvas container
                document.getElementById('myCanvasContainer').style.display = 'none';
            }
        };
    </script>
    <style>
        body{
            margin: 0px;
            background-color: rgb(77, 181, 236);
        }
        h1{
            -webkit-margin-before: 0;
            -webkit-margin-after: 0;
            padding:10px;
            background-color: #3D3333;
            border-bottom: 3px solid rgb(86, 83, 83);
            color:#fff;
        }

        #myCanvasContainer{
            background-size: 107%;
            min-height: 45em;
        }
    </style>
</head>
<body>
<% Logger logger = Logger.getLogger(this.getClass().getName());%>
<h1 style="text-align: center">Buzzword Cloud</h1>
<div id="myCanvasContainer"  style="background-image: url(AppCloudBanner.png); background-repeat: no-repeat;">
    <canvas width="1400" height="800" id="myCanvas">
        <p>Anything in here will be replaced on browsers that support the canvas element</p>
    </canvas>
</div>
<div id="tags">
    <ul>
        <%
            BuzzwordDAO dao = new BuzzwordDAO();
            Buzzword[] buzzwords = new Buzzword[0];
            try {
                buzzwords = dao.getBuzzWordList();
                if (buzzwords != null) {
                    for (Buzzword buzzword : buzzwords) { %>
                    <li>
                        <a style="font-size: <%=buzzword.getPopularity()%>" href="#"><%=buzzword.getWord()%>
                        </a>
                    </li>
                <% } // end of for loop
                } else {
                %>
                <li>
                    <a style="font-size: 14" href="#">No Buzzwords Found.</a>
                </li>
                <%
                        }
            } catch (Exception e) {
                %>
                <li>
                    <a style="font-size: 14" href="#">Error Occurred:<%=e.getMessage()%></a>
                </li>
                <%
            }
        %>
    </ul>
</div>
</body>
</html>
