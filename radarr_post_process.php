#!/usr/bin/env php
<?php
$envVars = $_SERVER;

$eventType=isset($envVars["radarr_eventtype"]) ? $envVars["radarr_eventtype"] : null;
$moviePath=isset($envVars["radarr_movie_path"]) ? $envVars["radarr_movie_path"] : null;
$movieFile=isset($envVars[""]) ? $envVars[""] : null;

if($eventType != "Download")
    die();

if($filePath != null)
{
    if(file_exists($filePath))
    {
        file_put_contents("", "", FILE_APPEND);
        exec('');
    }
}                 