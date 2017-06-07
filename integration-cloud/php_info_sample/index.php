<!--
  ~ Copyright (c) 2016, WSO2 Inc. (http://wso2.com) All Rights Reserved.
  ~
  ~ Licensed under the Apache License, Version 2.0 (the "License");
  ~ you may not use this file except in compliance with the License.
  ~ You may obtain a copy of the License at
  ~
  ~ http://www.apache.org/licenses/LICENSE-2.0
  ~
  ~ Unless required by applicable law or agreed to in writing, software
  ~ distributed under the License is distributed on an "AS IS" BASIS,
  ~ WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  ~ See the License for the specific language governing permissions and
  ~ limitations under the License.
  -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>PHP Samples - WSO2 App Cloud</title>

    <!-- Mobile Specific Meta -->
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">

    <link rel="stylesheet" href="https://netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">
    <link rel="stylesheet" href="css/style.css">
</head>

<body data-spy="scroll" data-target="#main-bar">
    <div class="jumbotron" id="topBar">
        <p class="text-center">WSO2 App Cloud PHP Sample</p>
    </div>
    <div class="jumbotron" id="myCanvasContainer">
        <div class="container text-center">
            <h1>Congratulations !!!</h1>
            <p>You have successfully deployed your sample PHP application in WSO2 App Cloud</p>
            <div class="row">
                <p> <?php echo 'Your PHP version is ' ?><strong><?php echo phpversion(); ?></strong></p>
            </div>
            <div>
                <p>
                    <a class="white-color-font" target="_blank" href="phpinfo.php">View PHP info</a>
                </p>
            </div>
        </div>
    </div>
</body>
</html>